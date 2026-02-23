import React from 'react';
import { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';

export const metadata: Metadata = {
    title: "Bay To Bay Appliance Repair | Best Appliance Repair in Lakeland",
    description: "Dealing with a broken appliance in Lakeland, FL? Bay To Bay Appliance Repair is your premier local Appliance Repair partner, dedicated to restoring co...",
};

export default function BusinessProfilePage() {
    const schemaData = {'@context': 'https://schema.org', '@type': 'LocalBusiness', 'name': 'Bay To Bay Appliance Repair', 'telephone': '(813) 704-5045', 'url': 'https://lakelandfinds.com/lakeland/appliance-repair/bay-to-bay-appliance-repair', 'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': '5.0', 'reviewCount': '1'}, 'address': {'@type': 'PostalAddress', 'addressLocality': 'Lakeland', 'addressRegion': 'FL'}};

    return (
        <div className="min-h-screen bg-zinc-50 font-sans text-zinc-900">
            <Script
                id="schema-bay-to-bay-appliance-repair"
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
                <span className="text-zinc-800 font-bold">Bay To Bay Appliance Repair</span>
            </nav>

            <main className="max-w-4xl mx-auto px-8 py-16">
                <div className="p-8 bg-white border border-zinc-200 rounded-2xl shadow-sm mb-8">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <h1 className="text-4xl font-black mb-2 text-zinc-900">Bay To Bay Appliance Repair</h1>
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
                            Dealing with a broken appliance in Lakeland, FL? Bay To Bay Appliance Repair is your premier local Appliance Repair partner, dedicated to restoring convenience to your home. We understand the frustration and disruption a faulty refrigerator, oven, dishwasher, or washing machine can cause. As a trusted local Appliance Repair service, we proudly serve homeowners throughout Lakeland and the wider Polk county area. Our team of certified and professional technicians brings extensive experience to every job, offering prompt, efficient, and trustworthy solutions for all major appliance brands. We prioritize clear communication, fair pricing, and lasting repairs. For reliable Appliance Repair in Lakeland FL, choose the experts who care. Don't let appliance troubles slow you down – contact Bay To Bay Appliance Repair today for exceptional service you can depend on. We're committed to keeping your household running smoothly.
                        </p>
                    </div>
                    
                    <div className="flex gap-4 border-t border-zinc-100 pt-8">
                        <a href="tel:(813) 704-5045" className="px-8 py-4 bg-amber-500 hover:bg-amber-600 text-white font-bold rounded-xl transition-colors">Call Now</a>
                        
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
