"use client";

import React, { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabaseClient';
import { CheckCircle, AlertTriangle, ArrowRight, Twitter } from 'lucide-react';
import Link from 'next/link';

interface VerificationTask {
    id: string;
    type: 'reply' | 'social';
    title: string;
    description: string;
    actionLink: string;
    timestamp: string;
}

export function VerificationQueue() {
    const [tasks, setTasks] = useState<VerificationTask[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTasks = async () => {
            setLoading(true);
            try {
                const newTasks: VerificationTask[] = [];

                // 1. Fetch AI Paused / Unverified Replies
                const { data: leads, error: leadsErr } = await supabase
                    .from('contacts_master')
                    .select('id, company_name, updated_at, status')
                    .eq('status', 'replied')
                    .order('updated_at', { ascending: false })
                    .limit(5);

                if (!leadsErr && leads) {
                    leads.forEach(lead => {
                        newTasks.push({
                            id: `reply_${lead.id}`,
                            type: 'reply',
                            title: `Verify Reply: ${lead.company_name || 'Unknown Contact'}`,
                            description: `Sovereign AI detected a reply. Human verification required before booking workflow proceeds.`,
                            actionLink: `/inbox`, // Could add ?contact_id=${lead.id} if supported
                            timestamp: lead.updated_at
                        });
                    });
                }

                // 2. Fetch Pending Social Drafts
                const { data: socials, error: socialsErr } = await supabase
                    .from('social_drafts')
                    .select('id, platform, created_at')
                    .eq('status', 'draft')
                    .order('created_at', { ascending: false })
                    .limit(5);

                if (!socialsErr && socials) {
                    socials.forEach(draft => {
                        newTasks.push({
                            id: `social_${draft.id}`,
                            type: 'social',
                            title: `Approve Social Asset: ${draft.platform}`,
                            description: `Sovereign drafted a new post for Ayrshare. Review required prior to dispatch.`,
                            actionLink: `/social`,
                            timestamp: draft.created_at
                        });
                    });
                }

                // Sort by newest first
                newTasks.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
                setTasks(newTasks);

            } catch (err) {
                console.error("Verification Queue Error:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchTasks();
    }, []);

    if (loading) {
        return (
            <div className="bg-zinc-900/50 border border-amber-500/20 rounded-xl p-6 flex flex-col items-center justify-center">
                <span className="w-6 h-6 border-2 border-amber-500 border-t-transparent rounded-full animate-spin mb-2"></span>
                <span className="text-sm text-zinc-400">Scanning Anti-Hallucination Matrix...</span>
            </div>
        );
    }

    if (tasks.length === 0) {
        return (
            <div className="bg-zinc-900/50 border border-green-500/20 rounded-xl p-6 flex flex-col items-center justify-center text-center">
                <CheckCircle className="w-8 h-8 text-green-500 mb-2" />
                <h3 className="text-lg font-bold text-white">Zero Hallucinations Detected</h3>
                <p className="text-zinc-400 text-sm">The pipeline is clean. No manual verifications required.</p>
            </div>
        );
    }

    return (
        <div className="bg-zinc-900/50 border border-amber-500/30 rounded-xl overflow-hidden shadow-lg shadow-black/50">
            <div className="bg-amber-500/10 border-b border-amber-500/20 p-4 shrink-0 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <AlertTriangle className="w-5 h-5 text-amber-500" />
                    <h3 className="font-bold text-amber-500 uppercase tracking-widest text-sm">Awaiting Human Verification</h3>
                </div>
                <span className="bg-amber-500 text-black text-xs font-bold px-2 py-0.5 rounded-full">{tasks.length}</span>
            </div>

            <div className="flex flex-col max-h-[400px] overflow-y-auto">
                {tasks.map(task => (
                    <div key={task.id} className="p-4 border-b border-white/5 hover:bg-white/5 transition-colors flex items-center justify-between gap-4">
                        <div className="flex-1">
                            <h4 className="font-bold text-white text-sm">{task.title}</h4>
                            <p className="text-xs text-zinc-400 mt-1">{task.description}</p>
                            <span className="text-[10px] text-zinc-500 block mt-2 font-mono">
                                LOGGED: {new Date(task.timestamp).toLocaleString()}
                            </span>
                        </div>
                        <Link href={task.actionLink} className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg text-xs font-bold transition-all border border-zinc-700 shrink-0">
                            {task.type === 'reply' ? 'Review Dossier' : 'Inspect Asset'}
                            <ArrowRight className="w-4 h-4" />
                        </Link>
                    </div>
                ))}
            </div>
        </div>
    );
}
