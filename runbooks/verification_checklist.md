# Verification Checklist - PowerShell + SQL

## PowerShell Verification Commands

### 1. Website Truth

```powershell
# Verify production website
python verify_production.py

# Check brand.json
curl.exe -s "https://www.aiserviceco.com/brand.json" | ConvertFrom-Json

# Check cache headers
curl.exe -sI "https://www.aiserviceco.com/" 2>&1 | Select-String "x-vercel|age"
```

### 2. Modal API Health

```powershell
# Health check
curl.exe -s "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/health"

# Truth endpoint
curl.exe -s "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/truth" | ConvertFrom-Json

# SMS health
curl.exe -s "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/health"
```

### 3. Git Status

```powershell
git status
git log --oneline -5
```

---

## SQL Verification Queries (Supabase)

### Recent Events

```sql
SELECT event_type, created_at, payload->>'contact_id' as contact
FROM event_log_v2
ORDER BY created_at DESC
LIMIT 20;
```

### SMS Pipeline Status

```sql
SELECT 
  event_type,
  COUNT(*) as count,
  MAX(created_at) as last_seen
FROM event_log_v2
WHERE event_type LIKE 'sms.%'
  AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY event_type
ORDER BY last_seen DESC;
```

### Deadman Check (unreplied SMS)

```sql
SELECT e1.created_at as inbound_time, e1.payload->>'from' as from_number
FROM event_log_v2 e1
WHERE e1.event_type = 'sms.inbound'
  AND e1.created_at > NOW() - INTERVAL '1 hour'
  AND NOT EXISTS (
    SELECT 1 FROM event_log_v2 e2
    WHERE e2.event_type = 'sms.reply.sent'
    AND e2.payload->>'to' = e1.payload->>'from'
    AND e2.created_at > e1.created_at
    AND e2.created_at < e1.created_at + INTERVAL '60 seconds'
  );
```

### Campaign Activity

```sql
SELECT event_type, COUNT(*) as count
FROM event_log_v2
WHERE created_at > NOW() - INTERVAL '24 hours'
  AND event_type IN ('campaign.sms.sent', 'campaign.email.sent', 'campaign.call.started')
GROUP BY event_type;
```

---

## Quick Status Check

```powershell
# All-in-one status check
Write-Host "=== VERIFICATION ===" -ForegroundColor Cyan

Write-Host "`n1. Production Website:" -ForegroundColor Yellow
python verify_production.py

Write-Host "`n2. Modal Health:" -ForegroundColor Yellow
curl.exe -s "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/health"

Write-Host "`n3. brand.json:" -ForegroundColor Yellow
(curl.exe -s "https://www.aiserviceco.com/brand.json" | ConvertFrom-Json).canonical | Format-Table
```
