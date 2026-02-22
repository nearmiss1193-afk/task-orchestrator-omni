'use client';

import React, { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabaseClient';

export default function SocialKanbanHUD() {
    const [drafts, setDrafts] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSocialQueue = async () => {
            setLoading(true);
            try {
                // First try the dedicated table
                const { data: dedicatedData, error: dedicatedErr } = await supabase
                    .from('social_drafts')
                    .select('*')
                    .order('created_at', { ascending: false });

                let allDrafts: any[] = [];

                if (!dedicatedErr && dedicatedData && dedicatedData.length > 0) {
                    allDrafts = dedicatedData;
                } else {
                    // Fallback: Parse the raw_research json schema inside contacts_master
                    const { data: contactData, error: contactErr } = await supabase
                        .from('contacts_master')
                        .select('id, company_name, raw_research')
                        .eq('status', 'research_done')
                        .is('ai_paused', false);

                    if (!contactErr && contactData) {
                        contactData.forEach(contact => {
                            try {
                                const raw = JSON.parse(contact.raw_research || '{}');
                                const embeddedDrafts = raw.social_drafts || [];
                                embeddedDrafts.forEach((d: any) => {
                                    allDrafts.push({
                                        ...d,
                                        id: `${contact.id}_${d.platform}`,
                                        lead_id: contact.id,
                                        company_name: contact.company_name
                                    });
                                });
                            } catch (e) { }
                        });
                    }
                }

                setDrafts(allDrafts);
            } catch (e) {
                console.error("Failed to load Social Matrix", e);
            } finally {
                setLoading(false);
            }
        };

        fetchSocialQueue();
    }, []);

    const handlePublishClick = async (draft: any) => {
        // Optimistic UI Update
        setDrafts(prev => prev.map(d => d.id === draft.id ? { ...d, status: 'publishing' } : d));

        try {
            const res = await fetch('/api/social-override', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    platform: draft.platform,
                    content: draft.content,
                    video_url: draft.video_url || draft.metadata?.video_url
                })
            });

            if (!res.ok) throw new Error("API Failure");

            // Successfully published, move to Published column
            setDrafts(prev => prev.map(d => d.id === draft.id ? { ...d, status: 'published' } : d));
        } catch (err) {
            console.error("Publishing Override Failed", err);
            // Revert optimistic update
            alert("Ayrshare Edge Route failed to publish asset.");
            setDrafts(prev => prev.map(d => d.id === draft.id ? { ...d, status: 'draft' } : d));
        }
    };

    const getPlatformIcon = (platform: string) => {
        switch (platform.toLowerCase()) {
            case 'linkedin': return <span className="text-blue-500 font-bold">in</span>;
            case 'x':
            case 'twitter': return <span className="text-slate-200 font-bold">X</span>;
            case 'instagram': return <span className="text-pink-500 font-bold">IG</span>;
            case 'facebook': return <span className="text-blue-600 font-bold">f</span>;
            case 'tiktok': return <span className="text-fuchsia-500 font-bold">TT</span>;
            case 'youtube': return <span className="text-red-500 font-bold">YT</span>;
            default: return <span>{platform.substring(0, 2).toUpperCase()}</span>;
        }
    };

    const columns = ['draft', 'publishing', 'published'];

    return (
        <div className="min-h-screen bg-slate-950 p-8">

            <div className="mb-10">
                <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
                    <svg className="w-8 h-8 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" /></svg>
                    Autonomous Social Asset Queue
                </h1>
                <p className="text-slate-400 mt-2">Visually manage, review, and override Ayrshare posts generated by Sovereign AI.</p>
            </div>

            {loading ? (
                <div className="flex flex-col items-center justify-center p-20 text-slate-500">
                    <span className="w-10 h-10 border-4 border-sky-500 border-t-transparent rounded-full animate-spin mb-4"></span>
                    Loading Semantic Matrix...
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {columns.map(col => {
                        const filteredDrafts = drafts.filter(d => d.status === col);

                        return (
                            <div key={col} className="bg-slate-900/40 border border-slate-800 rounded-2xl flex flex-col max-h-[75vh]">
                                <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/60 rounded-t-2xl">
                                    <h3 className="font-bold text-slate-200 uppercase tracking-widest text-sm">{col}</h3>
                                    <span className="bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full text-xs font-mono">{filteredDrafts.length}</span>
                                </div>

                                <div className="p-4 flex-1 overflow-y-auto space-y-4">
                                    {filteredDrafts.length === 0 ? (
                                        <div className="text-center p-8 text-slate-600 text-sm">No assets in {col}.</div>
                                    ) : (
                                        filteredDrafts.map(draft => (
                                            <div key={draft.id} className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 shadow-xl shadow-black/20 hover:border-sky-500/30 transition-colors group relative">

                                                <div className="flex justify-between items-start mb-3">
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-6 h-6 rounded bg-slate-900 border border-slate-700 flex items-center justify-center text-[10px]">
                                                            {getPlatformIcon(draft.platform)}
                                                        </div>
                                                        <span className="text-xs text-slate-400 font-mono truncate max-w-[120px]">{draft.company_name || draft.metadata?.city || 'Sovereign Brand'}</span>
                                                    </div>

                                                    {col === 'draft' && (
                                                        <button onClick={() => handlePublishClick(draft)} className="opacity-0 group-hover:opacity-100 transition-opacity bg-sky-500 hover:bg-sky-400 text-white text-[10px] uppercase font-bold tracking-wider px-3 py-1 rounded shadow-lg shadow-sky-500/20">
                                                            Deploy
                                                        </button>
                                                    )}
                                                    {col === 'publishing' && (
                                                        <span className="w-4 h-4 border-2 border-sky-400 border-t-transparent rounded-full animate-spin"></span>
                                                    )}
                                                </div>

                                                <p className="text-sm text-slate-300 leading-relaxed max-w-full overflow-hidden text-ellipsis line-clamp-4">
                                                    {draft.content}
                                                </p>

                                                {draft.video_url && (
                                                    <div className="mt-3 text-xs flex items-center gap-1 text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-1 rounded inline-block">
                                                        <svg className="w-3 h-3 inline pb-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
                                                        Rich Media Attached
                                                    </div>
                                                )}
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
