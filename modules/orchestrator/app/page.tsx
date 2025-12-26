"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import { Plan, ExecutionLog, Step } from "@/lib/types";
import Profile from "@/components/Profile";
import LogoutButton from "@/components/LogoutButton";

export default function Home() {
    const [instruction, setInstruction] = useState("Build me a landing page complete with contact payment widget embeds in my funnels section, find leads from plumbers in Florida, email them, and report performance.");
    const [plan, setPlan] = useState<Plan | null>(null);
    const [logs, setLogs] = useState<ExecutionLog[]>([]);
    const [loading, setLoading] = useState(false);
    const [executing, setExecuting] = useState(false);

    const handleCreatePlan = async () => {
        setLoading(true);
        try {
            const res = await axios.post("/api/agent/plan", { instruction });
            setPlan(res.data);
            setLogs([]);
        } catch (err) {
            alert("Failed to create plan");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleExecute = async () => {
        if (!plan) return;
        setExecuting(true);
        try {
            await axios.post("/api/agent/execute", { planId: plan.id });
        } catch (err) {
            alert("Failed to start execution");
            setExecuting(false);
        }
    };

    useEffect(() => {
        let interval: NodeJS.Timeout;
        if (plan && (executing || plan.status === 'RUNNING')) {
            interval = setInterval(async () => {
                try {
                    const res = await axios.get(`/api/agent/status?planId=${plan.id}`);
                    const updatedPlan: Plan = res.data.plan;
                    setPlan(updatedPlan);
                    setLogs(res.data.logs);

                    if (updatedPlan.status === 'COMPLETED' || updatedPlan.status === 'FAILED') {
                        setExecuting(false);
                        clearInterval(interval);
                    }
                } catch (err) {
                    console.error("Polling error", err);
                }
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [plan, executing]);

    return (
        <main className="flex min-h-screen flex-col bg-black text-cyan-500 font-mono selection:bg-cyan-900 selection:text-white overflow-hidden">
            {/* Background Grid */}
            <div className="fixed inset-0 z-0 opacity-20 pointer-events-none bg-grid-tech">
            </div>

            {/* Header */}
            <div className="z-10 w-full flex items-center justify-between p-6 border-b border-cyan-900/50 bg-black/80 backdrop-blur-md">
                <div className="flex items-center gap-4">
                    <div className="w-8 h-8 bg-cyan-500 rounded-sm animate-pulse shadow-[0_0_15px_rgba(6,182,212,0.8)]"></div>
                    <h1 className="text-2xl font-bold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-500">
                        CORTEX ORCHESTRATOR <span className="text-xs text-gray-500 align-top ml-2">v2.0</span>
                    </h1>
                </div>
                <div className="flex items-center gap-6">
                    <Profile />
                    <LogoutButton />
                </div>
            </div>

            <div className="z-10 grid grid-cols-1 lg:grid-cols-12 gap-6 p-8 h-[calc(100vh-80px)]">

                {/* LEFT: COMMAND CENTER */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    {/* Input Area */}
                    <div className="bg-gray-900/50 border border-cyan-900/50 rounded-none p-1 relative group hover:border-cyan-500/50 transition-colors">
                        <div className="absolute -top-1 -left-1 w-2 h-2 border-t border-l border-cyan-500"></div>
                        <div className="absolute -bottom-1 -right-1 w-2 h-2 border-b border-r border-cyan-500"></div>

                        <div className="bg-black p-5 h-full flex flex-col gap-4">
                            <h2 className="text-sm font-bold text-cyan-400 uppercase tracking-widest mb-2 flex justify-between">
                                <span>1. Mission Parameters</span>
                                <span className="text-[10px] text-gray-600">INPUT_STREAM_Active</span>
                            </h2>
                            <textarea
                                className="w-full h-40 bg-gray-900/30 border border-gray-800 text-gray-300 p-4 text-sm focus:outline-none focus:border-cyan-600 focus:bg-gray-900/80 transition-all font-mono resize-none"
                                value={instruction}
                                onChange={(e) => setInstruction(e.target.value)}
                                placeholder="> Enter directive..."
                            />
                            <button
                                onClick={handleCreatePlan}
                                disabled={loading || executing}
                                className="relative w-full overflow-hidden group bg-cyan-900/20 hover:bg-cyan-900/40 border border-cyan-800 text-cyan-400 py-4 font-bold uppercase tracking-widest transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <span className="relative z-10 flex items-center justify-center gap-2">
                                    {loading ? <span className="animate-spin">⟳</span> : "Initialize Plan"}
                                </span>
                                <div className="absolute inset-0 bg-cyan-500/10 transform -skew-x-[20deg] -translate-x-full group-hover:translate-x-full transition-transform duration-500"></div>
                            </button>
                        </div>
                    </div>

                    {/* Idea Assistant (Compact) */}
                    <div className="flex-grow flex flex-col bg-gray-900/50 border border-purple-900/30 p-1">
                        <IdeaAssistant />
                    </div>
                </div>

                {/* CENTER: EXECUTION FEED */}
                <div className="lg:col-span-5 flex flex-col gap-6 h-full overflow-hidden relative">
                    <div className="absolute top-0 left-0 w-full h-8 bg-gradient-to-b from-black to-transparent z-10"></div>
                    <div className="bg-gray-900/30 border-x border-cyan-900/30 h-full p-4 overflow-y-auto custom-scrollbar">
                        <h2 className="text-sm font-bold text-cyan-400 uppercase tracking-widest mb-6 sticky top-0 bg-black/90 p-2 backdrop-blur z-20 border-b border-cyan-900/30 flex justify-between items-center">
                            <span>2. Execution Sequence</span>
                            {plan && <span className={`text-[10px] px-2 py-1 ${plan.status === 'RUNNING' ? 'bg-cyan-900 text-cyan-200 animate-pulse' : 'bg-gray-800 text-gray-500'}`}>{plan.status}</span>}
                        </h2>

                        {!plan ? (
                            <div className="h-full flex items-center justify-center text-gray-700 text-xs uppercase tracking-widest">
                                [ No Active Sequence ]
                            </div>
                        ) : (
                            <div className="space-y-4 pb-20">
                                {plan.steps.map((step, idx) => (
                                    <div key={step.id} className="relative pl-6 border-l border-gray-800 hover:border-cyan-700 transition-colors group">
                                        <div className={`absolute -left-[5px] top-6 w-2 h-2 rounded-full ${step.status === 'COMPLETED' ? 'bg-green-500 shadow-[0_0_10px_lime]' :
                                            step.status === 'RUNNING' ? 'bg-cyan-500 animate-ping' :
                                                step.status === 'FAILED' ? 'bg-red-500' : 'bg-gray-800'
                                            }`}></div>
                                        <StepCard step={step} index={idx} />
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Action Bar */}
                    <div className="absolute bottom-4 left-4 right-4">
                        {plan && (
                            <button
                                onClick={handleExecute}
                                disabled={executing || plan.status === 'RUNNING' || plan.status === 'COMPLETED'}
                                className={`w-full py-4 font-bold uppercase tracking-widest shadow-2xl transition-all clip-corner ${executing ? 'bg-gray-800 text-cyan-500 cursor-wait' :
                                    plan.status === 'COMPLETED' ? 'bg-green-900/50 text-green-400 border border-green-700' :
                                        'bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-black'
                                    }`}
                            >
                                {executing ? ">> EXECUTING SEQUENCE <<" : plan.status === 'COMPLETED' ? "MISSION ACCOMPLISHED" : "ENGAGE SYSTEMS"}
                            </button>
                        )}
                    </div>
                </div>

                {/* RIGHT: DATA STREAM */}
                <div className="lg:col-span-3 flex flex-col bg-black border border-gray-800 relative overflow-hidden">
                    <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>
                    <div className="p-4 border-b border-gray-800 bg-gray-900/50 flex justify-between items-center">
                        <h2 className="text-xs font-bold text-green-500 uppercase tracking-widest">3. System Telemetry</h2>
                        <div className="flex gap-1">
                            <div className="w-1 h-3 bg-green-500"></div>
                            <div className="w-1 h-3 bg-green-600"></div>
                            <div className="w-1 h-3 bg-green-700"></div>
                        </div>
                    </div>
                    <div className="flex-grow p-4 font-mono text-[10px] text-green-400/80 overflow-y-auto space-y-1 custom-scrollbar">
                        {logs.length === 0 ? <span className="opacity-30">Waiting for datastream...</span> : logs.map(log => (
                            <div key={log.id} className="border-b border-white/5 pb-1 mb-1 opacity-80 hover:opacity-100 transition-opacity">
                                <span className="text-gray-500 mr-2">[{new Date(log.timestamp).toLocaleTimeString().split(' ')[0]}]</span>
                                {log.message.includes('OVERSEER') ? (
                                    <span className="text-purple-400 font-bold">{log.message}</span>
                                ) : log.level === 'error' ? (
                                    <span className="text-red-500 font-bold bg-red-900/20 px-1">{log.message}</span>
                                ) : (
                                    <span>{log.message}</span>
                                )}
                            </div>
                        ))}
                        <div ref={(el) => el?.scrollIntoView({ behavior: 'smooth' })} />
                    </div>
                </div>
            </div>
        </main>
    );
}

function IdeaAssistant() {
    // ... (Keep existing Logic but update styles to match Cyberpunk)
    // For brevity in this tool call, I'll rely on the existing component if available or assume I need to restyle it too.
    // Ideally I would rewrite it here to fit the theme.
    // Let's assume I need to rewrite it to be safe.

    const [input, setInput] = useState("");
    const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string }[]>([]);
    const [loading, setLoading] = useState(false);

    const handleSend = async () => {
        if (!input.trim()) return;
        const newMsgs = [...messages, { role: 'user' as const, content: input }];
        setMessages(newMsgs);
        setInput("");
        setLoading(true);

        try {
            const res = await axios.post('/api/agent/chat', { messages: newMsgs });
            setMessages([...newMsgs, { role: 'assistant', content: res.data.reply }]);
        } catch (err) {
            setMessages([...newMsgs, { role: 'assistant', content: "Error: Could not fetch response." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="h-full flex flex-col bg-black p-4">
            <h3 className="text-xs font-bold text-purple-400 mb-2 uppercase tracking-widest">Neural Link</h3>
            <div className="flex-grow overflow-y-auto space-y-2 mb-2 pr-1 custom-scrollbar">
                {messages.map((m, i) => (
                    <div key={i} className={`p-2 rounded-sm text-xs ${m.role === 'user' ? 'bg-cyan-900/20 text-cyan-200 border-l-2 border-cyan-500' : 'bg-purple-900/20 text-purple-200 border-r-2 border-purple-500 text-right'}`}>
                        {m.content}
                    </div>
                ))}
                {loading && <div className="text-[10px] text-gray-500 animate-pulse">Computing...</div>}
            </div>
            <div className="flex border border-gray-700 bg-gray-900">
                <input
                    className="flex-grow bg-transparent p-2 text-xs text-white focus:outline-none"
                    placeholder="Query Neural Net..."
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleSend()}
                />
                <button onClick={handleSend} disabled={loading} className="px-3 bg-purple-900/50 text-purple-400 hover:bg-purple-800/80 transition-colors">►</button>
            </div>
        </div>
    )
}

function StepCard({ step, index }: { step: Step, index: number }) {
    return (
        <div className={`bg-gray-900/40 p-4 border border-gray-800 ${step.status === 'RUNNING' ? 'border-cyan-500/50 shadow-[0_0_20px_rgba(6,182,212,0.1)]' : ''}`}>
            <div className="flex justify-between items-start mb-2">
                <div className="flex flex-col">
                    <span className="text-[10px] text-gray-600 uppercase tracking-widest mb-1">SEQ_0{index + 1} // {step.connectorName}</span>
                    <h4 className="text-sm font-bold text-gray-200">{step.action.toUpperCase()}</h4>
                </div>
                <StatusBadge status={step.status} />
            </div>
            {step.error && (
                <div className="mt-2 p-2 bg-red-900/20 border-l-2 border-red-500 text-[10px] text-red-300 font-mono">
                    ERR: {step.error}
                </div>
            )}
            {step.result && (
                <div className="mt-2 p-2 bg-green-900/10 border-l-2 border-green-500 text-[10px] text-green-300 font-mono overflow-hidden whitespace-nowrap text-ellipsis">
                    OUT: {JSON.stringify(step.result)}
                </div>
            )}
        </div>
    )
}

function formatActionName(action: string) {
    return action.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

function StatusBadge({ status }: { status: string }) {
    const colors = {
        PENDING: "text-gray-600",
        RUNNING: "text-cyan-400",
        COMPLETED: "text-green-400",
        FAILED: "text-red-500"
    };
    return <span className={`text-[10px] font-bold tracking-widest uppercase ${colors[status as keyof typeof colors] || 'text-gray-600'}`}>{status}</span>
}
