const CACHE_NAME = 'smartgov-health-v3';
const OFFLINE_URL = '/offline.html';

// Files to cache on install — all app-shell assets
const STATIC_CACHE_FILES = [
  '/',
  '/offline.html',
  '/static/style.css',
  '/static/manifest.webmanifest',
  '/static/icon.svg',
  '/static/enhanced-features.js',
  '/static/leaflet/leaflet.js',
  '/static/leaflet/leaflet.css',
  '/api/facilities',
  '/healthz'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_CACHE_FILES))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  
  // Handle HTML pages, JSON APIs, and static assets
  if (event.request.destination === 'document' || 
      event.request.destination === 'script' ||
      event.request.destination === 'style' ||
      event.request.destination === 'audio' ||
      url.pathname.endsWith('.json')) {
    
    // Stale-While-Revalidate strategy: serve from cache, update in background
    event.respondWith(
      caches.match(event.request).then(cached => {
        const fetchPromise = fetch(event.request).then(response => {
          // Only cache successful responses
          if (response && response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, responseClone);
            });
          }
          return response;
        });

        // Return cached immediately, or fetch if not cached
        return cached || fetchPromise;
      })
      .catch(() => {
        // Offline fallback
        if (event.request.destination === 'document') {
          return caches.match(OFFLINE_URL);
        }
        // Return a default response for other asset types
        return new Response('Offline - Resource not available', {
          status: 503,
          statusText: 'Service Unavailable'
        });
      })
    );
  } else {
    // For API and other requests: Network First, then exact cache, then fallback to base cache (for /api/)
    event.respondWith(
      fetch(event.request)
        .then(response => {
          if (response && response.status === 200 && response.type === 'basic') {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
            return caches.match(event.request).then(cached => {
                if (cached) return cached;
                // Fallback to base API URL if offline and exact query isn't cached
                if (url.pathname.startsWith('/api/')) {
                    return caches.match(url.pathname);
                }
                return null;
            });
        })
    );
  }
});

// Handle messages from clients
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'CACHE_ALL_AUDIO') {
    cacheAllAudio();
  }
});

async function cacheAllAudio() {
  try {
    const response = await fetch('/offline-cache');
    const data = await response.json();
    const cache = await caches.open(CACHE_NAME);
    
    // Cache the schemes data JSON payload
    cache.put('/offline-cache', new Response(JSON.stringify(data), {
      headers: { 'Content-Type': 'application/json' }
    }));
    
    // Cache individual scheme voice/audio URLs if available
    const schemes = data.schemes_list || {};
    for (const [name, scheme] of Object.entries(schemes)) {
      if (scheme.voice_url) {
        try {
          await cache.add(scheme.voice_url);
        } catch (e) {
          // Skip audio files that fail to cache (not yet generated, etc.)
        }
      }
    }

    console.log('✅ Offline cache updated with scheme data and audio');
  } catch (error) {
    console.warn('Failed to update offline cache:', error);
  }
}
