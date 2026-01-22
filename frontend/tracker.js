/**
 * Empire Visitor Tracker
 * Add this database-less tracking script to any page.
 */
(function () {
    const API_ENDPOINT = "https://nearmiss1193--v2-visitor-analytics-track-visitor.modal.run"; // Update if changed

    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    function getVisitorId() {
        let vid = localStorage.getItem('empire_visitor_id');
        if (!vid) {
            vid = generateUUID();
            localStorage.setItem('empire_visitor_id', vid);
        }
        return vid;
    }

    function track() {
        const payload = {
            url: window.location.href,
            referrer: document.referrer,
            user_agent: navigator.userAgent,
            visitor_id: getVisitorId(),
            metadata: {
                screen_width: window.screen.width,
                screen_height: window.screen.height,
                language: navigator.language
            }
        };

        // Send beacon (non-blocking) or fetch
        if (navigator.sendBeacon) {
            const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
            navigator.sendBeacon(API_ENDPOINT, blob);
        } else {
            fetch(API_ENDPOINT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            }).catch(console.error);
        }
    }

    // Track on load
    if (document.readyState === 'complete') {
        track();
    } else {
        window.addEventListener('load', track);
    }
})();
