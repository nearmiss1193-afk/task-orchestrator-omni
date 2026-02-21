-- AEO Prospect Lead List — Businesses with Missing/Weak Online Presence
-- Run this against the LakelandFinds Neon DB to find ideal AEO clients
-- These businesses NEED help with AI visibility and would pay for it
-- Query 1: Businesses with NO website (highest priority — they need everything)
SELECT name,
    category,
    phone,
    address,
    rating,
    total_ratings,
    'NO WEBSITE' as opportunity
FROM businesses
WHERE (
        website_url IS NULL
        OR website_url = ''
        OR website_url = 'null'
    )
    AND phone IS NOT NULL
    AND phone != ''
ORDER BY total_ratings DESC
LIMIT 50;
-- Query 2: Businesses with low ratings (under 3.5 stars but have reviews)
SELECT name,
    category,
    phone,
    website_url,
    address,
    rating,
    total_ratings,
    'LOW RATING - NEEDS REPUTATION MGMT' as opportunity
FROM businesses
WHERE rating < 3.5
    AND rating > 0
    AND total_ratings > 5
    AND phone IS NOT NULL
ORDER BY total_ratings DESC
LIMIT 25;
-- Query 3: High-value categories with websites (AEO upsell targets)
-- These businesses have websites but probably aren't optimized for AI search
SELECT name,
    category,
    phone,
    website_url,
    address,
    rating,
    total_ratings,
    'HAS WEBSITE - NEEDS AEO' as opportunity
FROM businesses
WHERE category IN (
        'Plumbing',
        'HVAC',
        'Roofing',
        'Electrical',
        'Restaurant',
        'Auto Repair',
        'Dentist',
        'Landscaping'
    )
    AND website_url IS NOT NULL
    AND website_url != ''
    AND phone IS NOT NULL
    AND rating >= 4.0
ORDER BY total_ratings DESC
LIMIT 50;
-- Query 4: Summary stats for your pitch deck
SELECT category,
    COUNT(*) as total_businesses,
    COUNT(
        CASE
            WHEN website_url IS NULL
            OR website_url = '' THEN 1
        END
    ) as no_website,
    COUNT(
        CASE
            WHEN rating < 3.5
            AND rating > 0 THEN 1
        END
    ) as low_rating,
    ROUND(AVG(rating)::numeric, 1) as avg_rating
FROM businesses
WHERE category IS NOT NULL
GROUP BY category
ORDER BY total_businesses DESC
LIMIT 30;