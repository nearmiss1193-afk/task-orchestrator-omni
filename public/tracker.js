(function () {
    console.log("🛰️ Empire Analytics: Initializing...");

    // CONFIG
    const ENDPOINT = "/api/track";

    // GENERATE SESSION ID
    let sessionId = sessionStorage.getItem('empire_session_id');
    if (!sessionId) {
        sessionId = 'sess_' + Math.random().toString(36).substr(2, 9);
        sessionStorage.setItem('empire_session_id', sessionId);
    }

    // TRACK FUNCTION
    async function trackEvent(type, meta = {}) {
        const payload = {
            url: window.location.href,
            event_type: type,
            referrer: document.referrer,
            session_id: sessionId,
            meta: meta
        };

        try {
            const res = await fetch(ENDPOINT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                console.log(`🛰️ Empire Analytics: ${type} sent.`);
                document.body.style.border = "5px solid green"; // Visual Success Indicator
            } else {
                console.error(`🛰️ Empire Analytics: Server returned ${res.status}`);
                document.body.style.border = "5px solid yellow"; // Server Error Indicator
                const text = await res.text();
                console.error("Error details:", text);
            }
        } catch (e) {
            console.error("Empire Analytics Error:", e);
            document.body.style.border = "5px solid red"; // Network/Client Error Indicator
        }
    }

    // AUTO-TRACK PAGEVIEW
    trackEvent('pageview');

    // EXPOSE GLOBAL
    window.empireTrack = trackEvent;

    // TRACK ALL CLICKS
    document.addEventListener('click', (e) => {
        const target = e.target.closest('a, button');
        if (target) {
            const label = target.innerText || target.id || target.className;
            trackEvent('click', { label: label.substring(0, 50) });
        }
    });

})();
