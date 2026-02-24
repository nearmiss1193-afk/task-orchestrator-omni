import os
import shutil
import random

BASE_DIR = r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\apps\portal\src\app"

NICHES = {
    "plumbers": "Plumbers",
    "roofers": "Roofers",
    "cleaning-services": "Cleaning Services",
    "electricians": "Electricians",
    "general-contractors": "General Contractors",
    "hvac": "HVAC",
    "landscapers": "Landscapers",
    "movers": "Movers",
    "painters": "Painters",
    "pest-control": "Pest Control"
}

CITIES = {
    "lakeland": "Lakeland",
    "orlando": "Orlando",
    "tampa": "Tampa",
    "winter-haven": "Winter Haven",
    "plant-city": "Plant City",
    "kissimmee": "Kissimmee",
    "brandon": "Brandon",
    "st-petersburg": "St. Petersburg",
    "clearwater": "Clearwater",
    "sarasota": "Sarasota",
    "bradenton": "Bradenton",
    "daytona-beach": "Daytona Beach",
    "melbourne": "Melbourne",
    "ocala": "Ocala",
    "gainesville": "Gainesville",
    "jacksonville": "Jacksonville",
    "tallahassee": "Tallahassee",
    "pensacola": "Pensacola",
    "fort-myers": "Fort Myers",
    "naples": "Naples"
}

PHRASES = {
    "ai-secretary": "AI Secretary",
    "ai-phone-agent": "AI Phone Agent",
    "ai-receptionist": "AI Receptionist",
    "automated-booking-system": "Automated Booking System",
    "voice-ai": "Voice AI"
}

TEMPLATE = """import React from 'react';
import {{ Metadata }} from 'next';
import Link from 'next/link';
import Script from 'next/script';

export const metadata: Metadata = {{
    title: "{display_phrase} for {display_niche} in {display_city}, FL | AI Service Co",
    description: "AI Service Co provides advanced 24/7 {display_phrase}s for {display_niche} in the {display_city} area. Stop missing calls and start booking more revenue automatically.",
}};

export default function AgencySeoPage() {{
    const schemaData = {{
        '@context': 'https://schema.org', 
        '@type': 'Service', 
        'name': '{display_phrase} for {display_niche} in {display_city}, FL', 
        'provider': {{
            '@type': 'LocalBusiness', 
            'name': 'AI Service Co', 
            'url': 'https://aiserviceco.com'
        }}, 
        'areaServed': {{
            '@type': 'City', 
            'name': '{display_city}', 
            'addressRegion': 'FL'
        }}
    }};

    return (
        <div className="min-h-screen bg-zinc-50 font-sans text-zinc-900">
            <Script
                id="schema-{url_slug}"
                type="application/ld+json"
                dangerouslySetInnerHTML={{{{ __html: JSON.stringify(schemaData) }}}}
            />
            
            <nav className="py-4 px-8 text-sm text-zinc-500 border-b border-zinc-200 bg-white">
                <Link href="/" className="hover:text-blue-600">AI Service Co</Link>
                <span className="mx-2">›</span>
                <span className="capitalize hover:text-blue-600">Solutions</span>
                <span className="mx-2">›</span>
                <span className="text-zinc-800 font-bold">{display_niche} in {display_city}</span>
            </nav>

            <main className="max-w-4xl mx-auto px-8 py-16">
                <div className="p-8 bg-white border border-zinc-200 rounded-2xl shadow-sm mb-8">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <div className="inline-block px-3 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded-full mb-4">Industry Solution</div>
                            <h1 className="text-5xl font-black mb-2 text-zinc-900 tracking-tight">{display_phrase} for {display_niche} <br/>in <span className="text-blue-600">{display_city}, FL</span></h1>
                        </div>
                    </div>
                    
                    <div className="prose prose-zinc max-w-none mb-8">
                        <p className="text-lg leading-relaxed text-zinc-700 font-medium">
                            AI Service Co provides advanced 24/7 {display_phrase}s for {display_niche} in the {display_city} area. Stop missing calls and start booking more revenue automatically.
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
                        {internal_links}
                    </ul>
                </div>
            </main>
        </div>
    );
}}
"""

def generate():
    # 1. Pre-calculate all 1000 routes
    all_routes = []
    for phrase_slug, phrase_disp in PHRASES.items():
        for niche_slug, niche_disp in NICHES.items():
            for city_slug, city_disp in CITIES.items():
                url_slug = f"{phrase_slug}-for-{niche_slug}-in-{city_slug}"
                
                # Check if it should be just the phrase (edge case logic from v1 if needed, but let's stick to standard)
                if niche_slug == 'none':
                    url_slug = phrase_slug
                    
                all_routes.append({
                    "url_slug": url_slug,
                    "phrase_slug": phrase_slug,
                    "phrase_disp": phrase_disp,
                    "niche_slug": niche_slug,
                    "niche_disp": niche_disp,
                    "city_slug": city_slug,
                    "city_disp": city_disp
                })
                
    print(f"Computed {len(all_routes)} geographic SEO combinations")
    
    # 2. Generate and write
    for route in all_routes:
        # Cross-linking (grab 10 random other routes to build dense mesh)
        cross_links = random.sample([r for r in all_routes if r['url_slug'] != route['url_slug']], 10)
        
        links_jsx = ""
        for cl in cross_links:
            anch = f"{cl['phrase_disp']} for {cl['niche_disp']} in {cl['city_disp']}"
            links_jsx += f'<li><Link href="/{cl["url_slug"]}" className="text-blue-600 hover:underline">{anch}</Link></li>\n                        '
            
        page_content = TEMPLATE.format(
            display_phrase=route['phrase_disp'],
            display_niche=route['niche_disp'],
            display_city=route['city_disp'],
            url_slug=route['url_slug'],
            internal_links=links_jsx.strip()
        )
        
        target_dir = os.path.join(BASE_DIR, route['url_slug'])
        os.makedirs(target_dir, exist_ok=True)
        
        with open(os.path.join(target_dir, "page.tsx"), "w", encoding="utf-8") as f:
            f.write(page_content)
            
    print("All 1000 programmatic pages successfully written to disk with dense internal linking.")

if __name__ == "__main__":
    generate()
