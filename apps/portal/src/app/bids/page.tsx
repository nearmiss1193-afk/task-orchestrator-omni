"use client";
import React, { useEffect, useState } from "react";
import { Hammer, Building2, Send, Clock, DollarSign, ArrowRight, Activity } from "lucide-react";

type BidMatch = {
    id: number;
    company_name: string;
    phone: string;
    rating: string;
    outreach_script: string;
};

type Bid = {
    id: number;
    title: string;
    closing_date: string | null;
    estimated_budget: string;
    required_certs: string;
    category: string;
    scope_summary: string;
    created_at: string;
    matches: BidMatch[];
};

export default function BidBotCommandCenter() {
    const [bids, setBids] = useState<Bid[]>([]);
    const [loading, setLoading] = useState(true);
    const [dispatching, setDispatching] = useState<number | null>(null); // match id tracking
    const [dispatchedIds, setDispatchedIds] = useState<Set<number>>(new Set());

    useEffect(() => {
        fetch('/api/bids')
            .then(res => res.json())
            .then(data => {
                if (Array.isArray(data)) {
                    setBids(data);
                }
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    const handleDispatch = async (match: BidMatch) => {
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
                <Activity className="w-12 h-12 text-blue-500 animate-spin mb-4" />
                <h2 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
                    Scanning OpenGov Portals...
                </h2>
                <p className="text-zinc-500">Executing RFP Matchmaker Algorithm</p>
            </div>
        );
    }

    return (
        <main className="min-h-screen bg-[#0a0a0a] text-white p-8 overflow-y-auto">
            <header className="mb-10">
                <div className="flex items-center gap-3 mb-2">
                    <Building2 className="w-10 h-10 text-emerald-500" />
                    <h1 className="text-4xl font-black tracking-tight">
                        Lakeland <span className="text-emerald-500">Bid-Bot</span>
                    </h1>
                </div>
                <p className="text-lg text-zinc-400 max-w-2xl">
                    Autonomous government contracting matchmaker. Extracts high-value RFPs and calculates optimal contractor targets in real-time.
                </p>
            </header>

            {bids.length === 0 ? (
                <div className="text-center py-20 border border-white/10 rounded-xl bg-zinc-900/30">
                    <Hammer className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
                    <h3 className="text-2xl font-bold text-zinc-400">No Active Bids Found</h3>
                    <p className="text-zinc-600 mt-2">The Nightly Scraper Daemon will hunt for new RFPs at 4:00 AM.</p>
                </div>
            ) : (
                <div className="grid gap-8">
                    {bids.map(bid => (
                        <div key={bid.id} className="border border-white/10 rounded-2xl bg-[#111111] overflow-hidden flex flex-col lg:flex-row">
                            {/* Left Panel: RFP Data */}
                            <div className="p-8 lg:w-2/3 border-b lg:border-b-0 lg:border-r border-white/10 flex flex-col">
                                <div className="flex justify-between items-start mb-4">
                                    <div>
                                        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 text-sm font-medium mb-3">
                                            <Hammer className="w-4 h-4" /> {bid.category}
                                        </div>
                                        <h2 className="text-2xl font-bold leading-tight">{bid.title}</h2>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-2xl font-black text-emerald-400 flex items-center justify-end">
                                            {bid.estimated_budget !== 'Unknown' ? bid.estimated_budget : 'Bidding Open'}
                                        </div>
                                        {bid.closing_date && (
                                            <div className="text-sm text-zinc-500 flex items-center gap-1 justify-end mt-1">
                                                <Clock className="w-3 h-3" /> Closes {bid.closing_date}
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <p className="text-zinc-400 flex-grow mb-6 leading-relaxed">
                                    {bid.scope_summary}
                                </p>

                                {bid.required_certs && bid.required_certs !== 'Unknown' && (
                                    <div className="bg-amber-500/10 border border-amber-500/20 text-amber-500 px-4 py-3 rounded-lg text-sm">
                                        <strong>Required Certifications:</strong> {bid.required_certs}
                                    </div>
                                )}
                            </div>

                            {/* Right Panel: Matchmaker Targets */}
                            <div className="p-0 lg:w-1/3 bg-black/40">
                                <div className="p-4 border-b border-white/5 bg-gradient-to-r from-emerald-500/10 to-transparent">
                                    <h3 className="font-bold text-emerald-500 flex items-center gap-2">
                                        <ArrowRight className="w-4 h-4" /> CRM Matches ({bid.matches.length})
                                    </h3>
                                </div>
                                <div className="p-4 max-h-[400px] overflow-y-auto space-y-4">
                                    {bid.matches.length === 0 ? (
                                        <p className="text-zinc-600 text-sm">No exact niche matches found in contacts_master.</p>
                                    ) : (
                                        bid.matches.map(match => (
                                            <div key={match.id} className="bg-zinc-900 rounded-xl p-4 border border-zinc-800 hover:border-emerald-500/30 transition-colors">
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
                                                        : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-[0_0_15px_rgba(16,185,129,0.3)]'
                                                        }`}
                                                >
                                                    {dispatchedIds.has(match.id) ? (
                                                        'Dispatched'
                                                    ) : dispatching === match.id ? (
                                                        <Activity className="w-4 h-4 animate-spin" />
                                                    ) : (
                                                        <><Send className="w-4 h-4" /> SMS Pitch</>
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
