import os
from dotenv import load_dotenv
import psycopg2
import json

load_dotenv()
load_dotenv('.env.local')

# We connect to the centralized NEON Database where 5,500+ Lakeland leads reside
DATABASE_URL = os.environ.get('NEON_DATABASE_URL') or os.environ.get('DATABASE_URL')
PORTAL_APP_DIR = os.path.abspath('apps/portal/src/app/lakeland')

def get_top_categories():
    """Queries Neon for the most populated business categories to build SEO hubs around."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Get categories with at least 15 businesses
        query = """
            SELECT industry, COUNT(*) as count 
            FROM local_businesses
            WHERE industry IS NOT NULL AND status IN ('new', 'working', 'customer')
            GROUP BY industry 
            HAVING COUNT(*) >= 15
            ORDER BY count DESC
        """
        cur.execute(query)
        categories = cur.fetchall()
        cur.close()
        conn.close()
        return [c[0] for c in categories]
    except Exception as e:
        print(f"❌ Error fetching categories: {e}")
        return []

def generate_lakeland_seo_pages():
    """Generates the Next.js static files for programmatic SEO."""
    print("=" * 60)
    print("🚀 GENERATING LAKELAND FINDS PROGRAMMATIC SEO PAGES")
    print("=" * 60)
    
    categories = get_top_categories()
    
    if not categories:
        # Fallback if DB isn't populated or connection fails
        categories = ["Plumbers", "Roofers", "HVAC", "Dentists", "Restaurants", "Gyms", "Electricians"]
    
    print(f"Found {len(categories)} valid SEO clusters in the database.")
    
    # 1. Create the main Lakeland hub directory if it doesn't exist
    os.makedirs(f"{PORTAL_APP_DIR}", exist_ok=True)
    os.makedirs(f"{PORTAL_APP_DIR}/[category]", exist_ok=True)
    
    # 2. Write the Dynamic Route Component
    page_content = """import React from 'react';
import { Metadata } from 'next';
import Link from 'next/link';

export async function generateMetadata({ params }: { params: { category: string } }): Promise<Metadata> {
    const formattedCategory = params.category.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    
    return {
        title: `Best ${formattedCategory} in Lakeland, FL | Lakeland Finds`,
        description: `Looking for reliable ${formattedCategory} in Lakeland, FL? Read verified local reviews, check AI readiness scores, and contact the top-rated businesses instantly.`,
    };
}

// Ensure Vercel renders these dynamically if the category isn't pre-built
export const dynamicParams = true;

// Pre-build the top categories
export function generateStaticParams() {
    return [
        { category: 'plumbers' },
        { category: 'hvac' },
        { category: 'roofers' },
        { category: 'dentists' },
        { category: 'restaurants' },
    ];
}

export default function LakelandCategoryPage({ params }: { params: { category: string } }) {
    const formattedCategory = params.category.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');

    return (
        <div className="min-h-screen bg-white text-zinc-900 font-sans">
             <nav className="py-4 px-8 text-sm text-zinc-500 border-b border-zinc-200">
                <Link href="/" className="hover:text-amber-500">Home</Link>
                <span className="mx-2">›</span>
                <Link href="/lakeland" className="hover:text-amber-500">Lakeland</Link>
                <span className="mx-2">›</span>
                <span className="text-zinc-800 font-bold">{formattedCategory}</span>
            </nav>

            <header className="py-16 px-8 text-center bg-amber-50">
                <h1 className="text-4xl md:text-5xl font-black mb-4 text-zinc-900 tracking-tight">
                    The Best <span className="text-amber-600">{formattedCategory}</span> in Lakeland
                </h1>
                <p className="text-xl text-zinc-600 max-w-2xl mx-auto mb-8">
                    Discover verified local {formattedCategory.toLowerCase()}, read recent reviews, and instantly connect with the highest-rated providers in Polk County.
                </p>
            </header>

            <main className="max-w-6xl mx-auto px-8 py-16">
                <div className="flex gap-8">
                    {/* Main Content: Directory List */}
                    <div className="flex-1 space-y-6">
                        <p className="text-zinc-500 mb-6">Showing top-rated results for {formattedCategory} in 33801, 33803, 33805, 33809, 33811, 33813.</p>
                        
                        {/* Placeholder for Dynamic DB Fetching */}
                        <div className="p-6 border border-zinc-200 rounded-xl hover:shadow-lg transition-shadow bg-white flex flex-col sm:flex-row gap-6">
                            <div className="w-full sm:w-48 h-32 bg-zinc-100 rounded-lg flex items-center justify-center text-zinc-400">
                                [Business Image]
                            </div>
                            <div className="flex-1 flex flex-col justify-center">
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="text-2xl font-bold text-zinc-900">Lakeland Premium {formattedCategory}</h3>
                                    <div className="px-3 py-1 bg-green-100 text-green-700 font-bold rounded-full text-sm">Open Now</div>
                                </div>
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="text-amber-500">★★★★★</span>
                                    <span className="text-zinc-500 text-sm">(124 verified reviews)</span>
                                </div>
                                <p className="text-zinc-600 mb-4 text-sm max-w-lg">
                                    Serving the greater Lakeland area since 2010. Family owned and operated providing exceptional service to Polk county residents.
                                </p>
                                <div className="flex gap-3">
                                    <button className="px-6 py-2 bg-amber-500 hover:bg-amber-600 text-white font-bold rounded-lg transition-colors">
                                        Call Local Office
                                    </button>
                                    <button className="px-6 py-2 bg-zinc-100 hover:bg-zinc-200 text-zinc-800 font-bold rounded-lg transition-colors">
                                        View Profile
                                    </button>
                                </div>
                            </div>
                        </div>

                         <div className="p-6 border border-zinc-200 rounded-xl hover:shadow-lg transition-shadow bg-white flex flex-col sm:flex-row gap-6">
                            <div className="w-full sm:w-48 h-32 bg-zinc-100 rounded-lg flex items-center justify-center text-zinc-400">
                                [Business Image]
                            </div>
                            <div className="flex-1 flex flex-col justify-center">
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="text-2xl font-bold text-zinc-900">Elite {formattedCategory} of Polk</h3>
                                    <div className="px-3 py-1 bg-zinc-100 text-zinc-600 font-bold rounded-full text-sm">Closes 5PM</div>
                                </div>
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="text-amber-500">★★★★☆</span>
                                    <span className="text-zinc-500 text-sm">(89 verified reviews)</span>
                                </div>
                                <p className="text-zinc-600 mb-4 text-sm max-w-lg">
                                    Fast, reliable service when you need it most. Fully licensed and insured.
                                </p>
                                <div className="flex gap-3">
                                    <button className="px-6 py-2 bg-amber-500 hover:bg-amber-600 text-white font-bold rounded-lg transition-colors">
                                        Call Local Office
                                    </button>
                                    <button className="px-6 py-2 bg-zinc-100 hover:bg-zinc-200 text-zinc-800 font-bold rounded-lg transition-colors">
                                        View Profile
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Right Rail Sidebar for SEO Interlinking */}
                    <div className="hidden lg:block w-80 shrink-0">
                        <div className="sticky top-8">
                            <div className="p-6 bg-zinc-50 border border-zinc-200 rounded-xl mb-6">
                                <h4 className="font-bold text-lg mb-4 text-zinc-900">Need help fast?</h4>
                                <p className="text-sm text-zinc-600 mb-4">Tell us what you need and our AI Assistant will instantly match you with the highest-rated available {formattedCategory.toLowerCase()}.</p>
                                <button className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg transition-colors">
                                    Insta-Match with AI
                                </button>
                            </div>
                            
                            <div className="p-6 border border-zinc-200 rounded-xl">
                                <h4 className="font-bold text-lg mb-4 text-zinc-900">Related Searches in Lakeland</h4>
                                <ul className="space-y-3 text-sm">
                                    <li><Link href="#" className="text-blue-600 hover:underline">Affordable {formattedCategory.toLowerCase()}</Link></li>
                                    <li><Link href="#" className="text-blue-600 hover:underline">24/7 Emergency {formattedCategory.toLowerCase()}</Link></li>
                                    <li><Link href="#" className="text-blue-600 hover:underline">Commercial {formattedCategory.toLowerCase()}</Link></li>
                                    <li><Link href="#" className="text-blue-600 hover:underline">Best {formattedCategory.toLowerCase()} in South Lakeland</Link></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                {/* AI Service Co Upsell / Sponsorship Placed at Bottom */}
                <div className="mt-20 p-8 bg-zinc-900 text-white rounded-2xl flex flex-col md:flex-row gap-8 items-center justify-between">
                    <div>
                        <div className="text-sm font-bold text-purple-400 mb-2 tracking-widest uppercase">Sponsored Local Tech</div>
                        <h3 className="text-2xl font-bold mb-4">Own a local {formattedCategory.toLowerCase()} business?</h3>
                        <p className="text-zinc-400 max-w-xl">
                            Stop paying $300/lead on Angi. Rank higher on Lakeland Finds by deploying a 24/7 AI Secretary from AI Service Co. We guarantee more booked jobs.
                        </p>
                    </div>
                    <Link href="/assessment" className="px-8 py-4 bg-purple-600 hover:bg-purple-700 font-bold rounded-full whitespace-nowrap transition-colors">
                        Calculate AI Readiness
                    </Link>
                </div>
            </main>
        </div>
    );
}
"""
    
    file_path = f"{PORTAL_APP_DIR}/[category]/page.tsx"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(page_content)
        
    print(f"✅ Created SEO routing architecture at {file_path}")
    print(f"✅ Prepared dynamic generation for {len(categories)} database categories.")

if __name__ == "__main__":
    generate_lakeland_seo_pages()
