"use client";
import React, { useEffect, useState } from "react";
import { Box, Home, Send, CalendarDays, ArrowRight, Activity, MapPin } from "lucide-react";

type IntentMatch = {
    id: number;
    company_name: string;
    phone: string;
    rating: string;
    outreach_script: string;
};

type IntentSale = {
    id: number;
    title: string;
    event_date: string | null;
    address: string;
    sale_type: string;
    intent_classification: string;
    description_summary: string;
    created_at: string;
    matches: IntentMatch[];
};

export default function IntentEngineCommandCenter() {
    const [sales, setSales] = useState<IntentSale[]>([]);
    const [loading, setLoading] = useState(true);
    const [dispatching, setDispatching] = useState<number | null>(null);
    const [dispatchedIds, setDispatchedIds] = useState<Set<number>>(new Set());

    useEffect(() => {
        fetch('/api/intents')
            .then(res => res.json())
            .then(data => {
                if (Array.isArray(data)) {
                    setSales(data);
                }
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    const handleDispatch = async (match: IntentMatch) => {
        setDispatching(match.id);
        try {
            const res = await fetch('/api/manual-override', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contact_identifier: match.phone,
                    channel: 'sms',
                    body: match.outreach_script
                })
            });
            const data = await res.json();
            if (data.success) {
                setDispatchedIds(prev => new Set(prev).add(match.id));
            } else {
                alert(`Dispatch Failed: ${data.error}`);
            }
        } catch (e) {
            console.error(e);
            alert("Network error during dispatch.");
        }
        setDispatching(null);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-[#0a0a0a] text-white flex flex-col items-center justify-center">
                <Activity className="w-12 h-12 text-violet-500 animate-spin mb-4" />
                <h2 className="text-xl font-bold bg-gradient-to-r from-violet-400 to-fuchsia-500 bg-clip-text text-transparent">
                    Scanning EstateSales.net...
                </h2>
                <p className="text-zinc-500">Extracting High-Value Consumer Intents</p>
            </div>
        );
    }

    return (
        <main className="min-h-screen bg-[#0a0a0a] text-white p-8 overflow-y-auto">
            <header className="mb-10">
                <div className="flex items-center gap-3 mb-2">
                    <Box className="w-10 h-10 text-violet-500" />
                    <h1 className="text-4xl font-black tracking-tight">
                        Lakeland <span className="text-violet-500">Intent Engine</span>
                    </h1>
                </div>
                <p className="text-lg text-zinc-400 max-w-2xl">
                    Autonomous B2C-to-B2B monetization loop. Identifies &apos;Moving&apos; and &apos;Liquidation&apos; sales, mapping them to Realtors and Junk Removal agencies.
                </p>
            </header>

            {sales.length === 0 ? (
                <div className="text-center py-20 border border-white/10 rounded-xl bg-zinc-900/30">
                    <Home className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
                    <h3 className="text-2xl font-bold text-zinc-400">No Intent Events Detected</h3>
                    <p className="text-zinc-600 mt-2">The AI Scraper operates at 5:00 AM daily.</p>
                </div>
            ) : (
                <div className="grid gap-8">
                    {sales.map(sale => (
                        <div key={sale.id} className="border border-white/10 rounded-2xl bg-[#111111] overflow-hidden flex flex-col lg:flex-row">
                            {/* Left Panel: Sale Data */}
                            <div className="p-8 lg:w-2/3 border-b lg:border-b-0 lg:border-r border-white/10 flex flex-col">
                                <div className="flex justify-between items-start mb-4">
                                    <div>
                                        <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium mb-3 ${sale.intent_classification?.includes('Moving')
                                            ? 'bg-rose-500/10 text-rose-400'
                                            : sale.intent_classification?.includes('Estate')
                                                ? 'bg-violet-500/10 text-violet-400'
                                                : 'bg-zinc-500/10 text-zinc-400'
                                            }`}>
                                            <Activity className="w-4 h-4" /> {sale.intent_classification || 'Unknown Intent'}
                                        </div>
                                        <h2 className="text-2xl font-bold leading-tight flex items-center gap-2">
                                            {sale.title}
                                        </h2>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-sm font-bold text-white flex items-center justify-end gap-1.5 bg-white/10 px-3 py-1.5 rounded-md">
                                            <CalendarDays className="w-4 h-4 text-zinc-400" /> {sale.event_date || 'TBD'}
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-2 text-zinc-400 mb-6 text-sm font-mono bg-black/50 w-fit px-3 py-1.5 rounded border border-white/5">
                                    <MapPin className="w-4 h-4 text-violet-500" /> {sale.address || 'Address Obscured'}
                                </div>

                                <div className="text-zinc-300 flex-grow mb-6 leading-relaxed relative">
                                    <p className="bg-zinc-900/50 p-4 rounded-xl border border-white/5">
                                        <span className="font-bold text-zinc-500 uppercase text-xs block mb-2">AI Summary</span>
                                        {sale.description_summary}
                                    </p>
                                </div>
                            </div>

                            {/* Right Panel: Matchmaker Targets */}
                            <div className="p-0 lg:w-1/3 bg-black/40">
                                <div className="p-4 border-b border-white/5 bg-gradient-to-r from-violet-500/10 to-transparent">
                                    <h3 className="font-bold text-violet-400 flex items-center gap-2">
                                        <ArrowRight className="w-4 h-4" /> Agency Matches ({sale.matches?.length || 0})
                                    </h3>
                                </div>
                                <div className="p-4 max-h-[400px] overflow-y-auto space-y-4">
                                    {!sale.matches || sale.matches.length === 0 ? (
                                        <p className="text-zinc-600 text-sm">No relevant Realtor/Junk niches found for this intent.</p>
                                    ) : (
                                        sale.matches.map(match => (
                                            <div key={match.id} className="bg-zinc-900 rounded-xl p-4 border border-zinc-800 hover:border-violet-500/30 transition-colors">
                                                <div className="flex justify-between items-center mb-3">
                                                    <div className="font-bold">{match.company_name}</div>
                                                    <div className="text-xs bg-zinc-800 px-2 py-1 rounded text-zinc-400">
                                                        {match.rating || '?'} ⭐
                                                    </div>
                                                </div>
                                                <div className="text-sm text-zinc-400 bg-black/50 p-3 rounded-lg mb-4 italic border border-white/5">
                                                    &quot;{match.outreach_script}&quot;
                                                </div>
                                                <button
                                                    onClick={() => handleDispatch(match)}
                                                    disabled={dispatching === match.id || dispatchedIds.has(match.id)}
                                                    className={`w-full py-2.5 rounded-lg font-bold flex items-center justify-center gap-2 transition-all ${dispatchedIds.has(match.id)
                                                        ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed'
                                                        : 'bg-violet-600 hover:bg-violet-500 text-white shadow-[0_0_15px_rgba(139,92,246,0.3)]'
                                                        }`}
                                                >
                                                    {dispatchedIds.has(match.id) ? (
                                                        'Pitched via SMS'
                                                    ) : dispatching === match.id ? (
                                                        <Activity className="w-4 h-4 animate-spin" />
                                                    ) : (
                                                        <><Send className="w-4 h-4" /> SMS Realtor Pitch</>
                                                    )}
                                                </button>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </main>
    );
}
