import React from 'react';
import { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';

export const metadata: Metadata = {
    title: "Kneeland TV & Appliance Service | Best Appliance Repair in Lakeland",
    description: "Experiencing appliance trouble in Lakeland, FL? Kneeland TV & Appliance Service is your trusted local Appliance Repair expert. For decades, we've prov...",
};

export default function BusinessProfilePage() {
    const schemaData = {'@context': 'https://schema.org', '@type': 'LocalBusiness', 'name': 'Kneeland TV & Appliance Service', 'telephone': '(863) 858-4695', 'url': 'https://lakelandfinds.com/lakeland/appliance-repair/kneeland-tv-appliance-service', 'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': '5.0', 'reviewCount': '1'}, 'address': {'@type': 'PostalAddress', 'addressLocality': 'Lakeland', 'addressRegion': 'FL'}};

    return (
        <div className="min-h-screen bg-zinc-50 font-sans text-zinc-900">
            <Script
                id="schema-kneeland-tv-appliance-service"
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaData) }}
            />
            
            <nav className="py-4 px-8 text-sm text-zinc-500 border-b border-zinc-200 bg-white">
                <Link href="/" className="hover:text-amber-500">Home</Link>
                <span className="mx-2">›</span>
                <Link href="/lakeland" className="hover:text-amber-500">Lakeland</Link>
                <span className="mx-2">›</span>
                <Link href="/lakeland/appliance-repair" className="hover:text-amber-500 capitalize">Appliance Repair</Link>
                <span className="mx-2">›</span>
                <span className="text-zinc-800 font-bold">Kneeland TV & Appliance Service</span>
            </nav>

            <main className="max-w-4xl mx-auto px-8 py-16">
                <div className="p-8 bg-white border border-zinc-200 rounded-2xl shadow-sm mb-8">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <h1 className="text-4xl font-black mb-2 text-zinc-900">Kneeland TV & Appliance Service</h1>
                            <div className="flex gap-4 text-sm text-zinc-500">
                                <span>📍 Lakeland, FL</span>
                                <span className="text-amber-500 font-bold">★ 5.0 (Recent Reviews)</span>
                            </div>
                        </div>
                        {/* Claim Profile Upsell */}
                        <div className="text-right">
                             <div className="inline-block px-3 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full mb-2">Verified Listing</div>
                             <br/>
                             <Link href="/assessment" className="text-xs font-bold text-blue-600 hover:text-blue-500 underline">Claim this profile</Link>
                        </div>
                    </div>
                    
                    <div className="prose prose-zinc max-w-none mb-8">
                        <p className="text-lg leading-relaxed text-zinc-700">
                            Experiencing appliance trouble in Lakeland, FL? Kneeland TV & Appliance Service is your trusted local Appliance Repair expert. For decades, we've provided reliable, efficient appliance repair solutions across Polk county, ensuring your home runs smoothly and stress-free. From refrigerators refusing to cool, washers that won't spin, or ovens that won't heat, our certified technicians skillfully diagnose and repair all major brands and models with professionalism and precision. We understand the major inconvenience a broken appliance causes, which is why we prioritize prompt, honest service you can truly depend on. When you need expert Appliance Repair in Lakeland FL, trust our experienced, friendly team to get your household appliances working like new again. We're proud to offer top-tier local Appliance Repair to our neighbors throughout Lakeland and the surrounding Polk county communities, committed to your complete satisfaction. Contact Kneeland TV & Appliance Service today for dependable, professional service you can trust.
                        </p>
                    </div>
                    
                    <div className="flex gap-4 border-t border-zinc-100 pt-8">
                        <a href="tel:(863) 858-4695" className="px-8 py-4 bg-amber-500 hover:bg-amber-600 text-white font-bold rounded-xl transition-colors">Call Now</a>
                        
                    </div>
                </div>

                {/* AI Service Co Upsell Widget */}
                <div className="p-8 bg-zinc-900 text-white rounded-2xl flex flex-col md:flex-row gap-8 items-center justify-between border-l-4 border-purple-500">
                    <div>
                        <div className="text-sm font-bold text-purple-400 mb-2 uppercase tracking-widest">Business Owner Tools</div>
                        <h3 className="text-2xl font-bold mb-2">Automate Your Operations</h3>
                        <p className="text-zinc-400">Stop missing calls when on the job. Install an AI Secretary to answer 24/7 and book appointments autonomously.</p>
                    </div>
                    <Link href="/assessment" className="px-8 py-4 bg-purple-600 hover:bg-purple-700 font-bold rounded-xl whitespace-nowrap transition-colors">
                        Calculate AI Score
                    </Link>
                </div>
            </main>
        </div>
    );
}
