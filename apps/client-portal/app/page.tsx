'use client';

import { useEffect, useState, useRef } from 'react';
import { createClient } from '@supabase/supabase-js';

// Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://rzcpfwkygdvoshtwxncs.supabase.co';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
const supabase = supabaseKey ? createClient(supabaseUrl, supabaseKey) : null;

type Tab = 'overview' | 'dossier' | 'conversations' | 'emails' | 'sms' | 'brain' | 'pages' | 'chat';

// INTERFACES
interface EmailRecord {
    id: string;
    to: string;
    subject: string;
    status: string;
    created_at: string;
}

interface SMSRecord {
    id: string;
    to: string;
    message: string;
    status: string;
    created_at: string;
}

interface SystemLog {
    id: string;
    level: string;
    message: string;
    created_at: string;
}

interface CallTranscript {
    id: number;
    call_id: string;
    phone_number: string;
    summary: string;
    transcript: string;
    created_at: string;
    duration?: number;
    sentiment?: string;
    recording_url?: string;
}

interface Appointment {
    id: number;
    title: string;
    start_time: string;
    end_time: string;
    attendees: string;
    status: string;
}

interface Lead {
    id: number;
    company_name: string;
    contact_name?: string;
    email?: string;
    status: string;
    industry?: string;
    notes?: string;
    created_at: string;
}

interface TrainingData {
    id: number;
    source: string;
    content: string;
    category?: string;
    verified: boolean;
    created_at: string;
}

export default function MissionControl() {
    const [activeTab, setActiveTab] = useState<Tab>('overview');
    const [logs, setLogs] = useState<SystemLog[]>([]);
    const [emails, setEmails] = useState<EmailRecord[]>([]);
    const [smsMessages, setSmsMessages] = useState<SMSRecord[]>([]);
    const [callTranscripts, setCallTranscripts] = useState<CallTranscript[]>([]);
    const [appointments, setAppointments] = useState<Appointment[]>([]);
    const [leads, setLeads] = useState<Lead[]>([]);
    const [trainingData, setTrainingData] = useState<TrainingData[]>([]);

    const [chatMessages, setChatMessages] = useState<{ role: string; content: string }[]>([]);
    const [chatInput, setChatInput] = useState('');
    const [loading, setLoading] = useState(true);
    const [currentTime, setCurrentTime] = useState(new Date());
    const chatEndRef = useRef<HTMLDivElement>(null);

    // Stats
    const [stats, setStats] = useState({
        emailsSent: 0,
        smssSent: 0,
        callsToday: 0,
        leadsToday: 0,
        systemHealth: 'OPERATIONAL'
    });

    // Landing pages
    const landingPages = [
        { name: 'HVAC Landing', url: '/hvac_landing.html', status: 'ready' },
        { name: 'ALF Referral', url: '/alf_landing.html', status: 'ready' },
        { name: 'Client Portal', url: 'https://client-portal-one-phi.vercel.app', status: 'live' },
    ];

    useEffect(() => {
        fetchData();
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);
        const dataRefresh = setInterval(fetchData, 30000);
        return () => {
            clearInterval(timer);
            clearInterval(dataRefresh);
        };
    }, []);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [chatMessages]);

    async function fetchData() {
        setLoading(true);

        if (supabase) {
            try {
                // 1. Fetch REAL System Logs
                const { data: logsData } = await supabase
                    .from('system_logs')
                    .select('*')
                    .order('created_at', { ascending: false })
                    .limit(50);

                if (logsData) {
                    setLogs(logsData);

                    // Calculate stats
                    const today = new Date().toDateString();
                    const todayLeads = logsData.filter(l =>
                        l.level === 'LEAD' && new Date(l.created_at).toDateString() === today
                    ).length;
                    const todayEmails = logsData.filter(l => l.level === 'EMAIL').length; // Estimate
                    const todaySMS = logsData.filter(l => l.level === 'SMS').length; // Estimate

                    setStats(prev => ({
                        ...prev,
                        leadsToday: todayLeads,
                        emailsSent: prev.emailsSent + todayEmails,
                        smssSent: prev.smssSent + todaySMS
                    }));
                }

                // 2. Fetch REAL Call Transcripts
                const { data: callsData } = await supabase
                    .from('call_transcripts')
                    .select('*')
                    .order('created_at', { ascending: false })
                    .limit(20);

                if (callsData) {
                    setCallTranscripts(callsData);
                    const todayCalls = callsData.filter(c =>
                        new Date(c.created_at).toDateString() === new Date().toDateString()
                    ).length;
                    setStats(prev => ({ ...prev, callsToday: todayCalls }));
                }

                // 3. Fetch REAL Appointments
                const { data: appointmentsData } = await supabase
                    .from('calendar_events')
                    .select('*')
                    .gte('start_time', new Date().toISOString())
                    .order('start_time', { ascending: true })
                    .limit(5);
                if (appointmentsData) setAppointments(appointmentsData);

                // 4. Fetch Leads (Dossier)
                const { data: leadData } = await supabase
                    .from('leads')
                    .select('*')
                    .order('created_at', { ascending: false })
                    .limit(50);
                if (leadData) setLeads(leadData);

                // 5. Fetch Training Data (Brain)
                const { data: trainData } = await supabase
                    .from('training_data')
                    .select('*')
                    .order('created_at', { ascending: false })
                    .limit(50);
                if (trainData) setTrainingData(trainData);

            } catch (e) {
                console.warn('Real data fetch incomplete (tables might be missing).', e);
            }
        }

        setLoading(false);
    }

    async function handleChatSubmit(e: React.FormEvent) {
        e.preventDefault();
        if (!chatInput.trim()) return;
        const userMessage = chatInput;
        setChatInput('');
        setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);

        // AI Logic
        setTimeout(() => {
            let response = "I'm the Empire AI assistant. ";

            if (userMessage.toLowerCase().includes('appointment')) {
                response += appointments.length > 0
                    ? `You have ${appointments.length} upcoming appointments. Next: ${appointments[0].title}.`
                    : "No upcoming appointments scheduled.";
            } else if (userMessage.toLowerCase().includes('lead')) {
                response += `We are tracking ${leads.length} leads in the dossier.`;
            } else if (userMessage.toLowerCase().includes('status')) {
                response += `System ${stats.systemHealth}. Calls today: ${stats.callsToday}.`;
            } else {
                response += "I can help with leads, appointments, calls, or system status.";
            }

            setChatMessages(prev => [...prev, { role: 'assistant', content: response }]);
        }, 500);
    }

    const getLevelColor = (level: string) => {
        switch (level) {
            case 'ERROR': return 'text-red-400 bg-red-500/10';
            case 'WARNING': return 'text-yellow-400 bg-yellow-500/10';
            case 'LEAD': return 'text-green-400 bg-green-500/10';
            case 'EMAIL': return 'text-purple-400 bg-purple-500/10';
            case 'SMS': return 'text-blue-400 bg-blue-500/10';
            default: return 'text-slate-400 bg-slate-500/10';
        }
    };

    const tabs: { id: Tab; label: string; icon: string }[] = [
        { id: 'overview', label: 'Overview', icon: '📊' },
        { id: 'dossier', label: 'Dossier', icon: '📁' },
        { id: 'conversations', label: 'Calls', icon: '📞' },
        { id: 'emails', label: 'Emails', icon: '✉️' },
        { id: 'sms', label: 'SMS', icon: '📱' },
        { id: 'brain', label: 'Brain', icon: '🧠' },
        { id: 'pages', label: 'Pages', icon: '🌐' },
        { id: 'chat', label: 'AI Chat', icon: '🤖' },
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-950 to-black text-white font-sans selection:bg-blue-500/30">
            {/* Header */}
            <header className="border-b border-white/5 bg-black/40 backdrop-blur-xl sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="text-3xl filter drop-shadow-lg">🏰</div>
                        <div>
                            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-500 bg-clip-text text-transparent">
                                Empire Mission Control
                            </h1>
                            <p className="text-xs text-slate-400 font-medium tracking-wide">REAL-TIME COMMAND CENTER</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-2 bg-green-500/10 px-3 py-1 rounded-full border border-green-500/20">
                            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(34,197,94,0.5)]"></span>
                            <span className="text-sm text-green-400 font-medium tracking-wide">LIVE DATA</span>
                        </div>
                        <div className="text-right">
                            <div className="text-lg font-mono text-blue-400 font-medium">
                                {currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Tab Navigation */}
            <nav className="border-b border-white/5 bg-black/20 backdrop-blur-md">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="flex gap-1 overflow-x-auto no-scrollbar pb-2 pt-2">
                        {tabs.map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`px-5 py-3 text-sm font-medium transition-all flex items-center gap-2 border-b-2 whitespace-nowrap rounded-t-lg hover:bg-white/5 ${activeTab === tab.id
                                        ? 'border-blue-500 text-blue-400 bg-blue-500/5'
                                        : 'border-transparent text-slate-400'
                                    }`}
                            >
                                <span className="text-lg">{tab.icon}</span>
                                <span>{tab.label}</span>
                            </button>
                        ))}
                    </div>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto p-6 animate-in fade-in duration-500">
                {/* Overview Tab */}
                {activeTab === 'overview' && (
                    <div className="space-y-6">
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            {/* Left Column: Stats & Logs */}
                            <div className="lg:col-span-2 space-y-6">
                                {/* Stats Grid */}
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <StatCard label="Emails Sent" value={stats.emailsSent} color="blue" />
                                    <StatCard label="SMS Sent" value={stats.smssSent} color="green" />
                                    <StatCard label="Calls Today" value={stats.callsToday} color="purple" />
                                    <StatCard label="Leads Today" value={stats.leadsToday} color="orange" />
                                </div>

                                {/* Live Feed */}
                                <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden backdrop-blur-sm">
                                    <div className="p-4 border-b border-white/5 bg-black/20 flex justify-between items-center">
                                        <h2 className="text-lg font-semibold flex items-center gap-2">
                                            📜 System Log
                                            <span className="text-[10px] uppercase font-bold bg-white/10 px-2 py-0.5 rounded text-slate-400">Real-time</span>
                                        </h2>
                                    </div>
                                    <div className="max-h-96 overflow-y-auto custom-scrollbar">
                                        {logs.length === 0 ? (
                                            <div className="p-8 text-center text-slate-500">
                                                No system logs found yet. Waiting for activity...
                                            </div>
                                        ) : (
                                            logs.map(log => (
                                                <div key={log.id} className="text-sm border-b border-white/5 p-3 hover:bg-white/5 transition-colors flex items-start gap-3 group">
                                                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase ${getLevelColor(log.level)}`}>
                                                        {log.level}
                                                    </span>
                                                    <span className="text-slate-300 flex-1 font-mono text-xs md:text-sm group-hover:text-white transition-colors">{log.message}</span>
                                                    <span className="text-xs text-slate-600 font-mono whitespace-nowrap">
                                                        {new Date(log.created_at).toLocaleTimeString()}
                                                    </span>
                                                </div>
                                            ))
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* Right Column: Active Appointments */}
                            <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden backdrop-blur-sm h-fit">
                                <div className="p-4 border-b border-white/5 bg-black/20">
                                    <h2 className="text-lg font-semibold flex items-center gap-2">
                                        📅 Upcoming Appointments
                                    </h2>
                                </div>
                                <div className="p-4">
                                    {appointments.length === 0 ? (
                                        <div className="text-center py-8 text-slate-500">
                                            <div className="text-4xl mb-4 grayscale opacity-30">📅</div>
                                            <p>No scheduled appointments.</p>
                                            <p className="text-xs mt-2">Bookings from calls will appear here.</p>
                                        </div>
                                    ) : (
                                        <div className="space-y-3">
                                            {appointments.map(apt => (
                                                <div key={apt.id} className="bg-black/20 border border-white/5 rounded-lg p-3 hover:border-blue-500/30 transition-all">
                                                    <div className="font-bold text-blue-300">{apt.title}</div>
                                                    <div className="text-sm text-slate-400 mt-1">
                                                        {new Date(apt.start_time).toLocaleDateString()} at {new Date(apt.start_time).toLocaleTimeString()}
                                                    </div>
                                                    <div className="text-xs text-slate-500 mt-2 font-mono">{apt.attendees}</div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Dossier (Leads) Tab */}
                {activeTab === 'dossier' && (
                    <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-xl font-semibold">📁 Lead Dossier</h2>
                            <div className="text-xs font-mono text-slate-400">{leads.length} Records</div>
                        </div>

                        {leads.length === 0 ? (
                            <div className="text-center py-12 bg-black/20 rounded-xl">
                                <div className="text-4xl mb-4">📭</div>
                                <h3 className="text-lg font-medium text-slate-300">Dossier Empty</h3>
                                <p className="text-slate-500">No leads found. Initialize your lead generation agents.</p>
                            </div>
                        ) : (
                            <div className="overflow-x-auto">
                                <table className="w-full text-left border-collapse">
                                    <thead>
                                        <tr className="border-b border-white/10 text-xs uppercase text-slate-400">
                                            <th className="p-3">Company</th>
                                            <th className="p-3">Contact</th>
                                            <th className="p-3">Status</th>
                                            <th className="p-3">Industry</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {leads.map(lead => (
                                            <tr key={lead.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                                                <td className="p-3 font-medium text-white">{lead.company_name}</td>
                                                <td className="p-3 text-slate-300">
                                                    {lead.contact_name}
                                                    <div className="text-xs text-slate-500">{lead.email}</div>
                                                </td>
                                                <td className="p-3">
                                                    <span className={`text-[10px] uppercase font-bold px-2 py-1 rounded ${lead.status === 'new' ? 'bg-blue-500/10 text-blue-400' :
                                                            lead.status === 'contacted' ? 'bg-yellow-500/10 text-yellow-400' :
                                                                'bg-green-500/10 text-green-400'
                                                        }`}>
                                                        {lead.status}
                                                    </span>
                                                </td>
                                                <td className="p-3 text-slate-400">{lead.industry}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                )}

                {/* Brain (Training) Tab */}
                {activeTab === 'brain' && (
                    <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-xl font-semibold">🧠 Training Data (Brain)</h2>
                            <div className="text-xs font-mono text-slate-400">{trainingData.length} Concepts</div>
                        </div>

                        <div className="grid gap-4">
                            {trainingData.length === 0 ? (
                                <div className="text-center py-12 bg-black/20 rounded-xl">
                                    <div className="text-4xl mb-4">🧠</div>
                                    <h3 className="text-lg font-medium text-slate-300">Brain is Empty</h3>
                                    <p className="text-slate-500">No training data harvested yet.</p>
                                </div>
                            ) : (
                                trainingData.map(data => (
                                    <div key={data.id} className="bg-black/20 border border-white/5 rounded-lg p-4">
                                        <div className="flex justify-between items-start mb-2">
                                            <span className="text-xs font-mono uppercase text-blue-400 bg-blue-500/10 px-2 py-1 rounded">
                                                {data.source}
                                            </span>
                                            <span className="text-xs text-slate-500">{new Date(data.created_at).toLocaleDateString()}</span>
                                        </div>
                                        <p className="text-slate-300 text-sm leading-relaxed">{data.content}</p>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                )}

                {/* Emails Tab */}
                {activeTab === 'emails' && (
                    <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                        <h2 className="text-xl font-semibold mb-6">Email Activity</h2>
                        <div className="p-8 text-center border-2 border-dashed border-white/10 rounded-lg">
                            <div className="text-4xl mb-4">✉️</div>
                            <h3 className="text-lg font-medium text-white mb-2">View in Resend</h3>
                            <p className="text-slate-400 max-w-md mx-auto mb-6">
                                Detailed email logs are securely stored in your Resend Dashboard.
                            </p>
                            <a href="https://resend.com/emails" target="_blank" rel="noopener noreferrer" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition-colors">
                                Open Resend Dashboard
                            </a>
                        </div>
                    </div>
                )}

                {/* SMS Tab */}
                {activeTab === 'sms' && (
                    <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                        <h2 className="text-xl font-semibold mb-6">SMS Log</h2>
                        <div className="p-8 text-center border-2 border-dashed border-white/10 rounded-lg">
                            <div className="text-4xl mb-4">📱</div>
                            <h3 className="text-lg font-medium text-white mb-2">Connect GHL to See SMS</h3>
                            <p className="text-slate-400 max-w-md mx-auto mb-6">
                                We need to connect your GoHighLevel account to pull real-time SMS logs.
                            </p>
                            <a href="https://app.gohighlevel.com" target="_blank" rel="noopener noreferrer" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition-colors">
                                Connect GHL
                            </a>
                        </div>
                    </div>
                )}

                {/* Conversations/Calls Tab */}
                {activeTab === 'conversations' && (
                    <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                        <h2 className="text-xl font-semibold mb-6">Real Call Transcripts</h2>

                        {callTranscripts.length === 0 ? (
                            <div className="p-12 text-center border border-white/5 rounded-lg bg-black/20">
                                <div className="text-5xl mb-4 opacity-50">📞</div>
                                <h3 className="text-xl font-medium text-slate-300">No Calls Recorded Yet</h3>
                                <p className="text-slate-500 mt-2 max-w-md mx-auto">
                                    Calls made to your Vapi agent <strong>(352) 758-5336</strong> will appear here automatically with transcripts and summaries.
                                </p>
                                <div className="mt-8">
                                    <p className="text-sm text-slate-400 mb-2">Try it now:</p>
                                    <div className="inline-block bg-white/5 px-4 py-2 rounded font-mono text-purple-400 border border-purple-500/30">
                                        (352) 758-5336
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {callTranscripts.map(call => (
                                    <div key={call.id} className="bg-black/20 border border-white/5 rounded-xl p-5 hover:border-purple-500/30 transition-all">
                                        <div className="flex justify-between items-start mb-4">
                                            <div>
                                                <div className="text-lg font-semibold text-white">{call.phone_number || 'Unknown Caller'}</div>
                                                <div className="text-xs text-slate-500 font-mono mt-1">{new Date(call.created_at).toLocaleString()}</div>
                                            </div>
                                            <span className="bg-purple-500/10 text-purple-400 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide">
                                                {call.sentiment || 'Call Info'}
                                            </span>
                                        </div>

                                        <div className="bg-white/5 rounded-lg p-4 text-sm text-slate-300 leading-relaxed border-l-2 border-purple-500/50">
                                            {call.summary || call.transcript || 'No transcript available.'}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Landing Pages Tab */}
                {activeTab === 'pages' && (
                    <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                        <h2 className="text-xl font-semibold mb-6">Active Landing Pages</h2>
                        <div className="grid gap-4 md:grid-cols-2">
                            {landingPages.map((page, i) => (
                                <div key={i} className="bg-black/20 border border-white/5 rounded-xl p-5 hover:border-blue-500/30 transition-all group flex flex-col h-full">
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="bg-blue-500/10 p-2 rounded-lg text-2xl group-hover:scale-110 transition-transform">🌐</div>
                                        <span className={`text-[10px] uppercase font-bold px-2 py-1 rounded ${page.status === 'live' ? 'bg-green-500/10 text-green-400' : 'bg-blue-500/10 text-blue-400'
                                            }`}>
                                            {page.status}
                                        </span>
                                    </div>
                                    <h3 className="text-lg font-bold text-white mb-1">{page.name}</h3>
                                    <div className="text-xs text-slate-500 font-mono mb-6 truncate">{page.url}</div>

                                    <div className="mt-auto">
                                        <a href={page.url} target="_blank" rel="noopener noreferrer"
                                            className="block w-full text-center py-2 bg-white/5 hover:bg-blue-600 hover:text-white rounded-lg text-sm font-medium transition-all border border-white/10 hover:border-transparent">
                                            Visit Page →
                                        </a>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* AI Chat Tab */}
                {activeTab === 'chat' && (
                    <div className="bg-white/5 border border-white/10 rounded-xl p-0 h-[600px] flex flex-col overflow-hidden">
                        <div className="p-4 border-b border-white/5 bg-black/20">
                            <h2 className="text-lg font-semibold flex items-center gap-2">
                                🤖 Empire AI Assistant
                                <span className="text-xs bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded-full">Beta</span>
                            </h2>
                        </div>

                        <div className="flex-1 overflow-y-auto space-y-4 p-6 custom-scrollbar bg-black/10">
                            {chatMessages.length === 0 && (
                                <div className="h-full flex flex-col items-center justify-center text-slate-500 opacity-60">
                                    <div className="text-6xl mb-6 grayscale text-slate-700">🤖</div>
                                    <p className="text-lg font-medium">Ready to assist.</p>
                                    <p className="text-sm">Ask about your business stats.</p>
                                </div>
                            )}
                            {chatMessages.map((msg, i) => (
                                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`max-w-[80%] rounded-2xl px-5 py-3 text-sm leading-relaxed shadow-lg ${msg.role === 'user'
                                            ? 'bg-blue-600 text-white rounded-br-none'
                                            : 'bg-white/10 text-slate-200 border border-white/5 rounded-bl-none'
                                        }`}>
                                        {msg.content}
                                    </div>
                                </div>
                            ))}
                            <div ref={chatEndRef} />
                        </div>

                        <div className="p-4 bg-black/20 border-t border-white/5">
                            <form onSubmit={handleChatSubmit} className="flex gap-2">
                                <input
                                    type="text"
                                    value={chatInput}
                                    onChange={(e) => setChatInput(e.target.value)}
                                    placeholder="Ask a question..."
                                    className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:border-blue-500/50 focus:bg-white/10 text-white placeholder-slate-600 transition-all font-light"
                                />
                                <button
                                    type="submit"
                                    className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl font-medium shadow-lg shadow-blue-900/20 transition-all transform hover:scale-105"
                                >
                                    Send
                                </button>
                            </form>
                        </div>
                    </div>
                )}
            </main>

            {/* Footer */}
            <footer className="mt-8 border-t border-white/5 bg-black/20 py-6 text-center text-slate-600 text-xs">
                <p>EMPIRE UNIFIED • MISSION CONTROL v2.3 • <span className="text-slate-500">Full Spectrum</span></p>
            </footer>
        </div>
    );
}

function StatCard({ label, value, color }: { label: string, value: number, color: string }) {
    const colorClasses: { [key: string]: string } = {
        blue: 'text-blue-400 border-blue-500/20 hover:border-blue-500/50 bg-blue-500/5',
        green: 'text-green-400 border-green-500/20 hover:border-green-500/50 bg-green-500/5',
        purple: 'text-purple-400 border-purple-500/20 hover:border-purple-500/50 bg-purple-500/5',
        orange: 'text-orange-400 border-orange-500/20 hover:border-orange-500/50 bg-orange-500/5',
    };

    return (
        <div className={`border rounded-xl p-4 transition-all duration-300 transform hover:-translate-y-1 ${colorClasses[color] || 'text-white border-white/10'}`}>
            <div className="text-slate-400 text-[10px] uppercase tracking-wider font-bold mb-1 opacity-70">{label}</div>
            <div className={`text-3xl font-bold font-mono tracking-tight`}>{value}</div>
        </div>
    );
}
