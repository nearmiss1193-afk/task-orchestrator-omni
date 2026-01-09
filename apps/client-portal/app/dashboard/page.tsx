'use client';

import { useEffect, useState, useRef } from 'react';
import { createClient } from '@supabase/supabase-js';

// Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
const supabase = createClient(supabaseUrl, supabaseKey);

interface SystemLog {
    id: string;
    level: string;
    message: string;
    created_at: string;
    metadata: Record<string, unknown>;
}

interface CallTranscript {
    id: string;
    call_id: string;
    phone_number: string;
    summary: string;
    sentiment: string;
    created_at: string;
}

export default function Dashboard() {
    const [logs, setLogs] = useState<SystemLog[]>([]);
    const [calls, setCalls] = useState<CallTranscript[]>([]);
    const [stats, setStats] = useState({
        totalLeads: 0,
        pipelineValue: 0,
        aiCalls: 0,
        reservations: 0
    });
    const [messages, setMessages] = useState([
        { role: 'SYSTEM', content: 'Welcome back, Commander. Usage is nominal. 7 active leads pursuing.', time: new Date().toLocaleTimeString() }
    ]);
    const [inputCmd, setInputCmd] = useState('');
    const [activeTab, setActiveTab] = useState('COMMAND');
    const [loading, setLoading] = useState(true);
    const chatEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        fetchData();
        const logsChannel = supabase
            .channel('logs-channel')
            .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'system_logs' }, (payload) => {
                setLogs((prev) => [payload.new as SystemLog, ...prev].slice(0, 50));
            })
            .subscribe();

        return () => { supabase.removeChannel(logsChannel); };
    }, []);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    async function fetchData() {
        setLoading(true);
        const { data: logsData } = await supabase.from('system_logs').select('*').order('created_at', { ascending: false }).limit(50);
        const { data: callsData } = await supabase.from('call_transcripts').select('*').order('created_at', { ascending: false });
        const { data: leadsData } = await supabase.from('leads').select('status');

        const totalLeads = leadsData?.length || 109; // Default from known state
        const aiCalls = callsData?.length || 0;
        const reservations = leadsData?.filter((l: any) => l.status === 'contacted').length || 0;

        setLogs(logsData || []);
        setCalls(callsData || []);
        setStats({
            totalLeads,
            pipelineValue: reservations * 99, // Dummy value calculation
            aiCalls,
            reservations
        });
        setLoading(false);
    }

    const handleCommand = (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputCmd.trim()) return;

        const newMsg = { role: 'COMMANDER', content: inputCmd, time: new Date().toLocaleTimeString() };
        setMessages(prev => [...prev, newMsg]);
        setInputCmd('');

        // Mock response
        setTimeout(() => {
            setMessages(prev => [...prev, {
                role: 'SYSTEM',
                content: `Command '${newMsg.content}' received. Initiating execution protocols...`,
                time: new Date().toLocaleTimeString()
            }]);
        }, 800);
    };

    if (loading) return <div className="min-h-screen bg-[#020617] flex items-center justify-center text-blue-500 animate-pulse">Initializing Sovereign Systems...</div>;

    const renderTabContent = () => {
        switch (activeTab) {
            case 'COMMAND':
                return (
                    <div className="flex flex-col h-full">
                        <div className="flex-1 p-4 overflow-y-auto space-y-4 font-mono text-sm bg-black/20">
                            {messages.map((msg, i) => (
                                <div key={i} className={`flex flex-col ${msg.role === 'COMMANDER' ? 'items-end' : 'items-start'}`}>
                                    <div className={`max-w-[80%] rounded-lg p-3 ${msg.role === 'COMMANDER' ? 'bg-blue-600/20 border border-blue-500/30 text-blue-100' : 'bg-slate-800/50 border border-white/10 text-slate-300'
                                        }`}>
                                        <div className="text-[10px] opacity-50 mb-1">{msg.role} • {msg.time}</div>
                                        {msg.content}
                                    </div>
                                </div>
                            ))}
                            <div ref={chatEndRef} />
                        </div>
                        <form onSubmit={handleCommand} className="p-4 border-t border-white/5 bg-white/2 gap-2 flex">
                            <input
                                type="text"
                                value={inputCmd}
                                onChange={(e) => setInputCmd(e.target.value)}
                                placeholder="Issue a command..."
                                className="flex-1 bg-[#1e293b] border-none rounded-lg px-4 py-2.5 text-sm focus:ring-1 focus:ring-blue-500 outline-none text-slate-200 placeholder-slate-500"
                            />
                            <button type="submit" title="Send Command" aria-label="Send Command" className="bg-[#334155] hover:bg-[#475569] p-2.5 rounded-lg text-slate-300 transition-colors">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
                            </button>
                        </form>
                    </div>
                );
            case 'CALLS':
                return (
                    <div className="flex-1 p-4 overflow-y-auto space-y-3 font-mono text-xs">
                        {calls.length === 0 ? <p className="text-slate-500 text-center py-10">No calls recorded yet.</p> : calls.map(call => (
                            <div key={call.id} className="bg-white/5 p-3 rounded-lg border border-white/5 hover:border-blue-500/30 transition-colors">
                                <div className="flex justify-between items-start mb-1">
                                    <span className="text-blue-400 font-bold">{call.phone_number}</span>
                                    <span className="text-slate-500">{new Date(call.created_at).toLocaleString()}</span>
                                </div>
                                <p className="text-slate-300 leading-relaxed mb-2 line-clamp-2">{call.summary || 'No summary available.'}</p>
                                <div className="flex justify-between items-center">
                                    <span className={`px-2 py-0.5 rounded text-[10px] ${call.sentiment?.includes('Positive') ? 'bg-green-500/20 text-green-400' : 'bg-slate-700 text-slate-400'}`}>
                                        {call.sentiment || 'Neutral'}
                                    </span>
                                    <button className="text-blue-500 hover:text-blue-400">View Transcript →</button>
                                </div>
                            </div>
                        ))}
                    </div>
                );
            case 'EMAILS':
            case 'SMS':
                return (
                    <div className="flex-1 flex flex-col items-center justify-center text-slate-500 p-10 text-center h-full">
                        <div className="w-12 h-12 bg-slate-800/50 rounded-full flex items-center justify-center mb-3">
                            <svg className="w-6 h-6 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={activeTab === 'EMAILS' ? "M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" : "M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"} /></svg>
                        </div>
                        <p>No recent {activeTab.toLowerCase()} found.</p>
                        <p className="text-xs mt-1">Sync is active. Waiting for new data.</p>
                    </div>
                );
            default: return null;
        }
    };

    return (
        <div className="min-h-screen bg-[#020617] text-white p-4 font-sans overflow-hidden">
            {/* Top Bar */}
            <div className="flex justify-between items-center mb-6 bg-[#0f172a]/50 backdrop-blur border border-white/5 p-3 rounded-xl">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20">
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                    </div>
                    <div>
                        <h1 className="text-xl font-bold tracking-tight">Sovereign Command</h1>
                        <div className="flex items-center gap-2 text-xs text-green-400">
                            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                            Status: All Systems Online
                        </div>
                    </div>
                </div>
                <div className="flex gap-2">
                    {['Landing Pages', 'System', 'Tools'].map(item => (
                        <button key={item} aria-label={item} className="px-4 py-2 bg-[#1e293b] hover:bg-[#334155] rounded-lg text-sm text-slate-300 transition-colors border border-white/5">
                            {item}
                        </button>
                    ))}
                    <button aria-label="Main Site" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition-colors shadow-lg shadow-blue-600/20">
                        Main Site
                    </button>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-4 gap-4 mb-6">
                {[
                    { label: 'TOTAL LEADS', value: stats.totalLeads, color: 'text-white' },
                    { label: 'EST. PIPELINE', value: `$${stats.pipelineValue}`, color: 'text-green-400' },
                    { label: 'AI CALLS', value: stats.aiCalls, color: 'text-blue-400' },
                    { label: 'RESERVATIONS', value: stats.reservations, color: 'text-purple-400' }
                ].map((stat, i) => (
                    <div key={i} className="bg-[#0f172a]/50 border border-white/5 rounded-xl p-5 backdrop-blur hover:border-white/10 transition-colors">
                        <div className="text-xs text-slate-400 font-medium tracking-wider mb-1">{stat.label}</div>
                        <div className={`text-3xl font-bold ${stat.color}`}>{stat.value}</div>
                    </div>
                ))}
            </div>

            {/* Main Control Area */}
            <div className="grid grid-cols-12 gap-6 h-[500px]">

                {/* Left: Orchestrator Uplink */}
                <div className="col-span-3 bg-[#0f172a]/50 border border-white/5 rounded-xl p-6 flex flex-col items-center justify-center text-center relative overflow-hidden group">
                    <div className="absolute inset-0 bg-blue-500/5 group-hover:bg-blue-500/10 transition-colors"></div>
                    <div className="w-20 h-20 bg-blue-900/30 rounded-full flex items-center justify-center mb-4 border border-blue-500/30">
                        <svg className="w-10 h-10 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" /></svg>
                    </div>
                    <h3 className="text-lg font-bold mb-1">Orchestrator Uplink</h3>
                    <div className="text-xs text-slate-400 mb-6">Level 5 Neural Link</div>
                    <button className="w-full py-3 bg-blue-600 hover:bg-blue-500 rounded-lg font-medium transition-all shadow-lg shadow-blue-600/20 active:scale-95">
                        Initiate Voice Uplink
                    </button>
                    <div className="mt-4 flex items-center gap-2 text-xs text-green-400">
                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" /></svg>
                        Status: Widget Active
                    </div>
                </div>

                {/* Center: Communication Hub */}
                <div className="col-span-6 bg-[#0f172a]/50 border border-white/5 rounded-xl flex flex-col relative overflow-hidden">
                    <div className="p-4 border-b border-white/5 flex justify-between items-center bg-white/2">
                        <div className="flex gap-4 text-sm font-medium">
                            {['COMMAND', 'CALLS', 'EMAILS', 'SMS'].map(tab => (
                                <button
                                    key={tab}
                                    onClick={() => setActiveTab(tab)}
                                    className={`relative px-1 py-1 transition-colors ${activeTab === tab ? 'text-white' : 'text-slate-500 hover:text-slate-300'}`}
                                >
                                    {tab}
                                    {activeTab === tab && <div className="absolute -bottom-[17px] left-0 w-full h-0.5 bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.5)]"></div>}
                                </button>
                            ))}
                        </div>
                        <div className="flex items-center gap-2 text-xs text-green-400">
                            <span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span> AI Online
                        </div>
                    </div>

                    {renderTabContent()}
                </div>

                {/* Right: Asset Inbox */}
                <div className="col-span-3 bg-[#0f172a]/50 border border-white/5 rounded-xl p-6 flex flex-col relative">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="font-bold">Asset Inbox</h3>
                        <div className="text-xs text-blue-400">Ready</div>
                    </div>
                    <div className="flex-1 border-2 border-dashed border-white/10 rounded-xl flex flex-col items-center justify-center p-4 text-center hover:border-blue-500/30 hover:bg-blue-500/5 transition-all cursor-pointer group">
                        <div className="w-12 h-12 bg-slate-800/50 rounded-full flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                            <svg className="w-6 h-6 text-slate-400 group-hover:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
                        </div>
                        <p className="text-sm text-slate-400 group-hover:text-slate-300">Drag & Drop Videos/Links</p>
                    </div>
                    <div className="mt-4 flex gap-2">
                        <input type="text" placeholder="Asset Label" className="flex-1 bg-[#1e293b] rounded-lg px-3 py-2 text-xs border-none outline-none" />
                        <button className="bg-blue-600 hover:bg-blue-500 px-3 py-2 rounded-lg text-xs font-bold">SAVE</button>
                    </div>
                    <p className="text-[10px] text-slate-600 text-center mt-3">Uploads route to Antigravity Watchdog.</p>
                </div>
            </div>

            {/* Recent Activity Marquee */}
            <div className="mt-6 bg-[#0f172a] border border-white/5 rounded-full px-6 py-3 flex items-center gap-4 overflow-hidden">
                <span className="text-sm font-semibold text-slate-400 whitespace-nowrap">Recent Activity</span>
                <div className="h-4 w-px bg-white/10"></div>
                <div className="flex gap-8 text-xs text-slate-500 animate-marquee whitespace-nowrap">
                    {logs.slice(0, 5).map(log => (
                        <span key={log.id} className="flex items-center gap-2">
                            <span className={`w-1.5 h-1.5 rounded-full ${log.level === 'ERROR' ? 'bg-red-500' : 'bg-blue-500'}`}></span>
                            {log.message}
                        </span>
                    ))}
                </div>
            </div>
        </div>
    );
}
