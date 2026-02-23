'use client';

import React, { useEffect, useState, useMemo } from 'react';
import { supabase } from '@/lib/supabaseClient';
import {
    MessageSquare,
    Mail,
    Phone,
    Clock,
    CheckCircle2,
    AlertCircle,
    Search,
    UserCircle2,
    Building2,
    ShieldAlert,
    Send,
    Eye
} from 'lucide-react';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

// --- Types ---
interface TouchEvent {
    id: string;
    phone: string | null;
    email: string | null;
    channel: 'sms' | 'email' | 'call';
    status: string;
    body: string | null;
    company: string | null;
    payload: any;
    ts: string;
    variant_name: string | null;
}

interface LeadStatus {
    id: string; // Phone or Email as primary key
    company: string;
    last_contacted: string;
    status: 'replied' | 'negotiating' | 'booked' | 'won' | 'sent' | 'bounced' | string;
    unread: boolean;
    channels: string[];
    latest_message: string;
    campaign: string;
}

export default function InboxPage() {
    const [touches, setTouches] = useState<TouchEvent[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedContactId, setSelectedContactId] = useState<string | null>(null);
    const [replyText, setReplyText] = useState('');
    const [activeTab, setActiveTab] = useState<'unread' | 'negotiating' | 'booked' | 'all'>('unread');
    const [searchQuery, setSearchQuery] = useState('');
    const [directiveText, setDirectiveText] = useState(''); // State for Commander Directives
    const [isSavingDirective, setIsSavingDirective] = useState(false);

    // Fetch initial telemetry
    useEffect(() => {
        const fetchInitialLogs = async () => {
            setLoading(true);
            const { data, error } = await supabase
                .from('outbound_touches')
                .select('*')
                .order('ts', { ascending: false })
                .limit(500); // Fetch more for deeper threads

            if (error) {
                console.error('Error fetching inbox telemetry:', error);
            } else if (data) {
                setTouches(data as TouchEvent[]);
            }
            setLoading(false);
        };

        fetchInitialLogs();

        // Subscribe to realtime WebSockets
        const channel = supabase
            .channel('public:outbound_touches')
            .on(
                'postgres_changes',
                { event: 'INSERT', schema: 'public', table: 'outbound_touches' },
                (payload) => {
                    console.log('New Inbound/Outbound Message Received!', payload.new);
                    setTouches((prev) => [payload.new as TouchEvent, ...prev]);
                }
            )
            .subscribe();

        return () => {
            supabase.removeChannel(channel);
        };
    }, []);

    // --- Data Processing: Build Triage Matrix ---
    const aggregatedLeads = useMemo(() => {
        const leadsMap = new Map<string, LeadStatus>();

        touches.forEach(touch => {
            // Determine primary identifier (favor phone if available, then email, else fallback)
            const identifier = touch.phone || touch.email;
            if (!identifier) return;

            const existing = leadsMap.get(identifier);
            const isLatest = !existing || new Date(touch.ts) > new Date(existing.last_contacted);

            // Determine "status" based on touch history
            // Heuristic: If there's an inbound reply, they are 'replied'. 
            // If we sent multiple, maybe 'negotiating'. (For now, derive from touch status if available, else simplify)
            let derivedStatus = 'sent';
            let unread = false;

            if (touch.payload?.direction === 'inbound' || touch.status === 'replied') {
                derivedStatus = 'replied';
                unread = true; // Assume unread if it's an inbound reply (need a real read-receipt system later)
            } else if (touch.status === 'booked' || touch.status === 'won') {
                derivedStatus = touch.status;
            }

            if (!existing) {
                leadsMap.set(identifier, {
                    id: identifier,
                    company: touch.company || 'Unknown Target',
                    last_contacted: touch.ts,
                    status: derivedStatus,
                    unread: unread,
                    channels: [touch.channel],
                    latest_message: touch.body || (touch.channel === 'call' ? '[Audio Transcript Payload]' : '[Encrypted Payload]'),
                    campaign: touch.variant_name || 'System / Uncategorized'
                });
            } else {
                // Update existing if this touch is newer
                if (isLatest) {
                    existing.last_contacted = touch.ts;
                    existing.latest_message = touch.body || (touch.channel === 'call' ? '[Audio Transcript Payload]' : '[Encrypted Payload]');
                    existing.campaign = touch.variant_name || existing.campaign;
                    // Only upgrade status, don't downgrade (e.g., if they replied before, keep them as replied even if we sent another message, until marked otherwise)
                    if (existing.status === 'sent' && derivedStatus !== 'sent') {
                        existing.status = derivedStatus;
                        existing.unread = unread;
                    }
                }
                if (!existing.channels.includes(touch.channel)) {
                    existing.channels.push(touch.channel);
                }
            }
        });

        return Array.from(leadsMap.values());
    }, [touches]);

    // --- Filtering ---
    const filteredLeads = useMemo(() => {
        let filtered = aggregatedLeads;

        // Apply Tab Filter
        if (activeTab === 'unread') {
            filtered = filtered.filter(l => l.status === 'replied' || l.unread);
        } else if (activeTab === 'negotiating') {
            filtered = filtered.filter(l => l.status === 'negotiating' || l.status === 'sent'); // Simplified for now
        } else if (activeTab === 'booked') {
            filtered = filtered.filter(l => l.status === 'booked' || l.status === 'won');
        }

        // Apply Search Filter
        if (searchQuery) {
            const lowerQ = searchQuery.toLowerCase();
            filtered = filtered.filter(l =>
                l.company.toLowerCase().includes(lowerQ) ||
                l.id.toLowerCase().includes(lowerQ) ||
                l.latest_message.toLowerCase().includes(lowerQ)
            );
        }

        // Sort by recency
        return filtered.sort((a, b) => new Date(b.last_contacted).getTime() - new Date(a.last_contacted).getTime());
    }, [aggregatedLeads, activeTab, searchQuery]);

    // Group filtered leads by Campaign
    const groupedLeads = useMemo(() => {
        const groups = new Map<string, LeadStatus[]>();
        filteredLeads.forEach(lead => {
            const camp = lead.campaign;
            if (!groups.has(camp)) groups.set(camp, []);
            groups.get(camp)!.push(lead);
        });
        // Sort campaigns alphabetically
        return Array.from(groups.entries()).sort((a, b) => a[0].localeCompare(b[0]));
    }, [filteredLeads]);

    // --- Active Thread ---
    const activeThread = useMemo(() => {
        if (!selectedContactId) return [];
        return touches
            .filter(t => (t.phone === selectedContactId || t.email === selectedContactId))
            .sort((a, b) => new Date(a.ts).getTime() - new Date(b.ts).getTime());
    }, [selectedContactId, touches]);

    const activeLeadMeta = aggregatedLeads.find(l => l.id === selectedContactId);


    // --- Handlers ---
    const executeManualOverride = async () => {
        if (!replyText.trim() || !selectedContactId) return;

        // Optimistic UI insert
        const optimisticMessage: TouchEvent = {
            id: `temp-${Date.now()}`,
            body: replyText,
            channel: 'sms', // default UI assumption
            status: 'sending',
            ts: new Date().toISOString(),
            phone: selectedContactId, // Assuming ID is phone - need better logic if email
            email: null,
            company: activeLeadMeta?.company || 'Unknown',
            variant_name: 'Manual Override',
            payload: { direction: 'outbound', type: 'manual_override' }
        };

        setTouches(prev => [optimisticMessage, ...prev]);
        setReplyText('');

        // Execute backend sequence
        try {
            const response = await fetch('/api/manual-override', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contact_identifier: selectedContactId,
                    channel: 'sms',
                    body: optimisticMessage.body,
                }),
            });

            const resData = await response.json();
            if (!response.ok) throw new Error(resData.error || 'Failed manual override');

            // Replace optimistic log with verified DB entry on backend sync
            setTouches(prev => prev.map(t => t.id === optimisticMessage.id ? { ...t, status: 'sent', payload: { ...t.payload, ai_paused: true } } : t));
        } catch (e) {
            console.error(e);
            setTouches(prev => prev.map(t => t.id === optimisticMessage.id ? { ...t, status: 'failed' } : t));
        }
    };

    const handleSaveDirective = async () => {
        if (!directiveText.trim() || !selectedContactId) return;
        setIsSavingDirective(true);
        try {
            // Optimistic UI for Directive insert (In Phase 12 this maps to an AI memory table)
            const directiveTouch: TouchEvent = {
                id: `directive-${Date.now()}`,
                body: `COMMANDER DIRECTIVE: ${directiveText}`,
                channel: 'sms', // System note
                status: 'directive',
                ts: new Date().toISOString(),
                phone: selectedContactId,
                email: null,
                company: activeLeadMeta?.company || 'Unknown',
                variant_name: 'Strategic Override',
                payload: { direction: 'system', type: 'training_directive' }
            };
            setTouches(prev => [directiveTouch, ...prev]);
            setDirectiveText('');
        } catch (e) {
            console.error("Failed to save directive:", e);
        } finally {
            setIsSavingDirective(false);
        }
    };

    // --- Helpers ---
    const getChannelIcon = (channel: string, className?: string) => {
        switch (channel) {
            case 'sms': return <MessageSquare className={twMerge("w-3 h-3 text-blue-400", className)} />;
            case 'email': return <Mail className={twMerge("w-3 h-3 text-emerald-400", className)} />;
            case 'call': return <Phone className={twMerge("w-3 h-3 text-purple-400", className)} />;
            default: return <MessageSquare className={twMerge("w-3 h-3 text-slate-400", className)} />;
        }
    };

    return (
        <div className="flex flex-col h-screen bg-slate-950 text-slate-200 overflow-hidden font-sans">

            {/* --- TOP HEADER NAVIGATION --- */}
            <header className="shrink-0 h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md px-6 flex items-center justify-between z-20">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <div className="relative flex h-3 w-3">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                        </div>
                        <h1 className="text-lg font-bold tracking-tight text-white uppercase">Sovereign Triage Deck</h1>
                    </div>
                    <div className="h-6 w-px bg-slate-800 hidden sm:block"></div>
                    <div className="hidden sm:flex items-center text-xs font-mono text-slate-400 bg-slate-800/50 px-3 py-1.5 rounded-md border border-slate-700/50">
                        <ShieldAlert className="w-3 h-3 mr-2 text-amber-500" />
                        Live Telemetry Monitoring
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <button className="px-4 py-2 bg-red-500/10 text-red-500 hover:bg-red-500 hover:text-white border border-red-500/20 rounded-md text-xs font-bold transition-all flex items-center gap-2 uppercase tracking-wider shadow-[0_0_15px_rgba(239,68,68,0.1)] hover:shadow-[0_0_20px_rgba(239,68,68,0.4)]">
                        Halt All Campaigns
                    </button>
                </div>
            </header>

            {/* --- MAIN LAYOUT --- */}
            <div className="flex flex-1 overflow-hidden">

                {/* --- LEFT PANEL: TRIAGE BROWSER --- */}
                <div className="w-[380px] shrink-0 border-r border-slate-800 bg-slate-900/30 flex flex-col z-10 relative shadow-[4px_0_24px_-10px_rgba(0,0,0,0.5)]">

                    {/* Search Bar */}
                    <div className="p-4 border-b border-slate-800/50 bg-slate-900/50">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                            <input
                                type="text"
                                placeholder="Search targets, transcripts, identifiers..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full bg-slate-950/50 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all placeholder:text-slate-600 shadow-inner"
                            />
                        </div>
                    </div>

                    {/* Filter Tabs */}
                    <div className="flex px-2 py-2 border-b border-slate-800/50 bg-slate-900/20 overflow-x-auto no-scrollbar">
                        {[
                            { id: 'unread', label: 'Priority / Replies', icon: AlertCircle, color: 'text-amber-400', count: aggregatedLeads.filter(l => l.unread).length },
                            { id: 'negotiating', label: 'Active Pipeline', icon: Clock, color: 'text-indigo-400' },
                            { id: 'booked', label: 'Booked / Won', icon: CheckCircle2, color: 'text-emerald-400' },
                            { id: 'all', label: 'All Dispatches', icon: Eye, color: 'text-slate-400' },
                        ].map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id as any)}
                                className={clsx(
                                    "flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-semibold whitespace-nowrap transition-all",
                                    activeTab === tab.id
                                        ? "bg-slate-800 text-white shadow-sm"
                                        : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                                )}
                            >
                                <tab.icon className={twMerge("w-3.5 h-3.5", activeTab === tab.id ? tab.color : "opacity-70")} />
                                {tab.label}
                                {tab.count !== undefined && tab.count > 0 && (
                                    <span className="ml-1.5 px-1.5 py-0.5 rounded-full bg-red-500/20 text-red-400 text-[10px] min-w-[20px] text-center border border-red-500/30">
                                        {tab.count}
                                    </span>
                                )}
                            </button>
                        ))}
                    </div>

                    {/* Leads List */}
                    <div className="flex-1 overflow-y-auto">
                        {loading ? (
                            <div className="flex flex-col gap-3 p-4">
                                {[1, 2, 3, 4, 5].map(i => (
                                    <div key={i} className="animate-pulse flex gap-4 p-4 rounded-xl border border-slate-800/50 bg-slate-800/20">
                                        <div className="w-10 h-10 rounded-full bg-slate-800"></div>
                                        <div className="flex-1 space-y-2 py-1">
                                            <div className="h-3 bg-slate-800 rounded w-3/4"></div>
                                            <div className="h-2 bg-slate-800 rounded w-1/2"></div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : filteredLeads.length === 0 ? (
                            <div className="flex flex-col items-center justify-center h-full text-slate-500 p-8 text-center">
                                <ShieldAlert className="w-12 h-12 mb-4 opacity-20" />
                                <p className="text-sm font-medium">No targets found in this sector.</p>
                                <p className="text-xs mt-1 opacity-60">Adjust your filtering parameters to view telemetry.</p>
                            </div>
                        ) : (
                            <div className="flex flex-col p-2 space-y-4">
                                {groupedLeads.map(([campaign, leads]) => (
                                    <div key={campaign} className="flex flex-col space-y-1">
                                        <div className="flex items-center gap-2 px-2 pt-1 pb-2">
                                            <div className="h-px bg-slate-800 flex-1"></div>
                                            <h3 className="text-[10px] font-bold text-indigo-400/80 uppercase tracking-widest">{campaign} <span className="text-slate-600">({leads.length})</span></h3>
                                            <div className="h-px bg-slate-800 flex-1"></div>
                                        </div>
                                        {leads.map(lead => (
                                            <button
                                                key={lead.id}
                                                onClick={() => setSelectedContactId(lead.id)}
                                                className={clsx(
                                                    "w-full text-left p-3 rounded-lg border transition-all relative overflow-hidden group",
                                                    selectedContactId === lead.id
                                                        ? "bg-slate-800 border-indigo-500/50 shadow-[0_0_15px_rgba(99,102,241,0.1)]"
                                                        : "bg-slate-900/40 border-slate-800/50 hover:bg-slate-800/60 hover:border-slate-700",
                                                    lead.unread && selectedContactId !== lead.id && "border-amber-500/30 bg-amber-500/5"
                                                )}
                                            >
                                                {/* Unread Indicator Bar */}
                                                {lead.unread && (
                                                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.5)]"></div>
                                                )}

                                                <div className="flex justify-between items-start mb-2">
                                                    <div className="flex flex-col">
                                                        <span className="font-bold text-sm text-slate-200 truncate pr-2">
                                                            {lead.company}
                                                        </span>
                                                        <span className="text-[10px] text-slate-500 font-mono truncate">
                                                            {lead.id}
                                                        </span>
                                                    </div>
                                                    <span className="text-[10px] text-slate-500 font-mono shrink-0 bg-slate-950/50 px-1.5 py-0.5 rounded border border-slate-800">
                                                        {new Date(lead.last_contacted).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                                                    </span>
                                                </div>

                                                <div className="text-xs text-slate-400 line-clamp-2 leading-relaxed mb-2 font-mono bg-slate-950/30 p-2 rounded border border-slate-800/50">
                                                    {lead.latest_message || <span className="italic opacity-50">[Encrypted Payload]</span>}
                                                </div>

                                                <div className="flex items-center justify-between">
                                                    {/* Channel Indicators */}
                                                    <div className="flex gap-1">
                                                        {lead.channels.includes('email') && <div className="p-1 rounded bg-emerald-500/10 border border-emerald-500/20"><Mail className="w-3 h-3 text-emerald-400" /></div>}
                                                        {lead.channels.includes('sms') && <div className="p-1 rounded bg-blue-500/10 border border-blue-500/20"><MessageSquare className="w-3 h-3 text-blue-400" /></div>}
                                                        {lead.channels.includes('call') && <div className="p-1 rounded bg-purple-500/10 border border-purple-500/20"><Phone className="w-3 h-3 text-purple-400" /></div>}
                                                    </div>

                                                    {/* Status Badge */}
                                                    <span className={clsx(
                                                        "text-[9px] uppercase tracking-wider font-bold px-2 py-0.5 rounded-full border",
                                                        lead.status === 'replied' ? "bg-amber-500/10 text-amber-400 border-amber-500/20" :
                                                            lead.status === 'booked' ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" :
                                                                "bg-slate-800 text-slate-400 border-slate-700"
                                                    )}>
                                                        {lead.status}
                                                    </span>
                                                </div>
                                            </button>
                                        ))}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* --- CENTER PANEL: OMNI-THREAD VIEWER --- */}
                <div className="flex-1 flex flex-col bg-slate-950 relative">

                    {!selectedContactId ? (
                        <div className="flex-1 flex flex-col items-center justify-center text-slate-600 pattern-isometric-slate-900/20">
                            <div className="h-20 w-20 mb-6 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center shadow-2xl skew-y-6 transform rotate-3">
                                <Search className="w-8 h-8 text-indigo-500/50" />
                            </div>
                            <h2 className="text-xl font-bold tracking-tight text-slate-300 mb-2 font-mono uppercase">Target Vector Not Selected</h2>
                            <p className="text-sm text-slate-500 max-w-sm text-center">Select a target from the Triage Matrix on the left to intercept communications and review intelligence dossiers.</p>
                        </div>
                    ) : (
                        <>
                            {/* Thread Header */}
                            <div className="px-6 py-4 border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm flex justify-between items-center z-10 shadow-sm sticky top-0">
                                <div className="flex items-center gap-4">
                                    <div className="h-10 w-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center">
                                        <Building2 className="w-5 h-5 text-indigo-400" />
                                    </div>
                                    <div>
                                        <h2 className="text-lg font-bold text-slate-200">{activeLeadMeta?.company}</h2>
                                        <div className="flex items-center gap-3 text-xs font-mono text-slate-500 mt-0.5">
                                            <span className="flex items-center gap-1">
                                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                                                Stream Active
                                            </span>
                                            <span className="opacity-50">|</span>
                                            <span className="select-all hover:text-slate-300 transition-colors">{activeLeadMeta?.id}</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    <button className="px-3 py-1.5 text-xs font-semibold bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-md transition-colors text-slate-300 flex items-center gap-1.5">
                                        <UserCircle2 className="w-4 h-4" />
                                        View Full Dossier
                                    </button>
                                </div>
                            </div>

                            {/* Chat Transcript Area */}
                            <div className="flex-1 overflow-y-auto p-6 scroll-smooth bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900/20 via-slate-950 to-slate-950">
                                <div className="max-w-4xl mx-auto flex flex-col gap-6">

                                    <div className="flex justify-center my-4">
                                        <span className="text-[10px] font-mono text-slate-500 bg-slate-900 border border-slate-800 px-3 py-1 rounded-full">
                                            End-to-End Encryption Established
                                        </span>
                                    </div>

                                    {activeThread.map(touch => {
                                        const isInbound = touch.payload?.direction === 'inbound' || touch.status === 'replied'; // Fallback heuristic

                                        return (
                                            <div key={touch.id} className={clsx("flex w-full group", isInbound ? "justify-start" : "justify-end")}>

                                                {/* Avatar (Left side for inbound) */}
                                                {isInbound && (
                                                    <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 shrink-0 mr-3 mt-auto flex items-center justify-center">
                                                        <UserCircle2 className="w-4 h-4 text-slate-400" />
                                                    </div>
                                                )}

                                                <div className="flex flex-col max-w-[85%] relative">

                                                    {/* Meta Info Above Bubble */}
                                                    <div className={clsx("flex items-center gap-2 mb-1.5 px-1", isInbound ? "justify-start" : "justify-end")}>
                                                        <span className="flex items-center gap-1 text-[10px] font-mono uppercase tracking-wider text-slate-500">
                                                            {getChannelIcon(touch.channel)}
                                                            {touch.channel}
                                                        </span>
                                                        <span className="text-[10px] text-slate-600 font-mono">
                                                            {new Date(touch.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                        </span>
                                                    </div>

                                                    {/* Message Bubble */}
                                                    <div className={clsx(
                                                        "rounded-2xl px-5 py-3.5 shadow-md relative",
                                                        isInbound
                                                            ? "bg-slate-800/80 border border-slate-700/50 text-slate-200 rounded-bl-sm"
                                                            : "bg-indigo-600 border border-indigo-500 text-white rounded-br-sm glow-indigo-sm"
                                                    )}>

                                                        {/* Variant Badge for Outbound */}
                                                        {!isInbound && touch.variant_name && (
                                                            <div className="absolute -top-3 right-4 bg-indigo-900 border border-indigo-400 text-indigo-200 text-[9px] px-2 py-0.5 rounded-full whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity whitespace-pre truncate max-w-[200px]">
                                                                Variant: {touch.variant_name}
                                                            </div>
                                                        )}

                                                        {/* Rich Body Rendering (Handle HTML emails basically) */}
                                                        <div className={clsx("text-[15px] leading-[1.6] font-sans break-words", isInbound ? "prose prose-invert prose-sm max-w-none" : "whitespace-pre-wrap")}>
                                                            {touch.body ? (
                                                                // Very simple dangerous HTML rendering for emails, text for SMS
                                                                touch.channel === 'email' ? (
                                                                    <div dangerouslySetInnerHTML={{ __html: touch.body.replace(/\n/g, '<br>') }} />
                                                                ) : (
                                                                    touch.body
                                                                )
                                                            ) : (
                                                                <span className="italic opacity-60 font-mono text-sm">
                                                                    {touch.channel === 'call' ? '[Audio Transcript Payload Unresolved]' : '[No Payload Recorded]'}
                                                                </span>
                                                            )}
                                                        </div>
                                                    </div>

                                                    {/* Status Below Bubble (Outbound Only) */}
                                                    {!isInbound && (
                                                        <div className="flex justify-end mt-1.5 px-1">
                                                            <span className="text-[9px] uppercase tracking-wider font-semibold text-slate-500 flex items-center gap-1">
                                                                {touch.status === 'sending' ? (
                                                                    <><span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-ping"></span> Dispatching...</>
                                                                ) : touch.status === 'delivered' ? (
                                                                    <><CheckCircle2 className="w-3 h-3 text-emerald-500" /> Delivered</>
                                                                ) : touch.status === 'opened' ? (
                                                                    <><Eye className="w-3 h-3 text-emerald-400" /> Opened</>
                                                                ) : (
                                                                    <span className="opacity-60">{touch.status}</span>
                                                                )}
                                                            </span>
                                                        </div>
                                                    )}

                                                </div>

                                                {/* Avatar (Right side for outbound) */}
                                                {!isInbound && (
                                                    <div className="w-8 h-8 rounded-full bg-indigo-900 border border-indigo-500 shrink-0 ml-3 mt-auto flex items-center justify-center">
                                                        <span className="text-[10px] font-bold text-indigo-300">AI</span>
                                                    </div>
                                                )}
                                            </div>
                                        )
                                    })}

                                    {/* Future Outreach Placeholder */}
                                    {activeLeadMeta?.status !== 'replied' && activeLeadMeta?.status !== 'booked' && activeLeadMeta?.status !== 'won' && (
                                        <div className="flex w-full justify-center mt-6 mb-2 opacity-60 hover:opacity-100 transition-opacity">
                                            <div className="border border-dashed border-indigo-500/50 bg-indigo-500/5 rounded-xl px-6 py-4 flex flex-col items-center max-w-sm text-center shadow-inner">
                                                <Clock className="w-5 h-5 text-indigo-400 mb-2 animate-pulse" />
                                                <h4 className="text-xs font-bold text-indigo-300 uppercase tracking-widest mb-1">Awaiting Target Response</h4>
                                                <p className="text-[10px] text-slate-400 leading-relaxed">Autonomous sequence paused. If no response is detected, the next escalation payload will dispatch per campaign parameters.</p>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Command Input Area */}
                            <div className="p-4 bg-slate-900 border-t border-slate-800 z-10 shrink-0">
                                <div className="max-w-4xl mx-auto relative group">
                                    <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl opacity-0 group-focus-within:opacity-20 transition duration-500 blur"></div>
                                    <div className="relative flex items-end gap-2 bg-slate-950 border border-slate-700 focus-within:border-indigo-500 rounded-xl p-2 transition-colors">

                                        <button className="h-10 w-10 shrink-0 rounded-lg flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-800 transition-colors" title="Attach Files">
                                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" /></svg>
                                        </button>

                                        <textarea
                                            value={replyText}
                                            onChange={(e) => setReplyText(e.target.value)}
                                            className="w-full bg-transparent border-none focus:ring-0 text-sm text-slate-200 placeholder:text-slate-600 resize-none max-h-32 min-h-[40px] py-2"
                                            placeholder="Transmit manual override payload to target..."
                                            rows={1}
                                            onKeyDown={(e) => {
                                                if (e.key === 'Enter' && !e.shiftKey) {
                                                    e.preventDefault();
                                                    executeManualOverride();
                                                }
                                            }}
                                        />

                                        <button
                                            onClick={executeManualOverride}
                                            disabled={!replyText.trim()}
                                            className="h-10 px-4 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:bg-slate-800 disabled:text-slate-500 text-white rounded-lg font-bold text-sm transition-all shadow-lg flex items-center gap-2 shrink-0 group-focus-within:shadow-[0_0_15px_rgba(79,70,229,0.4)]"
                                        >
                                            <Send className="w-4 h-4" />
                                            <span>TRANSMIT</span>
                                        </button>
                                    </div>

                                    <div className="flex justify-between mt-2 px-2">
                                        <div className="flex items-center gap-1.5 text-[10px] text-slate-500 uppercase tracking-wider font-mono">
                                            <ShieldAlert className="w-3 h-3 text-amber-500/70" />
                                            Transmitting suspends autonomous AI modules for target
                                        </div>
                                        <div className="flex gap-3 text-[10px] text-slate-600 font-mono">
                                            <span className="flex items-center gap-1 cursor-pointer hover:text-slate-400">
                                                <div className="w-2 h-2 rounded-full border border-current flex items-center justify-center p-[1px]"><div className="w-full h-full rounded-full bg-current"></div></div>
                                                Send as SMS
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </>
                    )}
                </div>

                {/* --- RIGHT PANEL: Directives & Dossier --- */}
                {selectedContactId && (
                    <div className="w-[300px] border-l border-slate-800 bg-slate-900/30 overflow-y-auto hidden lg:flex flex-col p-4 shadow-[-4px_0_24px_-10px_rgba(0,0,0,0.5)] z-10">

                        {/* Commander's Directives Active Widget */}
                        <div className="mb-6">
                            <h3 className="text-xs uppercase tracking-widest text-slate-400 font-bold mb-3 flex items-center gap-2">
                                <ShieldAlert className="w-3.5 h-3.5 text-indigo-400" />
                                Commander&apos;s Directives
                            </h3>
                            <div className="bg-slate-900 border border-slate-700 rounded-lg overflow-hidden group focus-within:border-indigo-500 transition-colors shadow-inner">
                                <textarea
                                    className="w-full bg-transparent text-sm text-slate-200 placeholder:text-slate-600 p-3 resize-none min-h-[120px] focus:outline-none"
                                    placeholder="Draft strategic overrides or context constraints for the Autonomous AI. (e.g. 'Push hard on the lack of a website' or 'Offer the Lakeland Discount')..."
                                    value={directiveText}
                                    onChange={(e) => setDirectiveText(e.target.value)}
                                ></textarea>
                                <div className="bg-slate-950 px-3 py-2 flex justify-between items-center border-t border-slate-800">
                                    <span className="text-[10px] text-slate-500 font-mono">
                                        Inject into AI Memory
                                    </span>
                                    <button
                                        onClick={handleSaveDirective}
                                        disabled={!directiveText.trim() || isSavingDirective}
                                        className="text-[10px] uppercase font-bold tracking-wider px-3 py-1 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded transition-colors"
                                    >
                                        {isSavingDirective ? 'Fusing...' : 'Fuse Logic'}
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* View Past Directives */}
                        <div className="mb-6 flex flex-col gap-2">
                            {activeThread.filter(t => t.status === 'directive').map(directive => (
                                <div key={directive.id} className="bg-slate-950/50 border border-slate-800 rounded p-3 relative overflow-hidden">
                                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-indigo-500/50"></div>
                                    <div className="flex justify-between items-start mb-1">
                                        <span className="text-[9px] uppercase tracking-wider text-indigo-400 font-bold">System Directive</span>
                                        <span className="text-[9px] text-slate-600 font-mono">{new Date(directive.ts).toLocaleDateString()}</span>
                                    </div>
                                    <p className="text-xs text-slate-400 leading-relaxed italic border-l border-slate-800 pl-2 ml-1">
                                        &quot;{directive.body?.replace('COMMANDER DIRECTIVE: ', '')}&quot;
                                    </p>
                                </div>
                            ))}
                        </div>

                        {/* Tactical Target Dossier stub*/}
                        <div>
                            <h3 className="text-xs uppercase tracking-widest text-slate-400 font-bold mb-3 flex items-center gap-2">
                                Tactical Dossier
                            </h3>
                            <div className="bg-slate-950/50 border border-slate-800 rounded-lg p-4 text-sm text-slate-300">
                                <div className="mb-3">
                                    <div className="text-[10px] uppercase tracking-wider text-slate-500 mb-1">Company Name</div>
                                    <div className="font-semibold">{activeLeadMeta?.company}</div>
                                </div>
                                <div className="mb-3">
                                    <div className="text-[10px] uppercase tracking-wider text-slate-500 mb-1">Vector</div>
                                    <div className="font-mono text-xs break-all">{activeLeadMeta?.id}</div>
                                </div>
                                <div>
                                    <div className="text-[10px] uppercase tracking-wider text-slate-500 mb-1">Abacus Intel</div>
                                    <div className="flex flex-wrap gap-1 mt-1">
                                        <span className="text-[9px] px-1.5 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded">Engaged</span>
                                        <span className="text-[9px] px-1.5 py-0.5 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded">Warm</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
