const PREFIX = 'smartgov-studio-'
const CACHE = PREFIX + '__BUILD_ID__'
const BASE = '/studio/'
const data = [BASE + 'catalog.json', BASE + 'facilities.json']
const shell = [BASE, BASE + 'mark.svg', BASE + 'manifest.webmanifest', /*__ASSETS__*/]
const files = new Set([...shell, ...data])

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll([...files])))
})
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const names = await caches.keys()
    await Promise.all(names.filter(key => key.startsWith(PREFIX) && key !== CACHE).map(key => caches.delete(key)))
    await self.clients.claim()
  })())
})
self.addEventListener('fetch', event => {
  const { request } = event
  const url = new URL(request.url)
  if (request.method !== 'GET' || url.origin !== self.location.origin || !files.has(url.pathname)) return
  event.respondWith((async () => {
    const cache = await caches.open(CACHE)
    if (shell.includes(url.pathname)) return (await cache.match(url.pathname)) || fetch(request)
    try {
      const response = await fetch(request)
      if (response.ok) await cache.put(url.pathname, response.clone()).catch(() => {})
      else if (response.status >= 500 || response.status === 429) return (await cache.match(url.pathname)) || response
      return response
    } catch {
      return (await cache.match(url.pathname)) || new Response('{}', { status: 503, headers: { 'Content-Type': 'application/json' } })
    }
  })())
})
