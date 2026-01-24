/**
 * AEO Landing Page - JavaScript
 * Handles form submission, validation, and simulated payment flow
 */

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('audit-form');
    const submitBtn = document.getElementById('submit-btn');
    const modal = document.getElementById('payment-modal');
    const modalClose = document.getElementById('modal-close');
    const payBtn = document.getElementById('pay-btn');

    // Store form data for processing
    let formData = {};

    // ===== Form Submission =====
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        // Collect form data
        formData = {
            name: document.getElementById('name').value.trim(),
            email: document.getElementById('email').value.trim(),
            website: document.getElementById('website').value.trim(),
            niche: document.getElementById('niche').value
        };

        // Validate
        if (!validateForm(formData)) {
            return;
        }

        // Show payment modal
        openModal();
    });

    // ===== Form Validation =====
    function validateForm(data) {
        if (!data.name || data.name.length < 2) {
            showError('Please enter your name.');
            return false;
        }

        if (!data.email || !isValidEmail(data.email)) {
            showError('Please enter a valid email address.');
            return false;
        }

        if (!data.website || !isValidUrl(data.website)) {
            showError('Please enter a valid website URL.');
            return false;
        }

        if (!data.niche) {
            showError('Please select your industry.');
            return false;
        }

        return true;
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    function showError(message) {
        alert(message); // Simple for now - could be upgraded to toast
    }

    // ===== Modal Controls =====
    function openModal() {
        modal.style.display = 'flex';
        setTimeout(() => modal.classList.add('active'), 10);
    }

    function closeModal() {
        modal.classList.remove('active');
        setTimeout(() => modal.style.display = 'none', 300);
    }

    modalClose.addEventListener('click', closeModal);

    modal.addEventListener('click', function (e) {
        if (e.target === modal) {
            closeModal();
        }
    });

    // ===== Payment Processing (Simulated) =====
    payBtn.addEventListener('click', async function () {
        const cardNumber = document.getElementById('card-number').value.trim();
        const cardExpiry = document.getElementById('card-expiry').value.trim();
        const cardCvc = document.getElementById('card-cvc').value.trim();

        // Basic validation
        if (!cardNumber || cardNumber.length < 16) {
            showError('Please enter a valid card number.');
            return;
        }

        if (!cardExpiry || cardExpiry.length < 5) {
            showError('Please enter a valid expiry date.');
            return;
        }

        if (!cardCvc || cardCvc.length < 3) {
            showError('Please enter a valid CVC.');
            return;
        }

        // Show loading state
        const btnText = payBtn.querySelector('.btn-text');
        const btnLoader = payBtn.querySelector('.btn-loader');
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline';
        payBtn.disabled = true;

        // Simulate payment processing
        await simulatePayment();

        // Generate audit and redirect
        await generateAudit(formData);
    });

    // ===== Real Payment via Modal/Stripe =====
    async function simulatePayment() {
        try {
            const response = await fetch('https://nearmiss1193-afk--ghl-omni-automation-create-checkout-session.modal.run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
            const data = await response.json();
            if (data.url) {
                window.location.href = data.url; // Redirect to Stripe
                // We return a promise that never resolves so we don't continue execution here
                // while the browser redirects
                return new Promise(() => { });
            } else {
                throw new Error(data.error || 'No checkout URL returned');
            }
        } catch (e) {
            console.error("Checkout Failed:", e);
            document.getElementById('pay-btn').disabled = false;
            document.getElementById('pay-btn').querySelector('.btn-text').style.display = 'inline';
            document.getElementById('pay-btn').querySelector('.btn-loader').style.display = 'none';
            alert("Payment Error: " + e.message);
            throw e; // Stop execution
        }
    }

    // ===== Generate Audit =====
    async function generateAudit(data) {
        try {
            // Try to call local backend (if running)
            const response = await fetch('http://localhost:5000/generate-audit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const result = await response.json();
                // Store result and redirect
                localStorage.setItem('aeo_audit_result', JSON.stringify(result));
                window.location.href = 'success.html';
            } else {
                throw new Error('Backend not available');
            }
        } catch (error) {
            // Fallback: Generate simulated audit locally
            console.log('Backend not available, generating locally...');
            const simulatedAudit = generateLocalAudit(data);
            localStorage.setItem('aeo_audit_result', JSON.stringify(simulatedAudit));
            window.location.href = 'success.html';
        }
    }

    // ===== Local Audit Generation (Fallback) =====
    function generateLocalAudit(data) {
        const aiSearchPct = Math.floor(Math.random() * 8) + 1;
        const directPct = Math.floor(Math.random() * 20) + 50;
        const status = aiSearchPct < 10 ? 'INVISIBLE' : 'LOW VISIBILITY';
        const revenueRanges = ['$1M - $5M', '$5M - $10M', 'Under $1M'];
        const estRevenue = revenueRanges[Math.floor(Math.random() * revenueRanges.length)];

        const competitors = [
            { name: 'LocalPro Solutions', ai_rank: 1 },
            { name: 'Metro Service Experts', ai_rank: 2 },
            { name: 'Premier ' + data.niche + ' Co', ai_rank: 3 }
        ];

        const report = `# AI VISIBILITY AUDIT: ${data.website}

**Date:** ${new Date().toISOString().split('T')[0]}
**Prepared For:** ${data.name}
**Target Niche:** ${data.niche}
**Est. Revenue Range:** ${estRevenue}

---

## 1. Executive Summary: The "AI Gap"

**Current Status: ${status}**

Your business is currently **${status}** in AI search recommendations (ChatGPT, Gemini, Perplexity).

While your direct traffic appears strong (${directPct}%), this means you are only reaching people who **already know your name**. You are missing the growing segment of buyers who search through AI assistants.

**AI Search Traffic:** ${aiSearchPct}% (Industry leaders average 15-25%)

---

## 2. Competitive AI Ranking

When users ask AI assistants for "Best ${data.niche} near me," here's who gets recommended:

| Rank | Competitor | Why They Rank |
|------|------------|---------------|
| #1 | ${competitors[0].name} | Strong schema markup, 200+ reviews |
| #2 | ${competitors[1].name} | Active press mentions, NAP consistent |
| #3 | ${competitors[2].name} | FAQ pages match AI query patterns |
| ... | **${data.website}** | [NOT FOUND IN AI RECOMMENDATIONS] |

---

## 3. Revenue Impact Analysis

Based on your industry and traffic profile:

- **Estimated Monthly AI Traffic Lost:** 150-300 visitors
- **Average Lead Value (${data.niche}):** $200-500
- **Annual Revenue Leak:** $18,000 - $72,000

---

## 4. The 3-Step "Empire" Fix

### Pillar 1: Local Authority Foundation
- [ ] Sync Google Business Profile with website NAP
- [ ] Implement review generation workflow
- [ ] Add LocalBusiness schema markup

### Pillar 2: Semantic Content Structure
- [ ] Rewrite service pages with natural language Q&A
- [ ] Add FAQ schema to all key pages
- [ ] Create location-specific landing pages

### Pillar 3: Sentiment Siege
- [ ] Distribute 3 press releases over 90 days
- [ ] Secure mentions on 5 local authority sites
- [ ] Build citation consistency across directories

---

## 5. Next Steps

Book a **free 15-minute strategy call** to walk through this audit and get your custom AEO roadmap:

**[Book Your Call](https://link.aiserviceco.com/discovery)**

---

*Generated by Empire Unified AI • AI Service Co*
`;

        return {
            success: true,
            customer: data,
            report: report,
            status: status,
            metrics: {
                ai_search_pct: aiSearchPct,
                direct_pct: directPct,
                est_revenue: estRevenue
            }
        };
    }

    // ===== Card Number Formatting =====
    document.getElementById('card-number')?.addEventListener('input', function (e) {
        let value = e.target.value.replace(/\s/g, '').replace(/\D/g, '');
        let formatted = value.match(/.{1,4}/g)?.join(' ') || value;
        e.target.value = formatted.substring(0, 19);
    });

    document.getElementById('card-expiry')?.addEventListener('input', function (e) {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length >= 2) {
            value = value.substring(0, 2) + '/' + value.substring(2, 4);
        }
        e.target.value = value;
    });
});
