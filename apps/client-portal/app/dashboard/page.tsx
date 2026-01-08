'use client';

import { useEffect, useState } from 'react';
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
        totalCalls: 0,
        leadsToday: 0,
        systemHealth: 'CHECKING...'
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();

        // Set up real-time subscription
        const logsChannel = supabase
            .channel('logs-channel')
            .on('postgres_changes', {
                event: 'INSERT',
                schema: 'public',
                table: 'system_logs'
            }, (payload) => {
                setLogs((prev) => [payload.new as SystemLog, ...prev].slice(0, 50));
            })
            .subscribe();

        return () => {
            supabase.removeChannel(logsChannel);
        };
    }, []);

    async function fetchData() {
        setLoading(true);

        // Fetch recent logs
        const { data: logsData } = await supabase
            .from('system_logs')
            .select('*')
            .order('created_at', { ascending: false })
            .limit(50);

        // Fetch recent calls
        const { data: callsData } = await supabase
            .from('call_transcripts')
            .select('*')
            .order('created_at', { ascending: false })
            .limit(20);

        // Calculate stats
        const today = new Date().toISOString().split('T')[0];
        const leadsToday = logsData?.filter(
            (log: SystemLog) => log.level === 'LEAD' && log.created_at.startsWith(today)
        ).length || 0;

        setLogs(logsData || []);
        setCalls(callsData || []);
        setStats({
            totalCalls: callsData?.length || 0,
            leadsToday,
            systemHealth: 'OPERATIONAL'
        });
        setLoading(false);
    }

    const getLevelColor = (level: string) => {
        switch (level) {
            case 'ERROR': return 'text-red-400';
            case 'WARNING': return 'text-yellow-400';
            case 'LEAD': return 'text-green-400';
            case 'INFO': return 'text-blue-400';
            default: return 'text-slate-400';
        }
    };

    const getSentimentEmoji = (sentiment: string) => {
        if (!sentiment) return '❓';
        if (sentiment.toLowerCase().includes('positive')) return '😊';
        if (sentiment.toLowerCase().includes('negative')) return '😠';
        return '😐';
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center">
                <div className="text-blue-400 text-xl animate-pulse">Loading Mission Control...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-950 to-black text-white p-6">
            {/* Header */}
            <header className="mb-8">
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                    🎯 Empire Mission Control
                </h1>
                <p className="text-slate-400 mt-1">AI Service Company Operations Hub</p>
            </header>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                    <div className="text-slate-400 text-sm">System Status</div>
                    <div className="text-2xl font-bold text-green-400 flex items-center gap-2">
                        <span className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></span>
                        {stats.systemHealth}
                    </div>
                </div>

                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                    <div className="text-slate-400 text-sm">Total Calls Logged</div>
                    <div className="text-2xl font-bold text-blue-400">{stats.totalCalls}</div>
                </div>

                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                    <div className="text-slate-400 text-sm">Leads Today</div>
                    <div className="text-2xl font-bold text-purple-400">{stats.leadsToday}</div>
                </div>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Live Logs */}
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                    <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                        📋 Live System Logs
                        <span className="text-xs bg-red-500 px-2 py-0.5 rounded-full animate-pulse">LIVE</span>
                    </h2>
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                        {logs.length === 0 ? (
                            <p className="text-slate-500">No logs yet...</p>
                        ) : (
                            logs.map((log) => (
                                <div key={log.id} className="text-sm border-b border-white/5 pb-2">
                                    <span className={`font-mono ${getLevelColor(log.level)}`}>
                                        [{log.level}]
                                    </span>{' '}
                                    <span className="text-slate-300">{log.message}</span>
                                    <div className="text-xs text-slate-500">
                                        {new Date(log.created_at).toLocaleString()}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Recent Calls */}
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                    <h2 className="text-xl font-semibold mb-4">📞 Recent Calls</h2>
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                        {calls.length === 0 ? (
                            <p className="text-slate-500">No calls recorded yet...</p>
                        ) : (
                            calls.map((call) => (
                                <div key={call.id} className="bg-white/5 rounded-lg p-3">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <div className="font-mono text-blue-300">{call.phone_number || 'Unknown'}</div>
                                            <div className="text-sm text-slate-400 mt-1">
                                                {call.summary?.slice(0, 100) || 'No summary'}...
                                            </div>
                                        </div>
                                        <div className="text-2xl">{getSentimentEmoji(call.sentiment)}</div>
                                    </div>
                                    <div className="text-xs text-slate-500 mt-2">
                                        {new Date(call.created_at).toLocaleString()}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>

            {/* Footer */}
            <footer className="mt-8 text-center text-slate-500 text-sm">
                Empire Unified v2 • Powered by Supabase + Vercel
            </footer>
        </div>
    );
}
