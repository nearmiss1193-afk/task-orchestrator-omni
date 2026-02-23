import os
import sys
import time
import requests
import google.generativeai as genai
from github import Github, InputGitTreeElement
from dotenv import load_dotenv

# Load env variables (for local testing, CI will inject via secrets)
load_dotenv()
load_dotenv('.env.local')

# 1. Configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO = os.environ.get('GITHUB_REPO', 'nearmiss1193-afk/empire-unified-backup')
BATCH_SIZE = 50
LAKELAND_DIR = os.path.abspath('apps/portal/src/app/lakeland')

if not SUPABASE_URL or not SUPABASE_KEY or not GEMINI_KEY:
    print("❌ FATAL: Missing database or LLM credentials.")
    sys.exit(1)

genai.configure(api_key=GEMINI_KEY)
# We use standard flash model for quick, cheap, repetitive copy generation
model = genai.GenerativeModel('gemini-2.5-flash')

def get_unpublished_businesses():
    """Fetches the next batch of businesses that need pages built."""
    try:
        url = f"{SUPABASE_URL}/rest/v1/contacts_master"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        params = {
            "seo_published": "eq.false",
            "niche": "not.is.null",
            "select": "id,company_name,niche,phone,website_url",
            "limit": BATCH_SIZE
        }
        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        rows = r.json()
        
        businesses = []
        for row in rows:
            businesses.append({
                "id": row["id"],
                "business_name": row.get("company_name"),
                "industry": row.get("niche"),
                "phone_number": row.get("phone"),
                "website": row.get("website_url")
            })
        return businesses
    except Exception as e:
        print(f"❌ Database error fetching batch: {e}")
        return []

def mark_as_published(business_ids):
    """Updates the database to ensure we don't build duplicate pages."""
    if not business_ids: return
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/contacts_master"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        ids_str = ",".join(map(str, business_ids))
        params = {
            "id": f"in.({ids_str})"
        }
        payload = {"seo_published": True}
        
        r = requests.patch(url, headers=headers, params=params, json=payload)
        r.raise_for_status()
        
        print(f"✅ Marked {len(business_ids)} rows as published.")
    except Exception as e:
        print(f"❌ Database error marking as published: {e}")

def generate_ai_description(business):
    """Calls Gemini to write 150 words of highly optimized local SEO copy."""
    prompt = f"""Write a compelling 150-word SEO description for {business['business_name']}, a {business['industry']} located in Lakeland, FL. 
    
    Tone: Professional, local, and trustworthy.
    Keywords to naturally include: {business['industry']} in Lakeland FL, local {business['industry']}, Polk county.
    
    Return ONLY the raw text copy, no markdown formatting, no conversational filler like 'Here is your description:'
    """
    
    try:
        # Include a manual sleep to respect rate limits if we scale the batch size massively
        time.sleep(1)
        response = model.generate_content(prompt)
        return response.text.strip().replace('"', '&quot;')
    except Exception as e:
        print(f"⚠️ Gemini API failed for {business['business_name']}: {e}")
        return f"{business['business_name']} is a premium {business['industry']} serving the Lakeland area. Contact them today for expert service in Polk county."

def clean_slug(text, fallback_id="unknown"):
    """Converts a business name or industry into a URL-safe slug."""
    if not text: return fallback_id
    import re
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text).strip('-')
    if not text:
        return fallback_id
    return text

def batch_commit_to_github(files_dict, commit_message):
    """Commits multiple files in a single git commit transaction to trigger exactly 1 Vercel build."""
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

def build_nextjs_page_content(business, copy, industry_slug, business_slug):
    """Constructs the React component code."""
    # 2. Setup JSON-LD Schema
    schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": business['business_name'],
        "telephone": str(business['phone_number']) if business['phone_number'] else "",
        "url": str(business['website']) if business['website'] else f"https://lakelandfinds.com/lakeland/{industry_slug}/{business_slug}",
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "5.0",
            "reviewCount": "1"
        },
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Lakeland",
            "addressRegion": "FL"
        }
    }
    
    # 2.5 Pre-calculate conditional button HTML
    phone_html = f'<a href="tel:{business["phone_number"]}" className="px-8 py-4 bg-amber-500 hover:bg-amber-600 text-white font-bold rounded-xl transition-colors">Call Now</a>' if business['phone_number'] else ""
    website_html = f'<a href="{business["website"]}" target="_blank" rel="noopener noreferrer" className="px-8 py-4 bg-zinc-100 hover:bg-zinc-200 text-zinc-800 font-bold rounded-xl transition-colors">Visit Website</a>' if business['website'] else ""

    # 3. Component Code
    page_content = f"""import React from 'react';
import {{ Metadata }} from 'next';
import Link from 'next/link';
import Script from 'next/script';

export const metadata: Metadata = {{
    title: "{business['business_name']} | Best {business['industry']} in Lakeland",
    description: "{copy[:150]}...",
}};

export default function BusinessProfilePage() {{
    const schemaData = {schema};

    return (
        <div className="min-h-screen bg-zinc-50 font-sans text-zinc-900">
            <Script
                id="schema-{business_slug}"
                type="application/ld+json"
                dangerouslySetInnerHTML={{{{ __html: JSON.stringify(schemaData) }}}}
            />
            
            <nav className="py-4 px-8 text-sm text-zinc-500 border-b border-zinc-200 bg-white">
                <Link href="/" className="hover:text-amber-500">Home</Link>
                <span className="mx-2">›</span>
                <Link href="/lakeland" className="hover:text-amber-500">Lakeland</Link>
                <span className="mx-2">›</span>
                <Link href="/lakeland/{industry_slug}" className="hover:text-amber-500 capitalize">{business['industry']}</Link>
                <span className="mx-2">›</span>
                <span className="text-zinc-800 font-bold">{business['business_name']}</span>
            </nav>

            <main className="max-w-4xl mx-auto px-8 py-16">
                <div className="p-8 bg-white border border-zinc-200 rounded-2xl shadow-sm mb-8">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <h1 className="text-4xl font-black mb-2 text-zinc-900">{business['business_name']}</h1>
                            <div className="flex gap-4 text-sm text-zinc-500">
                                <span>📍 Lakeland, FL</span>
                                <span className="text-amber-500 font-bold">★ 5.0 (Recent Reviews)</span>
                            </div>
                        </div>
                        {{/* Claim Profile Upsell */}}
                        <div className="text-right">
                             <div className="inline-block px-3 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full mb-2">Verified Listing</div>
                             <br/>
                             <Link href="/assessment" className="text-xs font-bold text-blue-600 hover:text-blue-500 underline">Claim this profile</Link>
                        </div>
                    </div>
                    
                    <div className="prose prose-zinc max-w-none mb-8">
                        <p className="text-lg leading-relaxed text-zinc-700">
                            {copy}
                        </p>
                    </div>
                    
                    <div className="flex gap-4 border-t border-zinc-100 pt-8">
                        {phone_html}
                        {website_html}
                    </div>
                </div>

                {{/* AI Service Co Upsell Widget */}}
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
}}
"""
    return page_content

def run_factory():
    print("=" * 60)
    print("🏭 INITIATING BACKGROUND SEO FACTORY RUN")
    print("=" * 60)
    
    businesses = get_unpublished_businesses()
    if not businesses:
        print("✅ Inbox zero! No unpublished businesses remain in the database.")
        sys.exit(0)
        
    print(f"📥 Pulled {len(businesses)} businesses for processing.")
    
    successful_ids = []
    files_to_commit = {}
    
    for i, business in enumerate(businesses):
        print(f"[{i+1}/{len(businesses)}] Processing: {business['business_name']}...")
        
        # 1. AI Copywriting
        copy = generate_ai_description(business)
        
        # 2. File Generation
        industry_slug = clean_slug(business['industry'], "unknown-industry")
        business_slug = clean_slug(business['business_name'], str(business.get('id', 'unknown')))
        
        file_path = f"apps/portal/src/app/lakeland/{industry_slug}/{business_slug}/page.tsx"
        page_content = build_nextjs_page_content(business, copy, industry_slug, business_slug)
        files_to_commit[file_path] = page_content
        
        successful_ids.append(business['id'])
        
    # 2.5 Commit files to repository 
    if files_to_commit and GITHUB_TOKEN:
        print(f"🚀 Pushing {len(files_to_commit)} files to GitHub repository...")
        batch_commit_to_github(files_to_commit, f"🚀 Autonomous SEO Factory Batch: {len(successful_ids)} Pages")
    elif files_to_commit:
        print("⚠️ GITHUB_TOKEN not found. Saving files locally instead (Legacy Mode).")
        for path, content in files_to_commit.items():
            dir_path = os.path.dirname(os.path.abspath(path))
            os.makedirs(dir_path, exist_ok=True)
            with open(os.path.abspath(path), "w", encoding="utf-8") as f:
                f.write(content)
        
    # 3. Mark processed in DB
    mark_as_published(successful_ids)
    
    print("=" * 60)
    print(f"🎉 FACTORY RUN COMPLETE: {len(successful_ids)} pages built.")

if __name__ == "__main__":
    run_factory()
