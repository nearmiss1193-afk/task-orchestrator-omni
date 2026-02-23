"use client";
import { ChatInterface } from "@/components/chat-interface";
import { CRMView } from "@/components/crm-view";
import { VerificationQueue } from "@/components/verification-queue";
import { OverrideConsole } from "@/components/override-console";
import { Shield, Radio, LayoutDashboard, Settings, UserCircle, Mail, PieChart, Mic, Share2 } from "lucide-react";
import React from "react";
import Link from "next/link";

export default function Home() {
    const [currentView, setCurrentView] = React.useState('command');
    const [stats, setStats] = React.useState({
        active_agents: "-",
        system_load: "-",
        network: "Connecting...",
        notifications: "-"
    });

    React.useEffect(() => {
        const fetchStats = () => {
            fetch('/api/status')
                .then(res => res.json())
                .then(data => {
                    setStats({
                        active_agents: data.active_agents.toString(),
                        system_load: data.system_load,
                        network: data.network_status,
                        notifications: data.notifications.toString()
                    });
                })
                .catch(err => console.error("Stats Fetch Failed:", err));
        }
        fetchStats();
        // Poll every 5 seconds for live traffic updates
        const interval = setInterval(fetchStats, 5000);
        return () => clearInterval(interval);
    }, []);

    const renderContent = () => {
        switch (currentView) {
            case 'communications':
                return <CRMView />;
            case 'personnel':
                return (
                    <div className="flex flex-col gap-6">
                        <h2 className="text-3xl font-bold text-white">Active Agents</h2>
                        <div className="p-6 bg-zinc-900/50 border border-white/10 rounded-xl">
                            <ul className="space-y-3">
                                <li className="flex justify-between border-b border-white/5 pb-2"><span>Cooling Cal (HVAC)</span> <span className="text-green-500">Live</span></li>
                                <li className="flex justify-between border-b border-white/5 pb-2"><span>Dispatch Dan (Plumber)</span> <span className="text-green-500">Live</span></li>
                                <li className="flex justify-between border-b border-white/5 pb-2"><span>Estimator Eric (Roofer)</span> <span className="text-green-500">Live</span></li>
                                <li className="flex justify-between border-b border-white/5 pb-2"><span>Electrician Ellie</span> <span className="text-green-500">Live</span></li>
                            </ul>
                        </div>
                    </div>
                );
            case 'settings':
                return (
                    <div className="flex flex-col gap-6">
                        <h2 className="text-3xl font-bold text-white">System Settings</h2>
                        <div className="p-6 bg-zinc-900/50 border border-white/10 rounded-xl">
                            <p className="text-zinc-400">Mode: <span className="text-white font-mono">SOVEREIGN_LIVE</span></p>
                            <p className="text-zinc-400">Host: <span className="text-white font-mono">localhost:3000</span></p>
                            <p className="text-zinc-400">Version: <span className="text-white font-mono">v45.0</span></p>
                        </div>
                    </div>
                );
            default: // Command
                return (
                    <div className="flex flex-col justify-center gap-6">
                        <div>
                            <h2 className="text-5xl font-bold tracking-tight mb-2 bg-gradient-to-br from-white to-zinc-500 bg-clip-text text-transparent">
                                Welcome to Empire
                            </h2>
                            <p className="text-zinc-400 text-lg max-w-md">
                                Your autonomous operations center. Call your office manager or chat with the concierge below.
                            </p>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <StatusCard label="Active Agents" value={stats.active_agents} />
                            <StatusCard label="System Load" value={stats.system_load} />
                            <StatusCard label="Network" value={stats.network} />
                            <StatusCard label="Notifications" value={stats.notifications} />
                        </div>

                        {/* Phase 10 matrices */}
                        <div className="mt-4 grid grid-cols-1 lg:grid-cols-2 gap-4">
                            <VerificationQueue />
                            <OverrideConsole />
                        </div>
                    </div>
                );
        }
    }

    return (
        <main className="flex min-h-screen bg-[#0a0a0a] text-white selection:bg-blue-500/30">
            {/* Sidebar Navigation */}
            <aside className="w-20 lg:w-64 border-r border-white/10 flex flex-col items-center lg:items-stretch py-8 bg-[#0f0f0f]">
                <div className="mb-12 px-4 flex items-center justify-center lg:justify-start gap-3">
                    <Shield className="w-8 h-8 text-blue-500" />
                    <span className="hidden lg:block font-bold text-xl tracking-wider">EMPIRE</span>
                </div>

                <nav className="flex-1 flex flex-col gap-2 px-2">
                    <NavItem icon={<LayoutDashboard />} label="Command" active={currentView === 'command'} onClick={() => setCurrentView('command')} />
                    <NavItem icon={<Radio />} label="Communications" active={currentView === 'communications'} onClick={() => setCurrentView('communications')} />
                    <Link href="/inbox" className={`flex items-center gap-3 p-3 rounded-xl transition-all text-indigo-400 hover:bg-white/5 hover:text-indigo-300 bg-indigo-500/10 border border-indigo-500/20 mt-1`}>
                        <Mail className="w-6 h-6" />
                        <span className="hidden lg:block font-medium">Omni-Channel Inbox</span>
                    </Link>
                    <Link href="/campaigns" className={`flex items-center gap-3 p-3 rounded-xl transition-all text-emerald-400 hover:bg-white/5 hover:text-emerald-300 bg-emerald-500/10 border border-emerald-500/20 mt-1`}>
                        <PieChart className="w-6 h-6" />
                        <span className="hidden lg:block font-medium">Campaign Triage</span>
                    </Link>
                    <Link href="/voice" className={`flex items-center gap-3 p-3 rounded-xl transition-all text-fuchsia-400 hover:bg-white/5 hover:text-fuchsia-300 bg-fuchsia-500/10 border border-fuchsia-500/20 mt-1`}>
                        <Mic className="w-6 h-6" />
                        <span className="hidden lg:block font-medium">Voice Transcripts</span>
                    </Link>
                    <Link href="/social" className={`flex items-center gap-3 p-3 rounded-xl transition-all text-sky-400 hover:bg-white/5 hover:text-sky-300 bg-sky-500/10 border border-sky-500/20 mt-1`}>
                        <Share2 className="w-6 h-6" />
                        <span className="hidden lg:block font-medium">Social Queue</span>
                    </Link>
                    <NavItem icon={<UserCircle />} label="Personnel" active={currentView === 'personnel'} onClick={() => setCurrentView('personnel')} />

                    <div className="mt-4 pt-4 border-t border-white/10 px-2 flex flex-col gap-2">
                        <span className="text-xs text-zinc-500 font-bold px-2 uppercase tracking-wider mb-1">AI Services</span>
                        <Link href="/ai-secretary" className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-zinc-400 hover:text-white hover:bg-white/5 transition-colors">
                            🤖 AI Secretary
                        </Link>
                        <Link href="/automation-workflows" className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-zinc-400 hover:text-white hover:bg-white/5 transition-colors">
                            ⚡ Workflows
                        </Link>
                        <Link href="/custom-ai-solutions" className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-zinc-400 hover:text-white hover:bg-white/5 transition-colors">
                            ⚙️ Custom AI
                        </Link>
                    </div>

                    <div className="mt-4 pt-4 border-t border-white/10 px-2 flex flex-col gap-2">
                        <span className="text-xs text-zinc-500 font-bold px-2 uppercase tracking-wider mb-1">Local Directory</span>
                        <Link href="/lakeland/plumbers" className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-amber-500 hover:text-amber-400 hover:bg-white/5 transition-colors bg-amber-900/10 border border-amber-500/20">
                            🌴 Lakeland Finds
                        </Link>
                        <Link href="/bids" className="flex items-center justify-between px-3 py-2 rounded-lg text-sm font-bold text-emerald-400 bg-emerald-900/10 border border-emerald-500/20 hover:bg-emerald-900/30 transition-colors">
                            <div className="flex items-center gap-3">
                                🏛️ Lakeland Bid-Bot
                            </div>
                        </Link>
                        <Link href="/intents" className="flex items-center justify-between px-3 py-2 rounded-lg text-sm font-bold text-violet-400 bg-violet-900/10 border border-violet-500/20 hover:bg-violet-900/30 transition-colors mt-1">
                            <div className="flex items-center gap-3">
                                🎯 Intent Engine
                            </div>
                        </Link>
                    </div>

                    <div className="mt-4 pt-4 border-t border-white/10 px-2 flex flex-col gap-2">
                        <span className="text-xs text-zinc-500 font-bold px-2 uppercase tracking-wider mb-1">Growth</span>
                        <Link href="/assessment" className="flex items-center justify-between px-3 py-2 rounded-lg text-sm font-bold text-blue-400 bg-blue-900/10 border border-blue-500/20 hover:bg-blue-900/30 transition-colors">
                            <div className="flex items-center gap-3">
                                📈 AI Readiness Score
                            </div>
                        </Link>
                    </div>

                    <div className="mt-auto">
                        <NavItem icon={<Settings />} label="Settings" active={currentView === 'settings'} onClick={() => setCurrentView('settings')} />
                    </div>
                </nav>

                <div className="px-4 py-4 border-t border-white/10">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-500 to-purple-500" />
                        <div className="hidden lg:block">
                            <p className="text-sm font-medium">Verified User</p>
                            <p className="text-xs text-zinc-500">Level 5 Authority</p>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col relative overflow-hidden">

                {/* Background Ambient Glow */}
                <div className="absolute top-[-50%] left-[-10%] w-[1000px] h-[1000px] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[800px] h-[800px] bg-purple-600/5 rounded-full blur-[100px] pointer-events-none" />

                <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-[#0a0a0a]/50 backdrop-blur-md z-10">
                    <h1 className="text-lg font-medium text-zinc-300">Operations / {currentView.charAt(0).toUpperCase() + currentView.slice(1)}</h1>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                        <span className="text-xs text-green-500 font-mono">SYSTEM ONLINE</span>
                    </div>
                </header>

                <div className="flex-1 p-8 grid lg:grid-cols-2 gap-8 z-0">
                    {/* Left Column: Dynamic Content based on View */}
                    <div className="flex flex-col justify-center gap-6 relative">
                        {renderContent()}
                    </div>

                    {/* Right Column: Chat Interface (Always Visible) */}
                    <div className="h-full max-h-[700px] flex flex-col">
                        <div className="flex-1 bg-zinc-900/50 border border-white/10 rounded-2xl shadow-2xl overflow-hidden backdrop-blur-sm">
                            <ChatInterface />
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}

function NavItem({ icon, label, active = false, onClick }: { icon: React.ReactNode, label: string, active?: boolean, onClick: () => void }) {
    return (
        <button
            onClick={onClick}
            className={`flex items-center gap-3 p-3 rounded-xl transition-all ${active ? 'bg-blue-600/10 text-blue-400' : 'text-zinc-400 hover:bg-white/5 hover:text-white'}`}
        >
            {icon}
            <span className="hidden lg:block font-medium">{label}</span>
        </button>
    );
}

function StatusCard({ label, value }: { label: string, value: string }) {
    return (
        <div className="p-4 rounded-xl border border-white/5 bg-white/5 hover:bg-white/10 transition-colors">
            <p className="text-zinc-500 text-xs uppercase tracking-wider mb-1">{label}</p>
            <p className="text-xl font-mono text-white">{value}</p>
        </div>
    );
}
