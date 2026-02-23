import React from 'react';
import { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';

export const metadata: Metadata = {
    title: "Galloway Carpet One Floor & Home | Best Hardwood Flooring in Lakeland",
    description: "Transform your home with stunning Hardwood Flooring in Lakeland FL from Galloway Carpet One Floor & Home. As your trusted local Hardwood Flooring expe...",
};

export default function BusinessProfilePage() {
    const schemaData = {'@context': 'https://schema.org', '@type': 'LocalBusiness', 'name': 'Galloway Carpet One Floor & Home', 'telephone': '(863) 209-7041', 'url': 'https://www.gallowaycarpetonelakeland.com/?utm_source=&utm_medium=organic&utm_campaign=gbp-listing&utm_content=Lakeland-showroom', 'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': '5.0', 'reviewCount': '1'}, 'address': {'@type': 'PostalAddress', 'addressLocality': 'Lakeland', 'addressRegion': 'FL'}};

    return (
        <div className="min-h-screen bg-zinc-50 font-sans text-zinc-900">
            <Script
                id="schema-galloway-carpet-one-floor-home"
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaData) }}
            />
            
            <nav className="py-4 px-8 text-sm text-zinc-500 border-b border-zinc-200 bg-white">
                <Link href="/" className="hover:text-amber-500">Home</Link>
                <span className="mx-2">›</span>
                <Link href="/lakeland" className="hover:text-amber-500">Lakeland</Link>
                <span className="mx-2">›</span>
                <Link href="/lakeland/hardwood-flooring" className="hover:text-amber-500 capitalize">Hardwood Flooring</Link>
                <span className="mx-2">›</span>
                <span className="text-zinc-800 font-bold">Galloway Carpet One Floor & Home</span>
            </nav>

            <main className="max-w-4xl mx-auto px-8 py-16">
                <div className="p-8 bg-white border border-zinc-200 rounded-2xl shadow-sm mb-8">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <h1 className="text-4xl font-black mb-2 text-zinc-900">Galloway Carpet One Floor & Home</h1>
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
                            Transform your home with stunning Hardwood Flooring in Lakeland FL from Galloway Carpet One Floor & Home. As your trusted local Hardwood Flooring experts, we've proudly served Lakeland and the wider Polk county area for years, providing unparalleled quality and service. We understand the unique style and needs of our community, offering a vast selection of beautiful, durable hardwood options to elevate any space. Our professional team is dedicated to guiding you through every step, ensuring a seamless experience from selection to expert installation. Choosing hardwood flooring is an investment in your home's beauty and value, and you can trust our reliable, experienced professionals to deliver exceptional results. Discover why so many in Polk county choose us for their flooring needs. Visit Galloway Carpet One Floor & Home today and experience the difference of true local expertise and trustworthy service.
                        </p>
                    </div>
                    
                    <div className="flex gap-4 border-t border-zinc-100 pt-8">
                        <a href="tel:(863) 209-7041" className="px-8 py-4 bg-amber-500 hover:bg-amber-600 text-white font-bold rounded-xl transition-colors">Call Now</a>
                        <a href="https://www.gallowaycarpetonelakeland.com/?utm_source=&utm_medium=organic&utm_campaign=gbp-listing&utm_content=Lakeland-showroom" target="_blank" rel="noopener noreferrer" className="px-8 py-4 bg-zinc-100 hover:bg-zinc-200 text-zinc-800 font-bold rounded-xl transition-colors">Visit Website</a>
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
