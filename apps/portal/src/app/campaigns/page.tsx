'use client';

import React, { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabaseClient';

export default function CampaignsPage() {
    const [campaigns, setCampaigns] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchCampaignTelemetry = async () => {
            setLoading(true);

            // Pull 30-day trailing telemetry
            const thirtyDaysAgo = new Date();
            thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

            const { data, error } = await supabase
                .from('outbound_touches')
                .select('template_name, channel, status, ts, direction')
                .gte('ts', thirtyDaysAgo.toISOString())
                .eq('direction', 'outbound');

            if (error) {
                console.error('Failed to pull campaign telemetry:', error);
                setLoading(false);
                return;
            }

            // We must independently query replies because they are direction = 'inbound'
            // Or we check records where 'replied' = true. In the architecture, we usually track 'status' = 'replied' or explicit true flags.
            // For this master A/B matrix, we will aggregate based on `template_name`.

            const aggregationMap: Map<string, any> = new Map();

            const touchLogs: any[] = data || [];
            touchLogs.forEach((touch: any) => {
                // Normalize null scripts into a "Manual Execution" bucket
                const templateId = touch.template_name || 'Manual Execution Override';
                const key = `${touch.channel}_${templateId}`;

                if (!aggregationMap.has(key)) {
                    aggregationMap.set(key, {
                        id: key,
                        template: templateId,
                        channel: touch.channel || 'UNK',
                        totalSent: 0,
                        delivered: 0,
                        opened: 0,
                        replied: 0,
                        bookings: 0,
                        lastFired: touch.ts
                    });
                }

                const entry = aggregationMap.get(key);

                // Timestamp updater
                if (new Date(touch.ts) > new Date(entry.lastFired)) {
                    entry.lastFired = touch.ts;
                }

                // Increment Sent
                entry.totalSent += 1;

                // Increment delivery/read bounds
                if (touch.status === 'delivered') entry.delivered += 1;
                if (touch.status === 'opened' || touch.status === 'read') {
                    entry.delivered += 1;
                    entry.opened += 1;
                }
                if (touch.status === 'replied') {
                    entry.delivered += 1;
                    entry.opened += 1;
                    entry.replied += 1;
                }
                if (touch.status === 'booking') {
                    entry.delivered += 1;
                    entry.opened += 1;
                    entry.replied += 1;
                    entry.bookings += 1;
                }
            });

            // Sort by highest sending volume
            const sortedCampaigns = Array.from(aggregationMap.values()).sort((a, b) => b.totalSent - a.totalSent);

            setCampaigns(sortedCampaigns);
            setLoading(false);
        };

        fetchCampaignTelemetry();
    }, []);

    return (
        <div className="min-h-screen bg-slate-950 p-8">

            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
                        <svg className="w-8 h-8 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" /></svg>
                        Active Campaign Triage
                    </h1>
                    <p className="text-slate-400 mt-2">Realtime A/B statistical variance monitoring and execution control.</p>
                </div>

                <div className="flex bg-slate-900 border border-slate-800 rounded-lg p-1">
                    <button className="px-4 py-1.5 bg-slate-800 text-slate-200 rounded shadow-sm text-sm font-medium">30 Days</button>
                    <button className="px-4 py-1.5 text-slate-400 hover:text-slate-200 rounded text-sm font-medium">14 Days</button>
                    <button className="px-4 py-1.5 text-slate-400 hover:text-slate-200 rounded text-sm font-medium">24 Hours</button>
                </div>
            </div>

            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden backdrop-blur-md">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase tracking-wider bg-slate-900/80">
                                <th className="p-4 font-semibold">Script / Template</th>
                                <th className="p-4 font-semibold justify-center">Network</th>
                                <th className="p-4 font-semibold text-right">Volume</th>
                                <th className="p-4 font-semibold text-right">Open Rate</th>
                                <th className="p-4 font-semibold text-right">Reply Rate</th>
                                <th className="p-4 font-semibold text-center">Status</th>
                                <th className="p-4 font-semibold text-center">Controls</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan={7} className="p-12 text-center">
                                        <div className="inline-flex items-center justify-center gap-3">
                                            <span className="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></span>
                                            <span className="text-slate-400 font-medium tracking-wide animate-pulse">Computing Matrix...</span>
                                        </div>
                                    </td>
                                </tr>
                            ) : campaigns.length === 0 ? (
                                <tr>
                                    <td colSpan={7} className="p-12 text-center text-slate-500">No outbound telemetry found in parameters.</td>
                                </tr>
                            ) : (
                                campaigns.map((camp, idx) => {
                                    const openRate = camp.totalSent > 0 ? ((camp.opened / camp.totalSent) * 100).toFixed(1) : '0.0';
                                    const replyRate = camp.totalSent > 0 ? ((camp.replied / camp.totalSent) * 100).toFixed(1) : '0.0';

                                    // Simple A/B flag heuristic
                                    const isWinning = parseFloat(replyRate) > 3.0;
                                    const isLosing = parseFloat(replyRate) < 1.0 && camp.totalSent > 50;

                                    return (
                                        <tr key={camp.id} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                                            <td className="p-4">
                                                <div className="font-medium text-slate-200 flex items-center gap-2">
                                                    {camp.template}
                                                    {isWinning && <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold tracking-widest uppercase">Winner</span>}
                                                    {isLosing && <span className="px-2 py-0.5 rounded text-[10px] bg-red-500/10 text-red-400 border border-red-500/20 font-bold tracking-widest uppercase">Suboptimal</span>}
                                                </div>
                                                <div className="text-xs text-slate-500 mt-1 font-mono">Last Fired: {new Date(camp.lastFired).toLocaleDateString()}</div>
                                            </td>

                                            <td className="p-4 text-center">
                                                <span className={`px-2.5 py-1 rounded text-xs font-semibold uppercase tracking-wider ${camp.channel === 'sms' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : camp.channel === 'email' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-purple-500/10 text-purple-400 border border-purple-500/20'}`}>
                                                    {camp.channel}
                                                </span>
                                            </td>

                                            <td className="p-4 text-right font-mono text-slate-300">
                                                {camp.totalSent.toLocaleString()}
                                            </td>

                                            <td className="p-4 text-right">
                                                <span className={`font-mono font-medium ${parseFloat(openRate) > 40 ? 'text-emerald-400' : 'text-slate-300'}`}>
                                                    {camp.channel === 'sms' ? 'N/A' : `${openRate}%`}
                                                </span>
                                            </td>

                                            <td className="p-4 text-right">
                                                <span className={`font-mono font-bold ${isWinning ? 'text-emerald-400' : isLosing ? 'text-red-400' : 'text-slate-200'}`}>
                                                    {replyRate}%
                                                </span>
                                            </td>

                                            <td className="p-4 text-center">
                                                <span className="flex justify-center items-center gap-2">
                                                    <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
                                                    <span className="text-xs text-slate-400">Live</span>
                                                </span>
                                            </td>

                                            <td className="p-4">
                                                <div className="flex justify-center gap-2">
                                                    <button className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-700 rounded transition-colors" title="Edit Template">
                                                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
                                                    </button>
                                                    <button className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors" title="Halt Campaign">
                                                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                                    </button>
                                                </div>
                                            </td>

                                        </tr>
                                    );
                                })
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
    );
}
