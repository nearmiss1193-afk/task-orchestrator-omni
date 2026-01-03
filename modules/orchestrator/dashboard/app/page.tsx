import LiveLogs from '@/components/LiveLogs';
import { Activity, Users, Zap, Shield } from 'lucide-react';
import OracleChat from '@/components/OracleChat';
import { supabase } from '@/lib/supabase';

// Server Component for initial stats
async function getStats() {
  const { count: contacts } = await supabase.from('contacts_master').select('*', { count: 'exact', head: true });
  const { count: staged } = await supabase.from('staged_replies').select('*', { count: 'exact', head: true }).eq('status', 'pending_approval');
  const { count: nurtured } = await supabase.from('contacts_master').select('*', { count: 'exact', head: true }).eq('status', 'nurtured');
  return { contacts: contacts || 0, staged: staged || 0, nurtured: nurtured || 0 };
}

export default async function Dashboard() {
  const stats = await getStats();

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-6 font-sans selection:bg-blue-500/30">
      {/* Header */}
      <header className="flex justify-between items-center mb-8 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
            EMPIRE COMMAND CENTER
          </h1>
          <p className="text-slate-500 text-sm mt-1">Sovereign Stack V2 // <span className="text-green-500">ONLINE</span></p>
        </div>
        <div className="flex gap-4">
          <div className="flex items-center gap-2 px-3 py-1 bg-slate-900 rounded-full border border-slate-800 text-xs text-slate-400">
            <Shield size={12} className="text-green-500" /> System Secure
          </div>
        </div>
      </header>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex justify-between items-start mb-2">
            <span className="text-slate-400 text-xs uppercase tracking-wider">Total Targets</span>
            <Users size={16} className="text-blue-500" />
          </div>
          <div className="text-2xl font-bold text-white">{stats.contacts}</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex justify-between items-start mb-2">
            <span className="text-slate-400 text-xs uppercase tracking-wider">Pending Approvals</span>
            <Activity size={16} className="text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-white">{stats.staged}</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex justify-between items-start mb-2">
            <span className="text-slate-400 text-xs uppercase tracking-wider">Active Nurture</span>
            <Zap size={16} className="text-purple-500" />
          </div>
          <div className="text-2xl font-bold text-white">{stats.nurtured}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex justify-between items-start mb-2">
            <span className="text-slate-400 text-xs uppercase tracking-wider">System Health</span>
            <Activity size={16} className="text-green-500" />
          </div>
          <div className="text-2xl font-bold text-green-400">100%</div>
        </div>
      </div>

      {/* Operational View */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Live Feed (2 Cols) */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-lg font-semibold text-slate-300">Operational Log</h2>
          <LiveLogs />
        </div>

        {/* Quick Actions (1 Col) */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-slate-300">Mission Control</h2>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
            <p className="text-sm text-slate-500">Manual Triggers (Coming Soon)</p>
            <button className="w-full text-left px-3 py-2 rounded bg-slate-800/50 text-slate-400 text-sm hover:bg-slate-800 transition-colors">
              ▶ Force Vortex Scrape
            </button>
            <button className="w-full text-left px-3 py-2 rounded bg-slate-800/50 text-slate-400 text-sm hover:bg-slate-800 transition-colors">
              ▶ Deploy Master Dossier
            </button>
          </div>
        </div>
      </div>

      <div className="fixed bottom-6 right-6 z-50">
        {/* GHL Widget is external */}
      </div>
      <OracleChat />
    </main>
  );
}
