// AI Service Co — Service Worker v1
const CACHE_NAME = 'aiserviceco-v1';
const ASSETS = [
    '/landing/dashboard.html',
    '/landing/client-dashboard.html',
    '/landing/manifest.json',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap'
];

// Install — cache core assets
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS)).then(() => self.skipWaiting())
    );
});

// Activate — clean old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => Promise.all(
            keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
        )).then(() => self.clients.claim())
    );
});

// Fetch — network-first with cache fallback
self.addEventListener('fetch', event => {
    // Skip non-GET and API calls
    if (event.request.method !== 'GET') return;
    if (event.request.url.includes('modal.run') || event.request.url.includes('supabase.co')) return;

    event.respondWith(
        fetch(event.request).then(response => {
            // Cache successful responses
            if (response.ok) {
                const clone = response.clone();
                caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
            }
            return response;
        }).catch(() => {
            // Offline fallback
            return caches.match(event.request);
        })
    );
});

// Push notifications
self.addEventListener('push', event => {
    const data = event.data?.json() || { title: '📞 New Call', body: 'Check your dashboard' };
    event.waitUntil(
        self.registration.showNotification(data.title, {
            body: data.body,
            icon: '⚡',
            badge: '📞',
            vibrate: [200, 100, 200]
        })
    );
});

// Notification click — open dashboard
self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(
        clients.openWindow('/landing/dashboard.html')
    );
});
