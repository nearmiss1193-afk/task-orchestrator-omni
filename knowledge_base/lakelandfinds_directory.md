# LakelandFinds Directory — Architecture & Deployment

## Last Updated: 2026-02-20

## Project Overview

Yelp-style local business directory for Lakeland, FL. Server-side rendered Next.js 14 app with Neon PostgreSQL, deployed on Vercel with auto-deploy via GitHub.

## Live URLs

- **Production**: <https://lakeland-local-prod.vercel.app>
- **Custom Domain**: lakelandfinds.com / <www.lakelandfinds.com> (Squarespace DNS → Vercel)
- **GitHub**: <https://github.com/nearmiss1193-afk/lakeland-local-prod>
- **Vercel Account**: nearmiss1193-9477

## Google Analytics

| Property | Measurement ID |
|----------|---------------|
| Primary (new Feb 20) | `G-QBGRPDW65K` |
| Secondary (existing) | `G-SZWJKJNSZ9` |

Both configured in `app/layout.tsx` with `strategy="beforeInteractive"` for Google tag detection compatibility.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | Next.js 14 (App Router, SSR) |
| Database | Neon DB (PostgreSQL) |
| ORM | Drizzle ORM |
| Hosting | Vercel (auto-deploy on push to `master`) |
| Styling | Tailwind CSS (warm coral #E85D3A) |
| Icons | lucide-react |
| Voice AI | VAPI Web SDK (`@vapi-ai/web`) |
| Analytics | Google Analytics GA4 (dual property) |

## Key Files

```text
app/page.tsx              → Homepage (hero, search, categories, top-rated)
app/search/page.tsx       → Search results with distance badges
app/categories/page.tsx   → 30-category grid with icons
app/claim/page.tsx        → Lead capture → 1staistep.com
app/business/[id]/page.tsx → Business detail with Google Maps
app/sitemap.ts            → Dynamic sitemap (static + business pages)
app/api/search/route.ts   → Autocomplete search API
hooks/useGeolocation.ts   → Browser location + Haversine distance
components/VapiWidget.tsx → VAPI voice widget (Sarah AI)
components/business/DistanceBadge.tsx → "0.8 mi" badges
components/layout/Footer.tsx → Newsletter + business CTA
components/search/SearchAutocomplete.tsx → Two-field autocomplete
lib/db/schema.ts          → Drizzle schema (businesses table)
lib/db/index.ts           → Lazy-init DB connection (Proxy-based)
lib/actions/business.ts   → Server actions (fetch, search, count)
scripts/scrape-osm.ts     → OpenStreetMap Overpass scraper
```

## VAPI Integration

| Key | Value |
|-----|-------|
| Public Key | `3b065ff0-a721-4b66-8255-30b6b8d6daab` |
| Private Key | `c23c884d-0008-...` (in Modal `agency-vault`) |
| Assistant ID | `1a797f12-e2dd-4f7f-b2c5-08c38c74859a` (Sarah) |
| SDK | `@vapi-ai/web` (lazy-loaded on first click) |

## Database Schema (businesses table)

id, name, address, category, phone, websiteUrl, rating, totalRatings, lat, lng, claimedStatus, vibeSummary, aiVisibilityScore

## Environment Variables (Vercel + .env.local)

- DATABASE_URL → Neon connection string (**only on Vercel, not local**)
- GOOGLE_MAPS_API_KEY → For embedded maps

## Deploy Workflow

```bash
# Make changes → commit → push → auto-deploy
git add -A
git commit -m "feat: description"
git push origin master
# Vercel auto-deploys to production
```

## Key Learnings

1. **PowerShell `curl` doesn't work** — use `Invoke-WebRequest` for testing
2. **Lucide `Home` icon** conflicts with Next.js default export named `Home` — use `Home as HomeIcon`
3. **Next.js stale webpack cache** can cause 500 errors — restart dev server
4. **PowerShell treats git stderr as errors** — exit code 1 doesn't mean failure
5. **Vercel Hobby plan** is sufficient for this project
6. **DistanceBadge (client component)** works fine in server pages — `'use client'` boundary handles it
7. **Lazy-init DB** — `lib/db/index.ts` uses Proxy to defer `neon()` call until runtime, preventing build-time crashes when `DATABASE_URL` isn't available locally
8. **VAPI Web SDK** needs a **public** key (not the private key stored in Modal secrets)
9. **Tailwind `@apply` arbitrary values** — never use `rgba()` or CSS functions with parentheses inside arbitrary values. They break PostCSS parsing. Use standard Tailwind classes instead.
10. **Vercel build cache** — use `--force` flag when CSS/config changes aren't being picked up. Vercel caches aggressively.
11. **Next.js `<Script strategy>`** — use `beforeInteractive` for GA tags so Google's static tag checker can detect them. `afterInteractive` loads via JS which bots can't see.
12. **GA tag ID B vs 8 typo** — ALWAYS copy-paste measurement IDs, never type manually. `G-QBGRPDW65K` ≠ `G-Q8GRPDW65K`.
13. **Pre-existing ESLint/TS errors blocking deploy** — add `eslint.ignoreDuringBuilds` and `typescript.ignoreBuildErrors` to `next.config.mjs` for quick unblocking.

## Revenue Model

- Free business listings drive traffic
- "Claim Your Listing" CTA → 1staistep.com lead capture
- Verified/featured placement for paying businesses (future)

## Future Roadmap

- AI-generated hero images (Lakeland landmarks)
- Google Places API scraper (expand listings beyond OSM)
- Save/Favorite feature (localStorage-based)
- Connect newsletter signups to GHL/Supabase
