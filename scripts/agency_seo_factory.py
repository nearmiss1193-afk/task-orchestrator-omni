import os
import sys
import time
import google.generativeai as genai
from github import Github, InputGitTreeElement
from dotenv import load_dotenv

# Load env variables (for local testing, CI will inject via secrets)
load_dotenv()

# 1. Configuration
GEMINI_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO = os.environ.get('GITHUB_REPO', 'nearmiss1193/empire-unified')

if not GEMINI_KEY:
    print("❌ FATAL: Missing LLM credentials.")
    sys.exit(1)

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

INDUSTRIES = [
    "Plumbers", "HVAC", "Roofers", "Electricians", "Landscapers", 
    "Pest Control", "Cleaning Services", "General Contractors", "Painters", "Movers"
]

CITIES = [
    "Lakeland", "Tampa", "Orlando", "Winter Haven", "Plant City"
]

def clean_slug(text):
    import re
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'[\s-]+', '-', text).strip('-')
    return text

def generate_ai_description(industry, city):
    prompt = f"""Write a compelling 150-word SEO description for AI Service Co, an AI Automation Agency providing AI Voice Receptionists for {industry} in {city}, FL. 
    
    Tone: Professional, authoritative, and focused on missed calls = missed revenue.
    Keywords to naturally include: AI receptionist for {industry}, 24/7 answering service in {city} FL, local {industry} answering service, stop missing calls.
    
    Return ONLY the raw text copy, no markdown formatting, no conversational filler.
    """
    try:
        time.sleep(1)
        response = model.generate_content(prompt)
        return response.text.strip().replace('"', '&quot;')
    except Exception as e:
        print(f"⚠️ Gemini API failed for {industry} in {city}: {e}")
        return f"AI Service Co provides advanced 24/7 AI Receptionists for {industry} in the {city} area. Stop missing calls and start booking more revenue automatically."

def build_nextjs_page_content(industry, city, copy, route_slug):
    schema = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": f"AI Receptionist for {industry} in {city}, FL",
        "provider": {
            "@type": "LocalBusiness",
            "name": "AI Service Co",
            "url": "https://aiserviceco.com"
        },
        "areaServed": {
            "@type": "City",
            "name": city,
            "addressRegion": "FL"
        }
    }
    
    page_content = f"""import React from 'react';
import {{ Metadata }} from 'next';
import Link from 'next/link';
import Script from 'next/script';

export const metadata: Metadata = {{
    title: "AI Receptionist for {industry} in {city}, FL | AI Service Co",
    description: "{copy[:150]}...",
}};

export default function AgencySeoPage() {{
    const schemaData = {schema};

    return (
        <div className="min-h-screen bg-zinc-50 font-sans text-zinc-900">
            <Script
                id="schema-{route_slug}"
                type="application/ld+json"
                dangerouslySetInnerHTML={{{{ __html: JSON.stringify(schemaData) }}}}
            />
            
            <nav className="py-4 px-8 text-sm text-zinc-500 border-b border-zinc-200 bg-white">
                <Link href="/" className="hover:text-blue-600">AI Service Co</Link>
                <span className="mx-2">›</span>
                <span className="capitalize hover:text-blue-600">Solutions</span>
                <span className="mx-2">›</span>
                <span className="text-zinc-800 font-bold">{industry} in {city}</span>
            </nav>

            <main className="max-w-4xl mx-auto px-8 py-16">
                <div className="p-8 bg-white border border-zinc-200 rounded-2xl shadow-sm mb-8">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <div className="inline-block px-3 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded-full mb-4">Industry Solution</div>
                            <h1 className="text-5xl font-black mb-2 text-zinc-900 tracking-tight">AI Receptionist for {industry} <br/>in <span className="text-blue-600">{city}, FL</span></h1>
                        </div>
                    </div>
                    
                    <div className="prose prose-zinc max-w-none mb-8">
                        <p className="text-lg leading-relaxed text-zinc-700 font-medium">
                            {copy}
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

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
            </main>
        </div>
    );
}}
"""
    return page_content

def batch_commit_to_github(files_dict, commit_message):
    try:
        gh = Github(GITHUB_TOKEN)
        repo = gh.get_repo(GITHUB_REPO)
        
        master_ref = repo.get_git_ref('heads/main')
        master_sha = master_ref.object.sha
        base_tree = repo.get_git_tree(master_sha)
        
        element_list = list()
        for file_path, content in files_dict.items():
            element = InputGitTreeElement(file_path, '100644', 'blob', content)
            element_list.append(element)
            
        tree = repo.create_git_tree(element_list, base_tree)
        parent = repo.get_git_commit(master_sha)
        commit = repo.create_git_commit(commit_message, tree, [parent])
        master_ref.edit(commit.sha)
        print(f"✅ Successfully committed {len(files_dict)} files to GitHub via API.")
    except Exception as e:
        print(f"❌ GitHub API Error: {e}")

def run_factory():
    print("=" * 60)
    print("🚀 SOVEREIGN AGENCY SEO FACTORY BOOT SEQUENCE")
    print("=" * 60)
    
    files_to_commit = {}
    count = 0
    total = len(INDUSTRIES) * len(CITIES)
    
    for industry in INDUSTRIES:
        for city in CITIES:
            count += 1
            print(f"[{count}/{total}] Generating AI Solution Page: {industry} in {city}...")
            
            copy = generate_ai_description(industry, city)
            
            route_slug = f"ai-secretary-for-{clean_slug(industry)}-in-{clean_slug(city)}"
            file_path = f"apps/portal/src/app/{route_slug}/page.tsx"
            
            page_content = build_nextjs_page_content(industry, city, copy, route_slug)
            files_to_commit[file_path] = page_content
            
    if files_to_commit and GITHUB_TOKEN:
        print(f"🚀 Pushing {len(files_to_commit)} pages to GitHub repository...")
        batch_commit_to_github(files_to_commit, f"🚀 Autonomous Agency SEO Factory: 50 Regional Solution Pages")
    elif files_to_commit:
        print("⚠️ GITHUB_TOKEN not found. Saving files locally instead (Legacy Mode).")
        for path, content in files_to_commit.items():
            dir_path = os.path.dirname(os.path.abspath(path))
            os.makedirs(dir_path, exist_ok=True)
            with open(os.path.abspath(path), "w", encoding="utf-8") as f:
                f.write(content)
                
    print(f"🎉 FACTORY RUN COMPLETE: {total} pages built.")

if __name__ == "__main__":
    run_factory()
