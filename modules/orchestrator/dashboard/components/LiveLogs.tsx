
'use client';

import { useEffect, useState, useRef } from 'react';
import { supabase } from '@/lib/supabase';
import { Terminal } from 'lucide-react';

interface LogEntry {
    id: number;
    created_at: string;
    message: string;
}

export default function LiveLogs() {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Initial Fetch
        const fetchLogs = async () => {
            const { data } = await supabase
                .from('brain_logs')
                .select('*')
                .order('created_at', { ascending: false })
                .limit(50);

            if (data && data.length > 0) {
                setLogs(data.reverse());
            } else {
                // Fallback for visual confirmation if DB is empty/missing
                setLogs([
                    { id: 1, created_at: new Date().toISOString(), message: "System Link Established..." },
                    { id: 2, created_at: new Date().toISOString(), message: "Waiting for Brain Logs..." }
                ]);
            }
        };

        fetchLogs();

        // Realtime Subscription
        const channel = supabase
            .channel('realtime logs')
            .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'brain_logs' }, (payload) => {
                setLogs((prev) => [...prev.slice(-49), payload.new as LogEntry]);
            })
            .subscribe();

        return () => {
            supabase.removeChannel(channel);
        };
    }, []);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    return (
        <div className="bg-black border border-green-900 rounded-lg p-4 font-mono text-xs h-96 flex flex-col shadow-[0_0_20px_rgba(0,255,0,0.1)]">
            <div className="flex items-center gap-2 mb-3 text-green-500 border-b border-green-900 pb-2">
                <Terminal size={14} />
                <span className="font-bold tracking-widest uppercase">Live Intelligence Feed</span>
                <div className="ml-auto w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            </div>

            <div className="flex-1 overflow-y-auto space-y-1 scrollbar-hide">
                {logs.map((log, i) => (
                    <div key={log.id || i} className="text-green-300/80 hover:text-green-300 transition-colors">
                        <span className="text-green-800 mr-2">
                            {new Date(log.created_at).toLocaleTimeString()}
                        </span>
                        {log.message}
                    </div>
                ))}
                <div ref={bottomRef} />
            </div>
        </div>
    );
}
