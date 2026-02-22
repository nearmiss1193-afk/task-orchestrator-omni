"use client";

import { useState } from "react";
import { Terminal, ShieldAlert, Send, Loader2 } from "lucide-react";

interface LogMessage {
    id: string;
    sender: 'user' | 'system';
    text: string;
    timestamp: Date;
    isError?: boolean;
}

export function OverrideConsole() {
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [logs, setLogs] = useState<LogMessage[]>([
        {
            id: 'init',
            sender: 'system',
            text: 'Sovereign Commlink Online. Awaiting PIN-secured command injection.',
            timestamp: new Date()
        }
    ]);

    const executeOverride = async (e: React.FormEvent) => {
        e.preventDefault();
        const payload = input.trim();
        if (!payload) return;

        setInput("");

        // Add User Log
        setLogs(prev => [...prev, {
            id: Date.now().toString(),
            sender: 'user',
            text: payload,
            timestamp: new Date()
        }]);

        setIsLoading(true);

        try {
            const res = await fetch('/api/c2-override', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: payload })
            });

            const data = await res.json();

            setLogs(prev => [...prev, {
                id: (Date.now() + 1).toString(),
                sender: 'system',
                text: data.message || (res.ok ? "Command Executed Successfully." : "Command Rejected."),
                timestamp: new Date(),
                isError: !res.ok
            }]);

        } catch (err) {
            setLogs(prev => [...prev, {
                id: (Date.now() + 1).toString(),
                sender: 'system',
                text: "Fatal Error: Unable to reach Command Edge Route.",
                timestamp: new Date(),
                isError: true
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="bg-zinc-950 border border-red-500/20 rounded-xl overflow-hidden shadow-2xl flex flex-col h-[400px]">
            {/* Header */}
            <div className="bg-red-950/30 border-b border-red-500/20 p-3 shrink-0 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <ShieldAlert className="w-5 h-5 text-red-500" />
                    <h3 className="font-mono font-bold text-red-500 uppercase tracking-widest text-sm text-[11px] sm:text-sm">
                        Global Override Console
                    </h3>
                </div>
                <div className="flex items-center gap-2 px-2 py-1 bg-red-500/10 rounded border border-red-500/20">
                    <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
                    <span className="text-[10px] text-red-400 font-mono uppercase tracking-widest leading-none">
                        AUTH: PIN REQUIRED
                    </span>
                </div>
            </div>

            {/* Terminal Window */}
            <div className="flex-1 overflow-y-auto p-4 bg-zinc-950 font-mono text-sm space-y-2">
                {logs.map(log => (
                    <div key={log.id} className={`flex flex-col gap-1 ${log.sender === 'user' ? 'opacity-70' : ''}`}>
                        <div className="flex items-center gap-2 text-[10px] text-zinc-500">
                            <span>[{log.timestamp.toLocaleTimeString()}]</span>
                            <span className="uppercase">{log.sender}</span>
                        </div>
                        <div className={`break-words ${log.sender === 'user' ? 'text-zinc-300'
                                : log.isError ? 'text-red-400 font-bold'
                                    : 'text-emerald-400'
                            }`}>
                            {log.sender === 'user' ? '> ' + log.text : log.text}
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex items-center gap-2 text-[10px] text-zinc-500 mt-4">
                        <Loader2 className="w-3 h-3 animate-spin text-red-500" />
                        <span>AUTHENTICATING PAYLOAD...</span>
                    </div>
                )}
            </div>

            {/* Input Bar */}
            <form onSubmit={executeOverride} className="p-3 border-t border-red-500/20 bg-zinc-900 flex gap-2">
                <div className="relative flex-1">
                    <Terminal className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="e.g. 1175: Halt Campaigns"
                        className="w-full bg-zinc-950 border border-zinc-800 rounded px-10 py-2.5 text-sm font-mono text-emerald-400 focus:outline-none focus:border-red-500/50 focus:ring-1 focus:ring-red-500/50 transition-all placeholder:text-zinc-600"
                        disabled={isLoading}
                    />
                </div>
                <button
                    type="submit"
                    disabled={isLoading || !input.trim()}
                    className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded font-mono font-bold text-xs uppercase tracking-wider transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center shrink-0"
                >
                    <Send className="w-4 h-4" />
                </button>
            </form>
        </div>
    );
}
