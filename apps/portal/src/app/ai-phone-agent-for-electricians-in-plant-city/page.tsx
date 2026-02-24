import React from 'react';
import { Metadata } from 'next';
import Link from 'next/link';
import Script from 'next/script';

export const metadata: Metadata = {
    title: "AI Phone Agent for Electricians in Plant City, FL | AI Service Co",
    description: "AI Service Co provides advanced 24/7 AI Phone Agents for Electricians in the Plant City area. Stop missing calls and start booking more revenue automatically.",
};

export default function AgencySeoPage() {
    const schemaData = {
        '@context': 'https://schema.org', 
        '@type': 'Service', 
        'name': 'AI Phone Agent for Electricians in Plant City, FL', 
        'provider': {
            '@type': 'LocalBusiness', 
            'name': 'AI Service Co', 
            'url': 'https://aiserviceco.com'
        }, 
        'areaServed': {
            '@type': 'City', 
            'name': 'Plant City', 
            'addressRegion': 'FL'
        }
    };

    return (
        <div className="min-h-screen bg-zinc-50 font-sans text-zinc-900">
            <Script
                id="schema-ai-phone-agent-for-electricians-in-plant-city"
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaData) }}
            />
            
            <nav className="py-4 px-8 text-sm text-zinc-500 border-b border-zinc-200 bg-white">
                <Link href="/" className="hover:text-blue-600">AI Service Co</Link>
                <span className="mx-2">›</span>
                <span className="capitalize hover:text-blue-600">Solutions</span>
                <span className="mx-2">›</span>
                <span className="text-zinc-800 font-bold">Electricians in Plant City</span>
            </nav>

            <main className="max-w-4xl mx-auto px-8 py-16">
                <div className="p-8 bg-white border border-zinc-200 rounded-2xl shadow-sm mb-8">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <div className="inline-block px-3 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded-full mb-4">Industry Solution</div>
                            <h1 className="text-5xl font-black mb-2 text-zinc-900 tracking-tight">AI Phone Agent for Electricians <br/>in <span className="text-blue-600">Plant City, FL</span></h1>
                        </div>
                    </div>
                    
                    <div className="prose prose-zinc max-w-none mb-8">
                        <p className="text-lg leading-relaxed text-zinc-700 font-medium">
                            AI Service Co provides advanced 24/7 AI Phone Agents for Electricians in the Plant City area. Stop missing calls and start booking more revenue automatically.
                        </p>
                    </div>
                    
                    <div className="flex gap-4 border-t border-zinc-100 pt-8">
                        <Link href="/assessment" className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl transition-colors shadow-lg shadow-blue-500/30">
                            Calculate Your AI Score
                        </Link>
                        <a href="tel:13527585336" className="px-8 py-4 bg-zinc-100 hover:bg-zinc-200 text-zinc-800 font-bold rounded-xl transition-colors">
                            Call Our AI Now
                        </a>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                    <div className="p-6 bg-white border border-zinc-200 rounded-2xl">
                        <h3 className="text-xl font-bold mb-2">24/7 Booking</h3>
                        <p className="text-zinc-500 text-sm">Never miss a late-night emergency call. Our AI books jobs directly onto your calendar while you sleep.</p>
                    </div>
                    <div className="p-6 bg-white border border-zinc-200 rounded-2xl">
                        <h3 className="text-xl font-bold mb-2">Human-Like Voice</h3>
                        <p className="text-zinc-500 text-sm">Indistinguishable from a trained front-desk agent. Friendly, empathetic, and strictly adheres to your business rules.</p>
                    </div>
                    <div className="p-6 bg-white border border-zinc-200 rounded-2xl">
                        <h3 className="text-xl font-bold mb-2">Zero Training</h3>
                        <p className="text-zinc-500 text-sm">No payroll, no sick days, no training periods. The AI is deployed instantly and knows your entire service catalog.</p>
                    </div>
                </div>

                <div className="p-8 bg-white border border-zinc-200 rounded-2xl shadow-sm">
                    <h2 className="text-2xl font-bold mb-4">Other Solutions You Might Explore</h2>
                    <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                        <li><Link href="/ai-secretary-for-movers-in-fort-myers" className="text-blue-600 hover:underline">AI Secretary for Movers in Fort Myers</Link></li>
                        <li><Link href="/ai-secretary-for-movers-in-clearwater" className="text-blue-600 hover:underline">AI Secretary for Movers in Clearwater</Link></li>
                        <li><Link href="/voice-ai-for-movers-in-st-petersburg" className="text-blue-600 hover:underline">Voice AI for Movers in St. Petersburg</Link></li>
                        <li><Link href="/automated-booking-system-for-pest-control-in-fort-myers" className="text-blue-600 hover:underline">Automated Booking System for Pest Control in Fort Myers</Link></li>
                        <li><Link href="/voice-ai-for-plumbers-in-st-petersburg" className="text-blue-600 hover:underline">Voice AI for Plumbers in St. Petersburg</Link></li>
                        <li><Link href="/voice-ai-for-pest-control-in-clearwater" className="text-blue-600 hover:underline">Voice AI for Pest Control in Clearwater</Link></li>
                        <li><Link href="/automated-booking-system-for-general-contractors-in-ocala" className="text-blue-600 hover:underline">Automated Booking System for General Contractors in Ocala</Link></li>
                        <li><Link href="/ai-receptionist-for-hvac-in-melbourne" className="text-blue-600 hover:underline">AI Receptionist for HVAC in Melbourne</Link></li>
                        <li><Link href="/voice-ai-for-landscapers-in-sarasota" className="text-blue-600 hover:underline">Voice AI for Landscapers in Sarasota</Link></li>
                        <li><Link href="/automated-booking-system-for-general-contractors-in-lakeland" className="text-blue-600 hover:underline">Automated Booking System for General Contractors in Lakeland</Link></li>
                    </ul>
                </div>
            </main>
        </div>
    );
}
