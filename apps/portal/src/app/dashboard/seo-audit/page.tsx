import React from 'react';
import Link from 'next/link';
import { createClient } from '@supabase/supabase-js';

// Revalidate every minute to keep the audit fresh
export const revalidate = 60;

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY || '';
const supabase = createClient(supabaseUrl, supabaseKey);

export default async function SeoAuditDashboard() {
    let routes: { slug: string, industry: string, location: string }[] = [];
    try {
        const { data, error } = await supabase
            .from('seo_landing_pages')
            .select('slug, industry, location')
            .order('industry', { ascending: true })
            .order('location', { ascending: true });

        if (data && !error) {
            routes = data;
        }
    } catch (e) {
        console.error("Failed to load SEO routes from Supabase:", e);
    }

    return (
        <div className="min-h-screen bg-slate-950 text-slate-200 p-8 font-sans">
            <div className="max-w-7xl mx-auto">
                <div className="mb-8 flex flex-col md:flex-row justify-between items-start md:items-end gap-4 border-b border-slate-800 pb-6">
                    <div>
                        <div className="inline-flex items-center px-3 py-1 bg-indigo-500/10 text-indigo-400 border border-indigo-500/50 text-xs font-bold rounded-full mb-3">
                            <span className="w-2 h-2 rounded-full bg-indigo-500 mr-2 animate-pulse"></span>
                            Live Database connection
                        </div>
                        <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-white flex items-center gap-3">
                            Abacus SEO Audit Deck
                        </h1>
                        <p className="text-slate-400 mt-2 text-lg">
                            Reviewing {routes.length} Database-driven dynamic SEO landing pages.
                        </p>
                    </div>
                </div>

                {routes.length === 0 ? (
                    <div className="p-12 text-center bg-slate-900 border border-slate-800 rounded-xl text-slate-500">
                        <svg className="w-12 h-12 mx-auto mb-4 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                        </svg>
                        No programmatic SEO routes found in Supabase. Ensure migration script has run.
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                        {routes.map((route, i) => (
                            <Link
                                href={`/${route.slug}`}
                                key={i}
                                target="_blank"
                                className="p-5 bg-slate-900 border border-slate-800 rounded-xl hover:border-indigo-500 hover:bg-slate-800 hover:-translate-y-1 transition-all group flex flex-col justify-between h-full relative overflow-hidden"
                            >
                                <div className="absolute top-0 right-0 p-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <svg className="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                    </svg>
                                </div>
                                <div>
                                    <div className="text-xs font-semibold text-indigo-400 mb-1 uppercase tracking-wider">{route.industry}</div>
                                    <div className="text-white font-medium text-lg leading-tight mb-3 group-hover:text-indigo-300 transition-colors">
                                        {route.location}
                                    </div>
                                </div>
                                <div className="text-xs text-slate-500 font-mono truncate bg-slate-950 p-2 rounded border border-slate-800/50">
                                    /{route.slug}
                                </div>
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
