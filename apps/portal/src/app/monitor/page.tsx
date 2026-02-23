"use client";
import React, { useEffect, useState } from "react";
import { Activity, Target, Landmark, Home, Github, Mic, Box, ArrowRight } from "lucide-react";

type MonitorData = {
    regional_outbound_24h: number;
    bid_bot_24h: number;
    intent_engine_24h: number;
    campaign_mode: string;
    last_heartbeat: string;
    seo_factory_status: string;
};

export default function OmniMonitorDashboard() {
    const [data, setData] = useState<MonitorData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTelemetry = async () => {
            try {
                const res = await fetch('/api/monitor');
                const json = await res.json();
                setData(json);
            } catch (err) {
                console.error("Failed to fetch Omni-Monitor telemetry:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchTelemetry();
        // Poll every 30 seconds for live updates
        const interval = setInterval(fetchTelemetry, 30000);
        return () => clearInterval(interval);
    }, []);

    if (loading || !data) {
        return (
            <div className="min-h-screen bg-[#0a0a0a] text-white flex flex-col items-center justify-center">
                <Activity className="w-12 h-12 text-violet-500 animate-spin mb-4" />
                <h2 className="text-xl font-bold text-zinc-300">Synchronizing Sovereign Telemetry...</h2>
            </div>
        );
    }

    return (
        <main className="min-h-screen bg-[#0a0a0a] text-white p-8 overflow-y-auto">
            <header className="mb-10 flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-white/10 pb-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <Box className="w-10 h-10 text-emerald-500" />
                        <h1 className="text-4xl font-black tracking-tight">
                            Sovereign <span className="text-emerald-500">Omni-Monitor</span>
                        </h1>
                    </div>
                    <p className="text-lg text-zinc-400 max-w-2xl">
                        God-View matrix tracking all 5 active B2B and B2C offensive revenue architectures.
                    </p>
                </div>

                <div className="flex gap-4">
                    <div className="bg-zinc-900/50 border border-white/10 rounded-xl px-4 py-3 text-sm">
                        <div className="text-zinc-500 font-bold mb-1 uppercase tracking-wider text-xs">System Heartbeat</div>
                        <div className="flex items-center gap-2 text-emerald-400 font-mono">
                            <Activity className="w-4 h-4" /> {data.last_heartbeat}
                        </div>
                    </div>
                    <div className="bg-zinc-900/50 border border-white/10 rounded-xl px-4 py-3 text-sm">
                        <div className="text-zinc-500 font-bold mb-1 uppercase tracking-wider text-xs">Global Master Switch</div>
                        <div className={`flex items-center gap-2 font-mono font-bold capitalize ${data.campaign_mode === 'active' || data.campaign_mode === 'working' ? 'text-emerald-400' : 'text-rose-500'}`}>
                            <div className={`w-2 h-2 rounded-full ${data.campaign_mode === 'active' || data.campaign_mode === 'working' ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
                            {data.campaign_mode}
                        </div>
                    </div>
                </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">

                {/* 1. Regional Offensive */}
                <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 relative overflow-hidden group hover:border-violet-500/50 transition-colors">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-violet-500/10 rounded-full blur-3xl -mr-10 -mt-10 transition-opacity opacity-50 group-hover:opacity-100" />

                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-xl bg-violet-500/20 flex items-center justify-center">
                            <Target className="w-5 h-5 text-violet-400" />
                        </div>
                        <h2 className="text-xl font-bold">1. Regional Offensive</h2>
                    </div>

                    <p className="text-sm text-zinc-400 mb-6 min-h-[40px]">
                        Continuous cold outreach via Video Teasers and PDF Audits pitching AEO optimization.
                    </p>

                    <div className="bg-black/40 rounded-xl p-4 border border-white/5">
                        <div className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-1">Outbound 24H</div>
                        <div className="text-3xl font-black text-white">{data.regional_outbound_24h} <span className="text-sm text-zinc-500 font-medium">touches sent</span></div>
                    </div>
                </div>

                {/* 2. Lakeland Bid-Bot */}
                <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 relative overflow-hidden group hover:border-blue-500/50 transition-colors">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl -mr-10 -mt-10 transition-opacity opacity-50 group-hover:opacity-100" />

                    <div className="flex justify-between items-start mb-4">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center">
                                <Landmark className="w-5 h-5 text-blue-400" />
                            </div>
                            <h2 className="text-xl font-bold">2. Bid-Bot (B2G)</h2>
                        </div>
                        <a href="/bids" className="text-blue-500 hover:text-blue-400 bg-blue-500/10 px-3 py-1.5 rounded-lg text-sm font-bold flex items-center gap-1 transition-colors">
                            View Console <ArrowRight className="w-4 h-4" />
                        </a>
                    </div>

                    <p className="text-sm text-zinc-400 mb-6 min-h-[40px]">
                        Nightly 4:00 AM Abacus Scraper parsing Gov. RFPs to match with local B2B Contractors.
                    </p>

                    <div className="bg-black/40 rounded-xl p-4 border border-white/5">
                        <div className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-1">Bids Extracted 24H</div>
                        <div className="text-3xl font-black text-white">{data.bid_bot_24h} <span className="text-sm text-zinc-500 font-medium">new state contracts</span></div>
                    </div>
                </div>

                {/* 3. Intent Engine */}
                <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 relative overflow-hidden group hover:border-rose-500/50 transition-colors">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-rose-500/10 rounded-full blur-3xl -mr-10 -mt-10 transition-opacity opacity-50 group-hover:opacity-100" />

                    <div className="flex justify-between items-start mb-4">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-rose-500/20 flex items-center justify-center">
                                <Home className="w-5 h-5 text-rose-400" />
                            </div>
                            <h2 className="text-xl font-bold">3. Intent Engine (B2C)</h2>
                        </div>
                        <a href="/intents" className="text-rose-500 hover:text-rose-400 bg-rose-500/10 px-3 py-1.5 rounded-lg text-sm font-bold flex items-center gap-1 transition-colors">
                            View Console <ArrowRight className="w-4 h-4" />
                        </a>
                    </div>

                    <p className="text-sm text-zinc-400 mb-6 min-h-[40px]">
                        Nightly 5:00 AM Abacus Scraper parsing physical Yard Sales to map Moving Intent to Realtors.
                    </p>

                    <div className="bg-black/40 rounded-xl p-4 border border-white/5">
                        <div className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-1">Intent Signals 24H</div>
                        <div className="text-3xl font-black text-white">{data.intent_engine_24h} <span className="text-sm text-zinc-500 font-medium">B2C events captured</span></div>
                    </div>
                </div>

                {/* 4. SEO Factory */}
                <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 relative overflow-hidden group hover:border-orange-500/50 transition-colors">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-orange-500/10 rounded-full blur-3xl -mr-10 -mt-10 transition-opacity opacity-50 group-hover:opacity-100" />

                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-xl bg-orange-500/20 flex items-center justify-center">
                            <Github className="w-5 h-5 text-orange-400" />
                        </div>
                        <h2 className="text-xl font-bold">4. SEO Factory</h2>
                    </div>

                    <p className="text-sm text-zinc-400 mb-6 min-h-[40px]">
                        Programmatic edge route writing LLM-powered location pages natively into the GitHub repository matrix.
                    </p>

                    <div className="bg-black/40 rounded-xl p-4 border border-white/5 flex items-center justify-between">
                        <div>
                            <div className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-1">Cron Status</div>
                            <div className="text-xl font-bold text-emerald-400">{data.seo_factory_status}</div>
                        </div>
                        <div className="text-right">
                            <a href="https://github.com/nearmiss1193-afk/empire-unified-backup/actions" target="_blank" rel="noopener noreferrer" className="text-xs text-orange-400 hover:underline">View Pipeline</a>
                        </div>
                    </div>
                </div>

                {/* 5. Voice / Social Auto-Poster */}
                <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 relative overflow-hidden group hover:border-fuchsia-500/50 transition-colors">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-fuchsia-500/10 rounded-full blur-3xl -mr-10 -mt-10 transition-opacity opacity-50 group-hover:opacity-100" />

                    <div className="flex justify-between items-start mb-4">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-fuchsia-500/20 flex items-center justify-center">
                                <Mic className="w-5 h-5 text-fuchsia-400" />
                            </div>
                            <h2 className="text-xl font-bold">5. Voice / Social</h2>
                        </div>
                        <a href="/socials" className="text-fuchsia-500 hover:text-fuchsia-400 bg-fuchsia-500/10 px-3 py-1.5 rounded-lg text-sm font-bold flex items-center gap-1 transition-colors">
                            Queue <ArrowRight className="w-4 h-4" />
                        </a>
                    </div>

                    <p className="text-sm text-zinc-400 mb-6 min-h-[40px]">
                        Ayrshare scheduling B2B tweets / Vapi inbound receptionist matrix catching prospect calls.
                    </p>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-black/40 rounded-xl p-4 border border-white/5">
                            <div className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-1">Vapi Status</div>
                            <div className="text-lg font-bold text-emerald-400">Listening</div>
                        </div>
                        <div className="bg-black/40 rounded-xl p-4 border border-white/5">
                            <div className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-1">Social Bot</div>
                            <div className="text-lg font-bold text-emerald-400">Armed</div>
                        </div>
                    </div>
                </div>

            </div>
        </main>
    );
}
