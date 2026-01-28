import LiveLogs from '@/components/LiveLogs';
import { Shield } from 'lucide-react';
import OracleChat from '@/components/OracleChat';
import { supabase } from '@/lib/supabase';
import StatsGrid from '@/components/StatsGrid';

// Server Component for initial stats
async function getStats() {
  const { count: contacts } = await supabase.from('contacts_master').select('*', { count: 'exact', head: true });
  const { count: staged } = await supabase.from('staged_replies').select('*', { count: 'exact', head: true }).eq('status', 'pending_approval');
  const { count: nurtured } = await supabase.from('contacts_master').select('*', { count: 'exact', head: true }).eq('status', 'nurtured');
  const { count: outreach } = await supabase.from('outbound_touches').select('*', { count: 'exact', head: true });
  return { contacts: contacts || 0, staged: staged || 0, nurtured: nurtured || 0, outreach: outreach || 0 };
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
      <StatsGrid initialStats={stats} />

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
