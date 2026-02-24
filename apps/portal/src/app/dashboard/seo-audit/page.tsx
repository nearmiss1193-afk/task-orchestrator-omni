import React from 'react';
import Link from 'next/link';
import fs from 'fs';
import path from 'path';

export default async function SeoAuditDashboard() {
    let routes: string[] = [];
    try {
        const filePath = path.join(process.cwd(), 'src/app/dashboard/seo_routes.json');
        const fileContent = fs.readFileSync(filePath, 'utf-8');
        routes = JSON.parse(fileContent);
    } catch (e) {
        console.error("Failed to load SEO routes:", e);
    }

    return (
        <div className="min-h-screen bg-slate-950 text-slate-200 p-8 font-sans">
            <div className="max-w-6xl mx-auto">
                <div className="mb-8 border-b border-slate-800 pb-6 flex justify-between items-end">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
                            <span className="bg-indigo-600 p-2 rounded-lg">
                                <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                            </span>
                            Abacus SEO Audit Deck
                        </h1>
                        <p className="text-slate-400 mt-2">
                            Reviewing {routes.length} auto-generated SEO landing pages before Vercel Deployment.
                        </p>
                    </div>
                </div>

                {routes.length === 0 ? (
                    <div className="p-8 text-center bg-slate-900 border border-slate-800 rounded-xl text-slate-500">
                        No SEO routes loaded. Ensure scripts have run.
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {routes.map((route, i) => (
                            <Link
                                href={route}
                                key={i}
                                target="_blank"
                                className="p-4 bg-slate-900 border border-slate-800 rounded-lg hover:border-indigo-500 hover:bg-slate-800 transition-colors flex items-center justify-between group"
                            >
                                <span className="truncate text-sm font-medium text-slate-300 group-hover:text-white">
                                    {route}
                                </span>
                                <svg className="w-4 h-4 text-slate-600 group-hover:text-indigo-400 shrink-0 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                </svg>
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
