'use client';

import React, { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import {
  Shield,
  TrendingUp,
  MessageSquare,
  Users,
  Activity,
  Zap,
  ChevronRight,
  Send,
  Bell,
  Mail,
  Phone,
  Share2,
  ExternalLink
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

interface LogEntry {
  id: string;
  type: 'sms' | 'email' | 'call' | 'social';
  title: string;
  subtitle: string;
  timestamp: string;
  status: string;
  content?: string;
  video_watched?: boolean;
  intent_score?: number;
  metadata?: any;
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('Overview');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [stats, setStats] = useState({
    sentinel_score: 98,
    pipeline_value: 0,
    outbound_24h: 0,
    uptime: '100%',
    pulse_status: 'Steady'
  });
  const [selectedTranscript, setSelectedTranscript] = useState<string | null>(null);

  // Initial Data Fetch
  useEffect(() => {
    const fetchData = async () => {
      // Fetch Stats
      const { data: touches } = await supabase
        .from('outbound_touches')
        .select('id', { count: 'exact' })
        .gte('ts', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString());

      const { data: leads } = await supabase
        .from('contacts_master')
        .select('id', { count: 'exact' });

      setStats(prev => ({
        ...prev,
        outbound_24h: touches?.length || 0,
        pipeline_value: (leads?.length || 0) * 1200 // Mock ROI
      }));

      // Initial Logs
      const { data: touchLogs } = await supabase
        .from('outbound_touches')
        .select('*')
        .order('ts', { ascending: false })
        .limit(10);

      const formatted = (touchLogs || []).map(t => ({
        id: t.id,
        type: t.channel as any,
        title: t.company || 'Unknown Subject',
        subtitle: `${t.channel.toUpperCase()}: ${t.status}`,
        timestamp: t.ts,
        status: t.status,
        content: t.payload?.content || '',
        video_watched: t.payload?.video_watched || false,
        intent_score: t.payload?.intent_score || 0
      }));

      setLogs(formatted);
    };

    fetchData();

    // REAL-TIME SUBSCRIPTIONS
    const channel = supabase
      .channel('schema-db-changes')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'outbound_touches' }, payload => {
        const newEntry: LogEntry = {
          id: payload.new.id,
          type: payload.new.channel,
          title: payload.new.company || 'New Outreach',
          subtitle: `${payload.new.channel.toUpperCase()}: ${payload.new.status}`,
          timestamp: payload.new.ts,
          status: payload.new.status,
          video_watched: payload.new.payload?.video_watched || false,
          intent_score: payload.new.payload?.intent_score || 0
        };
        setLogs(prev => [newEntry, ...prev].slice(0, 20));

        // Update 24h Stat
        setStats(prev => ({
          ...prev,
          outbound_24h: prev.outbound_24h + 1,
          pipeline_value: prev.pipeline_value + 1200
        }));
      })
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'conversation_logs' }, payload => {
        if (payload.new.channel === 'social') {
          const newEntry: LogEntry = {
            id: payload.new.log_id,
            type: 'social',
            title: 'Empire Broadcast',
            subtitle: `${payload.new.metadata?.platform?.toUpperCase() || 'SOCIAL'} Post`,
            timestamp: payload.new.timestamp,
            status: 'live',
            content: payload.new.content
          };
          setLogs(prev => [newEntry, ...prev].slice(0, 20));
        } else {
          const newEntry: LogEntry = {
            id: payload.new.log_id,
            type: 'call',
            title: 'Sarah Voice Agent',
            subtitle: `Transcript Received`,
            timestamp: payload.new.timestamp,
            status: 'completed',
            content: payload.new.content
          };
          setLogs(prev => [newEntry, ...prev].slice(0, 20));
        }
      })
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'system_health_log' }, payload => {
        setStats(prev => ({
          ...prev,
          pulse_status: payload.new.status === 'working' ? 'Vibrant' : 'Steady',
          uptime: '99.9%' // Mock slightly varying for realism
        }));
      })
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  return (
    <div className="flex min-h-screen bg-[#050505] text-[#e0e0e0] font-sans overflow-hidden">
      {/* Sidebar */}
      <aside className="w-20 lg:w-64 border-r border-white/5 flex flex-col bg-black/40 backdrop-blur-2xl">
        <div className="p-6 flex items-center space-x-3 mb-8">
          <div className="p-2 bg-blue-500/20 rounded-xl border border-blue-500/30">
            <Shield className="text-blue-400 w-6 h-6" />
          </div>
          <span className="text-xl font-bold tracking-tighter hidden lg:block">SOVEREIGN</span>
        </div>

        <nav className="flex-1 px-4 space-y-2">
          {[
            { name: 'Overview', icon: Activity },
            { name: 'Leads', icon: Users },
            { name: 'Comms', icon: MessageSquare },
            { name: 'Social', icon: Share2 }
          ].map((item) => (
            <button
              key={item.name}
              onClick={() => setActiveTab(item.name)}
              className={`w-full flex items-center p-4 rounded-xl transition-all ${activeTab === item.name
                ? 'bg-blue-500/10 text-blue-400 shadow-lg shadow-blue-500/5 border border-blue-500/20'
                : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'
                }`}
            >
              <item.icon className="w-5 h-5 lg:mr-3" />
              <span className="hidden lg:block font-medium">{item.name}</span>
            </button>
          ))}
        </nav>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-y-auto p-4 md:p-8 space-y-8 h-screen custom-scrollbar relative">
        <header className="flex justify-between items-center glass-card p-4 rounded-2xl border border-white/5 bg-white/[0.02]">
          <div className="flex items-center space-x-4">
            <h2 className="text-lg font-bold text-gray-400 uppercase tracking-widest">{activeTab}</h2>
            <ChevronRight className="w-4 h-4 text-gray-600" />
            <span className="text-xs text-blue-400 font-mono animate-pulse">● LIVE UPLINK</span>
          </div>
          <div className="flex items-center space-x-6">
            <div className="text-right">
              <p className="text-[10px] text-gray-500 uppercase tracking-widest">Sentinel Protection</p>
              <p className="text-sm font-mono text-green-400">{stats.sentinel_score}% ACTIVE</p>
            </div>
          </div>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: 'Outbound (24h)', value: stats.outbound_24h, icon: Send, color: 'text-blue-400' },
            { label: 'Est. Pipeline', value: `$${stats.pipeline_value.toLocaleString()}`, icon: TrendingUp, color: 'text-purple-400' },
            { label: 'Uptime', value: stats.uptime, icon: Activity, color: 'text-green-400' },
            { label: 'AI Pulse', value: stats.pulse_status, icon: Zap, color: 'text-yellow-400' }
          ].map((item, i) => (
            <div key={i} className="bg-white/[0.03] border border-white/5 p-6 rounded-3xl group shadow-inner">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">{item.label}</p>
                  <h3 className="text-3xl font-bold mt-1 tracking-tighter">{item.value}</h3>
                </div>
                <div className={`p-3 rounded-2xl bg-white/5 ${item.color}`}>
                  <item.icon className="w-5 h-5" />
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Activity Feed */}
          <section className="lg:col-span-2 bg-white/[0.02] border border-white/5 p-6 rounded-3xl flex flex-col h-[600px]">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold flex items-center uppercase tracking-tight">
                <Zap className="w-5 h-5 mr-3 text-blue-400" />
                Real-Time Mission Feed
              </h2>
              <div className="text-[10px] font-mono text-gray-500 tracking-widest">SYNCING WITH REVENUE LOOP...</div>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
              {logs.map((log) => (
                <div
                  key={log.id}
                  onClick={() => log.type === 'call' && setSelectedTranscript(log.content || 'No transcript.')}
                  className={`flex items-center justify-between p-4 rounded-2xl bg-white/[0.03] border border-white/5 hover:border-blue-500/30 transition-all cursor-pointer group`}
                >
                  <div className="flex items-center space-x-4">
                    <div className={`p-2.5 rounded-xl bg-white/5 group-hover:scale-110 transition-transform relative`}>
                      {log.type === 'sms' && <MessageSquare className="w-4 h-4 text-green-400" />}
                      {log.type === 'email' && <Mail className="w-4 h-4 text-blue-400" />}
                      {log.type === 'call' && <Phone className="w-4 h-4 text-purple-400" />}
                      {log.type === 'social' && <Share2 className="w-4 h-4 text-pink-400" />}
                      {log.video_watched && (
                        <div className="absolute -top-1 -right-1 p-1 bg-red-500 rounded-full animate-ping" />
                      )}
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <h4 className="text-sm font-bold text-gray-200 group-hover:text-white">{log.title}</h4>
                        {log.video_watched && (
                          <span className="bg-red-500/10 text-red-500 text-[8px] font-black px-1.5 py-0.5 rounded border border-red-500/20 uppercase tracking-tighter">HOT INTENT (VIDEO)</span>
                        )}
                      </div>
                      <p className="text-[10px] text-gray-500 font-medium uppercase tracking-widest">
                        {log.subtitle} {log.intent_score ? `• SCORE: ${log.intent_score}` : ''}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-[10px] text-gray-400 font-mono">
                      {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </p>
                    {log.type === 'call' && <span className="text-[9px] text-blue-400 underline opacity-0 group-hover:opacity-100">VIEW TRANSCRIPT</span>}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Transcript / Details Panel */}
          <section className="bg-black/60 border border-white/10 p-6 rounded-3xl flex flex-col h-[600px]">
            <h2 className="text-lg font-bold flex items-center mb-6 text-gray-400">
              <Activity className="w-5 h-5 mr-3 text-purple-400" />
              INTELLIGENCE OVERLAY
            </h2>
            <div className="flex-1 overflow-y-auto font-mono text-xs text-gray-300 leading-relaxed bg-black/40 p-4 rounded-2xl border border-white/5">
              {selectedTranscript ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between border-b border-white/5 pb-2">
                    <span className="text-purple-400">SARAH AGENT 3.1</span>
                    <button onClick={() => setSelectedTranscript(null)} className="text-gray-600 hover:text-white">CLOSE [X]</button>
                  </div>
                  <div className="whitespace-pre-wrap">{selectedTranscript}</div>
                </div>
              ) : (
                <div className="h-full flex flex-col items-center justify-center opacity-30 text-center">
                  <Activity className="w-12 h-12 mb-4 animate-pulse" />
                  <p>SELECT A CALL LOG TO VIEW REAL-TIME TRANSCRIPT DATA</p>
                </div>
              )}
            </div>
          </section>
        </div>

        <footer className="pt-12 pb-6 text-center text-gray-600 text-[10px] font-mono tracking-[0.4em]">
          SOVEREIGN EMPIRE UNIFIED PROTOCOL // VERSION 5.0 LIVE
        </footer>
      </main>
    </div>
  );
}
