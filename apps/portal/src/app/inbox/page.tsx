'use client';

import React, { useEffect, useState, useRef } from 'react';
import { supabase } from '@/lib/supabaseClient';

export default function InboxPage() {
    const [touches, setTouches] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedContact, setSelectedContact] = useState<string | null>(null);
    const [replyText, setReplyText] = useState('');

    // Fetch initial telemetry
    useEffect(() => {
        const fetchInitialLogs = async () => {
            setLoading(true);
            const { data, error } = await supabase
                .table('outbound_touches')
                .select('*')
                .order('ts', { ascending: false })
                .limit(100);

            if (error) {
                console.error('Error fetching inbox telemetry:', error);
            } else if (data) {
                setTouches(data);
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
                    setTouches((prev) => [payload.new, ...prev]);
                }
            )
            .subscribe();

        return () => {
            supabase.removeChannel(channel);
        };
    }, []);

    // Compute unique contacts based on phone/email mapping
    const contactsMap = new Map();
    touches.forEach((touch) => {
        const key = touch.phone || touch.email || 'Anonymous';
        if (!contactsMap.has(key)) {
            contactsMap.set(key, {
                id: key,
                lastMessage: touch.body || (touch.channel === 'call' ? 'Transcript logged' : 'No preview'),
                ts: touch.ts,
                channel: touch.channel,
                phone: touch.phone,
                email: touch.email,
                status: touch.status
            });
        }
    });

    const contactsList = Array.from(contactsMap.values()).sort((a, b) => new Date(b.ts).getTime() - new Date(a.ts).getTime());

    // Filter active thread 
    const activeThread = touches.filter(t => (t.phone || t.email || 'Anonymous') === selectedContact).sort((a, b) => new Date(a.ts).getTime() - new Date(b.ts).getTime());

    // Handle Manual Override
    const executeManualOverride = async () => {
        if (!replyText.trim() || !selectedContact) return;

        // Optimistic UI insert
        const optimisticMessage = {
            id: `temp-${Date.now()}`,
            body: replyText,
            channel: 'sms', // default UI assumption
            direction: 'outbound',
            status: 'sending',
            ts: new Date().toISOString(),
            phone: activeThread[0]?.phone,
            email: activeThread[0]?.email,
        };
        setTouches(prev => [optimisticMessage, ...prev]);
        setReplyText('');

        // Execute backend sequence
        try {
            const response = await fetch('/api/manual-override', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contact_identifier: selectedContact,
                    channel: 'sms',
                    body: optimisticMessage.body,
                }),
            });

            const resData = await response.json();
            if (!response.ok) throw new Error(resData.error || 'Failed manual override');

            // Replace optimistic log with verified DB entry on backend sync
            setTouches(prev => prev.map(t => t.id === optimisticMessage.id ? { ...t, status: 'sent', ai_paused: true } : t));
        } catch (e) {
            console.error(e);
            setTouches(prev => prev.map(t => t.id === optimisticMessage.id ? { ...t, status: 'failed' } : t));
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 text-slate-200">

            {/* Top HUD Nav */}
            <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md px-6 py-4 flex justify-between items-center sticky top-0 z-10">
                <div>
                    <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
                        Omni-Channel C2 Inbox
                    </h1>
                    <p className="text-xs text-slate-400 mt-1">Realtime Sovereign Empire Telemetry</p>
                </div>

                {/* Global Kill Switch Stub */}
                <button className="px-4 py-2 bg-red-500/10 text-red-400 hover:bg-red-500/20 hover:text-red-300 border border-red-500/20 rounded-md text-sm font-medium transition-all flex items-center gap-2">
                    <span>HALT CAMPAIGNS</span>
                </button>
            </nav>

            {/* 3-Pane Layout */}
            <div className="flex h-[calc(100vh-80px)] overflow-hidden">

                {/* Left Pane: Contacts Queue */}
                <div className="w-[320px] border-r border-slate-800 bg-slate-900/20 overflow-y-auto hidden md:block">
                    <div className="p-4 border-b border-slate-800/50 bg-slate-900/80 sticky top-0 backdrop-blur">
                        <input
                            type="text"
                            placeholder="Search leads..."
                            className="w-full bg-slate-950/50 border border-slate-800 rounded px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-indigo-500 transition-colors placeholder:text-slate-600"
                        />
                    </div>

                    {loading ? (
                        <div className="p-8 text-center text-sm text-slate-500 animate-pulse">Connecting to Network...</div>
                    ) : (
                        <div className="flex flex-col">
                            {contactsList.map((contact) => (
                                <button
                                    key={contact.id}
                                    onClick={() => setSelectedContact(contact.id)}
                                    className={`p-4 border-b border-slate-800/30 text-left transition-all hover:bg-slate-800/40 cursor-default ${selectedContact === contact.id ? 'bg-slate-800/60 border-l-2 border-l-indigo-500' : 'border-l-2 border-l-transparent'}`}
                                >
                                    <div className="flex justify-between items-start mb-1">
                                        <span className="font-semibold text-sm truncate text-slate-200">
                                            {contact.id}
                                        </span>
                                        <span className="text-[10px] text-slate-500 font-mono shrink-0 ml-2">
                                            {new Date(contact.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </span>
                                    </div>
                                    <div className="text-xs text-slate-400 truncate mt-1 break-all flex items-center gap-2">
                                        <span className={`px-1.5 py-0.5 rounded text-[9px] font-medium uppercase tracking-wider ${contact.channel === 'sms' ? 'bg-blue-500/10 text-blue-400' : contact.channel === 'email' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-purple-500/10 text-purple-400'}`}>
                                            {contact.channel || 'UNK'}
                                        </span>
                                        <span className="truncate">{contact.lastMessage}</span>
                                    </div>
                                </button>
                            ))}
                            {contactsList.length === 0 && (
                                <div className="text-center p-8 text-xs text-slate-500">No telemetry detected</div>
                            )}
                        </div>
                    )}
                </div>

                {/* Center Pane: Active Thread Viewer */}
                <div className="flex-1 flex flex-col bg-slate-950 relative">

                    {!selectedContact ? (
                        <div className="flex-1 flex flex-col items-center justify-center text-slate-600">
                            <div className="h-16 w-16 mb-4 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center">
                                <svg className="w-6 h-6 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
                            </div>
                            <p className="font-medium text-slate-400">Target a contact vector to intercept streams</p>
                        </div>
                    ) : (
                        <>
                            {/* Thread Header */}
                            <div className="px-6 py-4 border-b border-slate-800 bg-slate-950 flex justify-between items-center shadow-sm">
                                <div>
                                    <h2 className="text-lg font-bold text-slate-200">{selectedContact}</h2>
                                    <p className="text-xs text-slate-500 flex items-center gap-2 mt-1">
                                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                                        Encrypted connection established
                                    </p>
                                </div>
                            </div>

                            {/* Realtime Transcripts */}
                            <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4">
                                {activeThread.map(touch => (
                                    <div key={touch.id} className={`flex ${(!touch.direction || touch.direction === 'outbound') ? 'justify-end' : 'justify-start'}`}>

                                        <div className={`max-w-[70%] rounded-2xl px-5 py-3 ${(!touch.direction || touch.direction === 'outbound') ? 'bg-indigo-600 border border-indigo-500 text-indigo-50' : 'bg-slate-800 border border-slate-700 text-slate-200'}`}>

                                            <div className="flex items-center gap-2 mb-2 pb-2 border-b border-black/10">
                                                <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded ${(!touch.direction || touch.direction === 'outbound') ? 'bg-indigo-950/40 text-indigo-300' : 'bg-slate-900/50 text-slate-400'}`}>
                                                    {touch.channel || 'System'}
                                                </span>
                                                <span className="text-[10px] opacity-70 ml-auto">
                                                    {new Date(touch.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                </span>
                                            </div>

                                            <p className="text-sm leading-relaxed whitespace-pre-wrap font-sans">
                                                {touch.body || (touch.channel === 'call' ? '[Encrypted Voice Transcript Payload]' : '[No Body Analyzed]')}
                                            </p>

                                            {/* Mini Status Indicator */}
                                            {(!touch.direction || touch.direction === 'outbound') && (
                                                <div className="text-[9px] uppercase tracking-wide float-right mt-2 font-medium opacity-60 flex items-center gap-1">
                                                    {touch.status === 'sending' ? (
                                                        <><span className="w-1 h-1 rounded-full bg-indigo-300 animate-ping"></span> Sending</>
                                                    ) : touch.status === 'delivered' ? '✓ Delivered' : touch.status === 'read' ? '✓✓ Read' : touch.status}
                                                </div>
                                            )}

                                        </div>
                                    </div>
                                ))}
                                <div className="h-4"></div>
                            </div>

                            {/* Manual Override Execute Console */}
                            <div className="p-4 bg-slate-950 border-t border-slate-800">
                                <div className="relative">
                                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-red-500/20 to-orange-500/0 rounded-t-lg -translate-y-px pointer-events-none"></div>
                                    <textarea
                                        value={replyText}
                                        onChange={(e) => setReplyText(e.target.value)}
                                        className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-4 pr-32 py-3 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all resize-none h-[80px]"
                                        placeholder="Deploy manual override payload... (This will halt autonomous agents for this target)"
                                    />
                                    <button
                                        onClick={executeManualOverride}
                                        disabled={!replyText.trim()}
                                        className="absolute bottom-3 right-3 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:hover:bg-indigo-600 text-white rounded font-medium text-sm transition-all shadow-lg flex items-center gap-2"
                                    >
                                        <span>EXECUTE</span>
                                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
                                    </button>
                                </div>
                                <div className="flex justify-between items-center mt-2 px-1">
                                    <span className="text-[10px] text-slate-500 uppercase tracking-widest font-mono flex items-center gap-1">
                                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
                                        AI Lock Protocol active upon deployment
                                    </span>
                                    <span className="text-[10px] text-slate-600 font-mono">
                                        {replyText.length} chars
                                    </span>
                                </div>
                            </div>
                        </>
                    )}

                </div>

                {/* Right Pane: Target Dossier */}
                {selectedContact && (
                    <div className="w-[300px] border-l border-slate-800 bg-slate-900/30 overflow-y-auto hidden lg:block p-6">
                        <h3 className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-4 flex items-center gap-2">
                            Target Dossier <span className="h-px bg-slate-700/50 flex-1"></span>
                        </h3>

                        <div className="bg-slate-900/50 rounded-lg border border-slate-800 p-4 mb-4">
                            <div className="text-xs text-slate-400 mb-1">Vector Identification</div>
                            <div className="font-mono text-sm text-slate-300 break-all">{selectedContact}</div>
                        </div>

                        <div className="bg-slate-900/50 rounded-lg border border-slate-800 p-4 mb-4">
                            <div className="flex justify-between items-center mb-3">
                                <span className="text-xs text-slate-400">Pipeline Stage</span>
                                <span className="w-2 h-2 rounded-full bg-orange-400"></span>
                            </div>
                            <div className="inline-block px-2 py-1 bg-orange-500/10 text-orange-400 border border-orange-500/20 rounded text-xs font-semibold whitespace-nowrap">
                                Active Negotiation
                            </div>
                        </div>

                        <div className="bg-slate-900/50 rounded-lg border border-slate-800 p-4">
                            <div className="text-xs text-slate-400 mb-2">Abacus Intelligence Tags</div>
                            <div className="flex flex-wrap gap-2">
                                <span className="px-2 py-1 bg-indigo-500/10 text-indigo-300 text-[10px] rounded border border-indigo-500/20 font-medium">Responsive</span>
                                <span className="px-2 py-1 bg-emerald-500/10 text-emerald-300 text-[10px] rounded border border-emerald-500/20 font-medium">Auto-Nurtured</span>
                                <span className="px-2 py-1 bg-red-500/10 text-red-300 text-[10px] rounded border border-red-500/20 font-medium whitespace-nowrap">Needs Human Intervention</span>
                            </div>
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
}
