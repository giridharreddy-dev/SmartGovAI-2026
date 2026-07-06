const CACHE_NAME = 'smartgov-health-v1';
const OFFLINE_URL = '/offline.html';

const CORE_ASSETS = [
  '/',
  '/static/manifest.webmanifest',
  '/static/icon.svg',
  '/static/enhanced-features.js',
  '/healthz'
];

// Files to cache on install
const STATIC_CACHE_FILES = [
  '/static/manifest.webmanifest',
  '/static/icon.svg',
  '/static/enhanced-features.js',
  '/offline.html'
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
    // For other requests, try network first, then cache
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
        .catch(() => caches.match(event.request))
    );
  }
});

// Handle messages from clients
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'CACHE_ALL_AUDIO') {
    // Pre-cache all audio files
    cacheAllAudio();
  }
});

async function cacheAllAudio() {
  try {
    const response = await fetch('/offline-cache');
    const data = await response.json();
    const cache = await caches.open(CACHE_NAME);
    
    // Cache the schemes data
    cache.put('/offline-cache', new Response(JSON.stringify(data), {
      headers: { 'Content-Type': 'application/json' }
    }));
    
    console.log('✅ Offline cache updated');
  } catch (error) {
    console.warn('Failed to cache audio:', error);
  }
}

