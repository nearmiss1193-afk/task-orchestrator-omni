import React from 'react';
import { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';

export const metadata: Metadata = {
    title: "Florida Tile Lakeland | Best Tile Installation in Lakeland",
    description: "Florida Tile Lakeland is your premier choice for expert Tile Installation in Lakeland FL. As a trusted local Tile Installation provider, we are dedica...",
};

export default function BusinessProfilePage() {
    const schemaData = {'@context': 'https://schema.org', '@type': 'LocalBusiness', 'name': 'Florida Tile Lakeland', 'telephone': '(863) 665-4646', 'url': 'https://panariagroupusa.com/floridatile-showroom-lakeland?__hstc=230586243.50e3d4a15783eb962decbdc10768f24b.1751911048540.1761847998429.1761853790791.106&__hssc=230586243.3.1761853790791&__hsfp=1811316718', 'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': '5.0', 'reviewCount': '1'}, 'address': {'@type': 'PostalAddress', 'addressLocality': 'Lakeland', 'addressRegion': 'FL'}};

    return (
        <div className="min-h-screen bg-zinc-50 font-sans text-zinc-900">
            <Script
                id="schema-florida-tile-lakeland"
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaData) }}
            />
            
            <nav className="py-4 px-8 text-sm text-zinc-500 border-b border-zinc-200 bg-white">
                <Link href="/" className="hover:text-amber-500">Home</Link>
                <span className="mx-2">›</span>
                <Link href="/lakeland" className="hover:text-amber-500">Lakeland</Link>
                <span className="mx-2">›</span>
                <Link href="/lakeland/tile-installation" className="hover:text-amber-500 capitalize">Tile Installation</Link>
                <span className="mx-2">›</span>
                <span className="text-zinc-800 font-bold">Florida Tile Lakeland</span>
            </nav>

            <main className="max-w-4xl mx-auto px-8 py-16">
                <div className="p-8 bg-white border border-zinc-200 rounded-2xl shadow-sm mb-8">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <h1 className="text-4xl font-black mb-2 text-zinc-900">Florida Tile Lakeland</h1>
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
                            Florida Tile Lakeland is your premier choice for expert Tile Installation in Lakeland FL. As a trusted local Tile Installation provider, we are dedicated to transforming your spaces with precision and style throughout Polk county. Our professional team brings years of experience to every project, ensuring impeccable results for residential and commercial clients alike. From elegant ceramic and porcelain to durable natural stone and intricate mosaics, we handle all types of tile installations with meticulous attention to detail. We pride ourselves on transparent communication, reliable scheduling, and a steadfast commitment to customer satisfaction from start to finish. Choosing Florida Tile Lakeland means partnering with a local company deeply rooted in the community, providing tailored solutions that enhance your property's value and aesthetics. Discover why so many in Lakeland trust us for their tiling needs. Contact us today for a personalized quote and experience the difference professional installation makes.
                        </p>
                    </div>
                    
                    <div className="flex gap-4 border-t border-zinc-100 pt-8">
                        <a href="tel:(863) 665-4646" className="px-8 py-4 bg-amber-500 hover:bg-amber-600 text-white font-bold rounded-xl transition-colors">Call Now</a>
                        <a href="https://panariagroupusa.com/floridatile-showroom-lakeland?__hstc=230586243.50e3d4a15783eb962decbdc10768f24b.1751911048540.1761847998429.1761853790791.106&__hssc=230586243.3.1761853790791&__hsfp=1811316718" target="_blank" rel="noopener noreferrer" className="px-8 py-4 bg-zinc-100 hover:bg-zinc-200 text-zinc-800 font-bold rounded-xl transition-colors">Visit Website</a>
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
