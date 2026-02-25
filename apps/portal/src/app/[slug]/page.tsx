import React from 'react';
import { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';
import { notFound } from 'next/navigation';
import { createClient } from '@supabase/supabase-js';

// Init Supabase Client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY || '';

// Add a fallback if keys exist but we are in server mode
const supabase = createClient(supabaseUrl, supabaseKey);

// Revalidate this page every 24 hours to keep SEO fast but updated
export const revalidate = 86400;

// Dynamic Metadata Generation
export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
    const { data: page } = await supabase
        .from('seo_landing_pages')
        .select('page_title, meta_description')
        .eq('slug', params.slug)
        .single();

    if (!page) {
        return {
            title: 'Sovereign Empire AI',
            description: 'Advanced AI solutions for local businesses.'
        };
    }

    return {
        title: page.page_title,
        description: page.meta_description,
    };
}

export default async function DynamicSeoPage({ params }: { params: { slug: string } }) {
    // 1. Fetch exact page data from Supabase DB
    const { data: page } = await supabase
        .from('seo_landing_pages')
        .select('*')
        .eq('slug', params.slug)
        .single();

    // 2. If no data exists in DB, return a 404 naturally
    if (!page) {
        notFound();
    }

    const { keyword, industry, location, page_title, meta_description, content_data } = page;

    // 3. Render premium template with Dynamic Data
    const schemaData = {
        '@context': 'https://schema.org',
        '@type': 'Service',
        'name': page_title,
        'provider': {
            '@type': 'LocalBusiness',
            'name': 'AI Service Co',
            'url': 'https://aiserviceco.com'
        },
        'areaServed': {
            '@type': 'City',
            'name': location.split(',')[0].trim(),
            'addressRegion': 'FL'
        }
    };

    return (
        <div className="min-h-screen bg-zinc-50 font-sans text-zinc-900">
            <Script
                id={`schema-${params.slug}`}
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaData) }}
            />

            <nav className="py-4 px-8 text-sm text-zinc-500 border-b border-zinc-200 bg-white shadow-sm">
                <Link href="/" className="hover:text-blue-600 transition-colors">AI Service Co</Link>
                <span className="mx-3 text-zinc-300">/</span>
                <span className="capitalize hover:text-blue-600 cursor-pointer transition-colors">Solutions</span>
                <span className="mx-3 text-zinc-300">/</span>
                <span className="text-zinc-800 font-bold">{industry} in {location}</span>
            </nav>

            <main className="max-w-4xl mx-auto px-6 md:px-8 py-12 md:py-20 animate-fade-in-up">
                <div className="p-8 md:p-12 bg-white border border-zinc-200 rounded-3xl shadow-sm mb-12 hover:shadow-lg transition-shadow duration-500">
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-6">
                        <div>
                            <div className="inline-flex items-center px-4 py-1.5 bg-blue-50/80 text-blue-700 border border-blue-100/50 text-xs font-bold rounded-full mb-6 shadow-sm">
                                <span className="w-2 h-2 rounded-full bg-blue-500 mr-2 animate-pulse"></span>
                                Hyper-Local Industry Solution
                            </div>
                            <h1 className="text-4xl md:text-6xl font-black mb-4 text-zinc-900 tracking-tight leading-tight">
                                {keyword} for {industry} <br className="hidden md:block" />
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">in {location}</span>
                            </h1>
                        </div>
                    </div>

                    <div className="prose prose-zinc max-w-none md:text-lg leading-relaxed text-zinc-600 font-medium mb-10">
                        <p>{meta_description}</p>
                    </div>

                    <div className="flex flex-col sm:flex-row gap-4 border-t border-zinc-100 pt-8">
                        <Link href="/assessment" className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl transition-all shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 text-center flex-1 sm:flex-none">
                            Calculate Your AI Score
                        </Link>
                        <a href="tel:13527585336" className="px-8 py-4 bg-zinc-100 hover:bg-zinc-200 text-zinc-800 font-bold rounded-xl transition-colors text-center flex-1 sm:flex-none">
                            Call Our AI Now
                        </a>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
                    <div className="p-8 bg-white border border-zinc-200 rounded-3xl hover:-translate-y-1 transition-transform duration-300 shadow-sm hover:shadow-md">
                        <div className="w-12 h-12 bg-blue-50 rounded-2xl flex items-center justify-center mb-6">
                            <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                        </div>
                        <h3 className="text-xl font-bold mb-3">{content_data?.features?.[0] || "24/7 Booking"}</h3>
                        <p className="text-zinc-500 text-sm leading-relaxed">Never miss a late-night emergency call. Our AI books jobs directly onto your calendar while you sleep.</p>
                    </div>
                    <div className="p-8 bg-white border border-zinc-200 rounded-3xl hover:-translate-y-1 transition-transform duration-300 shadow-sm hover:shadow-md">
                        <div className="w-12 h-12 bg-indigo-50 rounded-2xl flex items-center justify-center mb-6">
                            <svg className="w-6 h-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" /></svg>
                        </div>
                        <h3 className="text-xl font-bold mb-3">{content_data?.features?.[2] || "Human-Like Voice"}</h3>
                        <p className="text-zinc-500 text-sm leading-relaxed">Indistinguishable from a trained front-desk agent. Friendly, empathetic, and strictly adheres to your business rules.</p>
                    </div>
                    <div className="p-8 bg-white border border-zinc-200 rounded-3xl hover:-translate-y-1 transition-transform duration-300 shadow-sm hover:shadow-md">
                        <div className="w-12 h-12 bg-emerald-50 rounded-2xl flex items-center justify-center mb-6">
                            <svg className="w-6 h-6 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                        </div>
                        <h3 className="text-xl font-bold mb-3">{content_data?.features?.[1] || "Instant Deployment"}</h3>
                        <p className="text-zinc-500 text-sm leading-relaxed">No payroll, no sick days, no training periods. The AI is deployed instantly and knows your entire service catalog.</p>
                    </div>
                </div>

            </main>
        </div>
    );
}
