# Railway Prospecting Engine

Railway-based autonomous prospecting and email engine for AI Service Co.

## Workers

| Worker | Schedule | Purpose |
|--------|----------|---------|
| `prospecting_worker.py` | Every 6h | Scrape Google Maps for leads |
| `enrichment_worker.py` | Every 2h | Run website audits |
| `email_engine.py` | Every 30m | Trigger GHL outreach |
| `webhook_handler.py` | Always-on | Receive GHL events |

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables (see `.env.example`)
3. Deploy to Railway: `railway up`

## Environment Variables

```
SUPABASE_URL=
SUPABASE_KEY=
GHL_API_KEY=
GHL_LOCATION_ID=
```
