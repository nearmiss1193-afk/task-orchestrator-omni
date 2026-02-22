'use client';

import React, { useEffect, useState } from 'react';

export default function VoiceTranscriptionHUD() {
    const [calls, setCalls] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedCall, setSelectedCall] = useState<any | null>(null);

    useEffect(() => {
        const fetchVapiCalls = async () => {
            try {
                const res = await fetch('/api/vapi/calls');
                if (!res.ok) throw new Error('Failed to fetch from Vapi Edge API');

                const data = await res.json();

                // Filter out highly empty calls
                const validCalls = data.filter((c: any) => c.status === 'ended' && c.messages && c.messages.length > 0);
                setCalls(validCalls);

                if (validCalls.length > 0) {
                    setSelectedCall(validCalls[0]);
                }
            } catch (err) {
                console.error('Voice HUD Mount Error:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchVapiCalls();
    }, []);

    const formatDuration = (startedAt: string, endedAt: string) => {
        if (!startedAt || !endedAt) return 'Unknown';
        const start = new Date(startedAt);
        const end = new Date(endedAt);
        const diffSecs = Math.floor((end.getTime() - start.getTime()) / 1000);
        const mins = Math.floor(diffSecs / 60);
        const secs = diffSecs % 60;
        return `${mins}m ${secs}s`;
    };

    return (
        <div className="h-screen bg-slate-950 flex flex-col overflow-hidden">

            {/* Header */}
            <div className="h-20 border-b border-slate-800 bg-slate-900/50 flex items-center px-8 shrink-0">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                        <svg className="w-6 h-6 text-fuchsia-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" /></svg>
                        Voice AI Interceptors
                    </h1>
                    <p className="text-slate-400 text-sm mt-1">Real-time Vapi Call Transcripts & Telemetry Logging</p>
                </div>
            </div>

            <div className="flex-1 flex overflow-hidden">
                {/* Left Sidebar: Call List */}
                <div className="w-1/3 border-r border-slate-800 bg-slate-900/30 overflow-y-auto">
                    {loading ? (
                        <div className="flex flex-col items-center justify-center h-full gap-4 text-slate-500">
                            <span className="w-6 h-6 border-2 border-fuchsia-500 border-t-transparent rounded-full animate-spin"></span>
                            Fetching Autonomous Calls...
                        </div>
                    ) : calls.length === 0 ? (
                        <div className="p-8 text-center text-slate-500">No completed calls found.</div>
                    ) : (
                        calls.map((call) => (
                            <div
                                key={call.id}
                                onClick={() => setSelectedCall(call)}
                                className={`p-5 border-b border-slate-800/50 cursor-pointer transition-colors hover:bg-slate-800/40 ${selectedCall?.id === call.id ? 'bg-slate-800/80 border-l-4 border-l-fuchsia-500' : 'border-l-4 border-l-transparent'}`}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <span className="text-slate-200 font-medium font-mono">
                                        {call.customer?.number || 'Unknown Caller'}
                                    </span>
                                    <span className="text-xs text-slate-500">
                                        {new Date(call.createdAt).toLocaleDateString()}
                                    </span>
                                </div>
                                <div className="flex items-center gap-3 text-xs text-slate-400">
                                    <span className="bg-slate-800 px-2 py-0.5 rounded">{formatDuration(call.createdAt, call.endedAt)}</span>
                                    <span className="text-emerald-400 font-medium">{call.cost ? `$${call.cost.toFixed(3)}` : ''}</span>
                                </div>
                                {call.summary && (
                                    <p className="text-slate-500 text-sm mt-3 line-clamp-2 italic">
                                        "{call.summary}"
                                    </p>
                                )}
                            </div>
                        ))
                    )}
                </div>

                {/* Right Sidebar: Transcript Bubbles */}
                <div className="w-2/3 bg-slate-950 overflow-y-auto relative">
                    {selectedCall ? (
                        <div className="p-8 max-w-4xl mx-auto pb-32">

                            <div className="mb-10 p-6 bg-slate-900 border border-slate-800 rounded-xl flex justify-between items-center">
                                <div>
                                    <h2 className="text-xl font-bold text-white mb-1">Call Telemetry: {selectedCall.customer?.number || 'Unknown'}</h2>
                                    <p className="text-slate-400 text-sm font-mono tracking-wide">ID: {selectedCall.id}</p>
                                </div>
                                {selectedCall.recordingUrl && (
                                    <a href={selectedCall.recordingUrl} target="_blank" rel="noreferrer" className="flex items-center gap-2 px-4 py-2 bg-fuchsia-600 hover:bg-fuchsia-500 text-white rounded-lg shadow-lg shadow-fuchsia-500/20 transition-all font-medium text-sm">
                                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                        Listen to Tape
                                    </a>
                                )}
                            </div>

                            <div className="space-y-6">
                                {selectedCall.messages?.map((msg: any, idx: number) => {
                                    if (msg.role !== 'user' && msg.role !== 'assistant') return null;
                                    const isAI = msg.role === 'assistant';

                                    return (
                                        <div key={idx} className={`flex ${isAI ? 'justify-start' : 'justify-end'}`}>
                                            <div className={`max-w-[75%] rounded-2xl p-5 ${isAI ? 'bg-slate-800 text-slate-200 rounded-tl-sm' : 'bg-fuchsia-600/20 text-fuchsia-100 border border-fuchsia-500/30 rounded-tr-sm'}`}>
                                                <div className="text-[10px] uppercase font-bold tracking-widest mb-2 opacity-50">
                                                    {isAI ? 'Sarah AI' : 'Human Caller'}
                                                </div>
                                                <p className="leading-relaxed whitespace-pre-wrap">{msg.message}</p>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    ) : (
                        <div className="absolute inset-0 flex items-center justify-center text-slate-600">
                            Select a transmission to decrypt the transcript.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
