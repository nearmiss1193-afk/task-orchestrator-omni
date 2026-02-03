'use client';

import React, { useState, useEffect } from 'react';
import {
  Shield,
  TrendingUp,
  MessageSquare,
  Users,
  Activity,
  Zap,
  ChevronRight,
  Send,
  Bell
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

const mockChartData = [
  { name: 'Mon', leads: 40 },
  { name: 'Tue', leads: 30 },
  { name: 'Wed', leads: 65 },
  { name: 'Thu', leads: 45 },
  { name: 'Fri', leads: 90 },
  { name: 'Sat', leads: 120 },
  { name: 'Sun', leads: 142 },
];

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('Overview');
  const [stats, setStats] = useState({
    sentinel_score: 98,
    pipeline_value: "$0",
    funnel: { prospects_discovered: 0, interested: 0, booked: 0 },
    recent_comms: []
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch('https://empire-unified-backup-production-6d15.up.railway.app/dashboard_stats');
        const data = await res.json();
        setStats(prev => ({
          ...prev,
          ...data,
          pipeline_value: new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(data.pipeline_value || 0)
        }));
      } catch (e) {
        console.error("Scale connection failed", e);
      }
    };
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex min-h-screen bg-background text-foreground overflow-hidden">
      {/* Sidebar Navigation */}
      <aside className="w-20 lg:w-64 border-r border-white/5 flex flex-col bg-card-bg/40 backdrop-blur-xl">
        <div className="p-6 flex items-center space-x-3 mb-8">
          <div className="p-2 bg-primary/20 rounded-xl">
            <Shield className="text-primary w-6 h-6" />
          </div>
          <span className="text-xl font-bold gold-glow hidden lg:block">SOVEREIGN</span>
        </div>

        <nav className="flex-1 px-4 space-y-2">
          {[
            { name: 'Overview', icon: Activity },
            { name: 'Leads', icon: Users },
            { name: 'Comms', icon: MessageSquare },
            { name: 'Settings', icon: Zap },
          ].map((item) => (
            <button
              key={item.name}
              onClick={() => setActiveTab(item.name)}
              className={`w-full flex items-center p-4 rounded-xl transition-all ${activeTab === item.name
                ? 'bg-primary/10 text-primary shadow-lg shadow-primary/5'
                : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'
                }`}
            >
              <item.icon className="w-5 h-5 lg:mr-3" />
              <span className="hidden lg:block font-medium">{item.name}</span>
              {activeTab === item.name && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary lg:block hidden" />}
            </button>
          ))}
        </nav>

        <div className="p-4">
          <div className="glass-card p-4 rounded-2xl bg-primary/5 border-primary/10">
            <p className="text-[10px] text-primary uppercase tracking-[0.2em] font-bold mb-2">Campaign Status</p>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-xs font-mono text-gray-200">ACTIVE - OUTREACHING</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-4 md:p-8 space-y-8 h-screen custom-scrollbar">
        {/* Header */}
        <header className="flex justify-between items-center glass-card p-4 rounded-2xl">
          <div className="flex items-center space-x-4">
            <h2 className="text-lg font-bold text-gray-400 capitalize">{activeTab}</h2>
            <ChevronRight className="w-4 h-4 text-gray-600" />
            <span className="text-xs text-gray-500 font-mono">/ {new Date().toLocaleDateString()}</span>
          </div>

          <div className="flex items-center space-x-6">
            <div className="hidden md:flex flex-col items-end">
              <span className="text-xs text-gray-400 uppercase tracking-widest">Sentinel Score</span>
              <span className="text-primary font-mono text-xl leading-none">{stats.sentinel_score}%</span>
            </div>
            <div className="p-2 rounded-full glass-card hover:bg-white/10 cursor-pointer relative group">
              <Bell className="w-5 h-5 text-gray-300" />
              <span className="absolute top-2 right-2 w-2 h-2 bg-accent rounded-full animate-pulse" />
              <div className="absolute top-full right-0 mt-4 w-64 glass-card p-4 rounded-xl opacity-0 group-hover:opacity-100 transition-all pointer-events-none z-50">
                <p className="text-xs font-bold text-primary mb-2">System Alerts</p>
                <div className="text-[10px] space-y-2">
                  <div className="flex justify-between text-gray-300">
                    <span>New Lead identified</span>
                    <span>2m ago</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Hero Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: 'Total Prospects', value: stats.funnel.prospects_discovered, icon: Users, color: 'text-secondary' },
            { label: 'Pipeline Val', value: stats.pipeline_value, icon: TrendingUp, color: 'text-primary' },
            { label: 'Hot Interests', value: stats.funnel.interested, icon: MessageSquare, color: 'text-accent' },
            { label: 'Sovereign Uptime', value: '100%', icon: Activity, color: 'text-green-400' },
          ].map((item, i) => (
            <div key={i} className="glass-card p-6 rounded-3xl group relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 -mr-16 -mt-16 bg-white/[0.02] rounded-full blur-3xl group-hover:bg-primary/[0.05] transition-all" />
              <div className="flex justify-between items-start relative">
                <div>
                  <p className="text-gray-400 text-sm font-medium uppercase tracking-wider">{item.label}</p>
                  <h3 className="text-3xl font-bold mt-1 group-hover:gold-glow transition-all">{item.value}</h3>
                </div>
                <div className={`p-3 rounded-2xl bg-white/5 ${item.color}`}>
                  <item.icon className="w-6 h-6" />
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Chart Area */}
          <section className="lg:col-span-2 glass-card p-6 rounded-3xl space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-bold flex items-center">
                <Activity className="w-5 h-5 mr-2 text-primary" />
                Growth Trajectory
              </h2>
              <div className="flex space-x-2">
                <button className="px-3 py-1.5 rounded-lg bg-primary/10 text-primary text-xs font-bold uppercase transition-all">Week</button>
                <button className="px-3 py-1.5 rounded-lg bg-white/5 text-gray-400 text-xs font-bold uppercase hover:bg-white/10 transition-all">Month</button>
              </div>
            </div>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={mockChartData}>
                  <defs>
                    <linearGradient id="colorLeads" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#d4af37" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#d4af37" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
                  <XAxis dataKey="name" stroke="#666" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#666" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: 'rgba(5, 5, 5, 0.9)', border: '1px solid rgba(212, 175, 55, 0.2)', borderRadius: '12px', backdropFilter: 'blur(10px)' }}
                    itemStyle={{ color: '#d4af37' }}
                  />
                  <Area type="monotone" dataKey="leads" stroke="#d4af37" strokeWidth={3} fillOpacity={1} fill="url(#colorLeads)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </section>

          {/* Command Feed / Activity */}
          <section className="glass-card p-6 rounded-3xl flex flex-col h-[450px]">
            <h2 className="text-xl font-bold flex items-center mb-6">
              <Zap className="w-5 h-5 mr-2 text-secondary" />
              Live Command Feed
            </h2>
            <div className="flex-1 overflow-y-auto space-y-4 pr-2 custom-scrollbar">
              {stats.recent_comms.length > 0 ? stats.recent_comms.map((comm: any, idx) => (
                <div key={idx} className="flex items-start space-x-3 p-3 rounded-2xl hover:bg-white/5 transition-colors cursor-pointer group border border-transparent hover:border-white/5">
                  <div className="mt-1 p-2 rounded-lg bg-secondary/10 text-secondary transition-all group-hover:bg-secondary group-hover:text-background">
                    <MessageSquare className="w-4 h-4" />
                  </div>
                  <div className="flex-1">
                    <div className="flex justify-between items-start">
                      <span className="text-sm font-bold text-gray-200">{comm.company}</span>
                      <span className="text-[10px] text-gray-500 font-mono italic">
                        {new Date(comm.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <p className="text-xs text-gray-400 mt-1 line-clamp-1 italic">"{comm.status}"</p>
                  </div>
                </div>
              )) : (
                <div className="h-full flex flex-col items-center justify-center text-gray-500 space-y-4 opacity-50">
                  <div className="relative">
                    <Activity className="w-12 h-12 animate-pulse text-primary" />
                    <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full" />
                  </div>
                  <p className="text-xs font-mono tracking-tighter uppercase italic gold-glow">Waiting for Signal...</p>
                </div>
              )}
            </div>
            <div className="mt-6 relative">
              <input
                type="text"
                placeholder="Manual Signal Override..."
                className="w-full bg-white/5 border border-white/10 rounded-2xl py-3 px-4 pr-12 text-sm focus:outline-none focus:border-primary transition-all shadow-inner focus:shadow-primary/5"
              />
              <button className="absolute right-2 top-2 p-2 bg-primary text-background rounded-xl hover:cyber-glow transition-all hover:scale-105 active:scale-95 group">
                <Send className="w-4 h-4 group-hover:rotate-12 transition-transform" />
              </button>
            </div>
          </section>
        </div>

        <footer className="text-center text-gray-600 text-[10px] py-4 flex flex-col items-center space-y-2">
          <p className="font-mono tracking-[0.3em] uppercase opacity-50">Sovereign Empire Protocol v4.0a // [BEYOND THE SHORE]</p>
          <div className="flex space-x-6">
            <span className="hover:text-primary cursor-pointer transition-colors hover:gold-glow">System Docs</span>
            <span className="hover:text-primary cursor-pointer transition-colors hover:gold-glow">Truth Oracle</span>
            <span className="hover:text-primary cursor-pointer transition-colors hover:gold-glow text-accent">Veto Control</span>
          </div>
        </footer>
      </main>
    </div>
  );
}
