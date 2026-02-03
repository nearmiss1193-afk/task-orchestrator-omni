
'use client';

import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { Activity, Users, Zap } from 'lucide-react';

interface Stats {
    contacts: number;
    staged: number;
    nurtured: number;
    outreach: number;
}

export default function StatsGrid({ initialStats }: { initialStats: Stats }) {
    const [stats, setStats] = useState<Stats>(initialStats);

    useEffect(() => {
        // Realtime subscription for contacts_master count
        const contactsChannel = supabase
            .channel('stats-changes')
            .on('postgres_changes', { event: '*', schema: 'public', table: 'contacts_master' }, () => {
                refreshStats();
            })
            .on('postgres_changes', { event: '*', schema: 'public', table: 'staged_replies' }, () => {
                refreshStats();
            })
            .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'outbound_touches' }, () => {
                refreshStats();
            })
            .subscribe();

        const refreshStats = async () => {
            const { count: contacts } = await supabase.from('contacts_master').select('*', { count: 'exact', head: true });
            const { count: staged } = await supabase.from('staged_replies').select('*', { count: 'exact', head: true }).eq('status', 'pending_approval');
            const { count: nurtured } = await supabase.from('contacts_master').select('*', { count: 'exact', head: true }).eq('status', 'nurtured');
            const { count: outreach } = await supabase.from('outbound_touches').select('*', { count: 'exact', head: true });
            setStats({
                contacts: contacts || 0,
                staged: staged || 0,
                nurtured: nurtured || 0,
                outreach: outreach || 0
            });

            // Trigger visual pulse
            const cards = document.querySelectorAll('.stat-card');
            cards.forEach(card => {
                card.classList.add('pulse-glow');
                setTimeout(() => card.classList.remove('pulse-glow'), 1000);
            });
        };

        return () => {
            supabase.removeChannel(contactsChannel);
        };
    }, []);

    return (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="stat-card bg-slate-900 border border-slate-800 p-4 rounded-xl transition-all duration-300">
                <div className="flex justify-between items-start mb-2">
                    <span className="text-slate-400 text-xs uppercase tracking-wider">Total Targets</span>
                    <Users size={16} className="text-blue-500" />
                </div>
                <div className="text-2xl font-bold text-white">{stats.contacts}</div>
            </div>

            <div className="stat-card bg-slate-900 border border-slate-800 p-4 rounded-xl transition-all duration-300">
                <div className="flex justify-between items-start mb-2">
                    <span className="text-slate-400 text-xs uppercase tracking-wider">Pending Approvals</span>
                    <Activity size={16} className="text-amber-500" />
                </div>
                <div className="text-2xl font-bold text-white">{stats.staged}</div>
            </div>

            <div className="stat-card bg-slate-900 border border-slate-800 p-4 rounded-xl transition-all duration-300">
                <div className="flex justify-between items-start mb-2">
                    <span className="text-slate-400 text-xs uppercase tracking-wider">Active Nurture</span>
                    <Zap size={16} className="text-purple-500" />
                </div>
                <div className="text-2xl font-bold text-white">{stats.nurtured}</div>
            </div>
            <div className="stat-card bg-slate-900 border border-slate-800 p-4 rounded-xl transition-all duration-300">
                <div className="flex justify-between items-start mb-2">
                    <span className="text-slate-400 text-xs uppercase tracking-wider">Total Outreach</span>
                    <Activity size={16} className="text-green-500" />
                </div>
                <div className="text-2xl font-bold text-green-400">{stats.outreach}</div>
            </div>
        </div>
    );
}
