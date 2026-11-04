const PREFIX = 'smartgov-studio-'
const CACHE = PREFIX + '__BUILD_ID__'
const RECORDINGS = 'smartgov-recordings-v1'
const BASE = '/studio/'
const data = [BASE + 'catalog.json', BASE + 'facilities.json']
const shell = [BASE, BASE + 'mark.svg', BASE + 'manifest.webmanifest', /*__ASSETS__*/]
const files = new Set([...shell, ...data])
const recordingPath = '/static/audio/studio/bilingual/'

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
  if (request.method !== 'GET' || url.origin !== self.location.origin) return
  if (url.pathname.startsWith(recordingPath) && /\.(en|te)\.mp3$/.test(url.pathname)) {
    event.respondWith(recordingResponse(request))
    return
  }
  if (!files.has(url.pathname)) return
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

async function recordingResponse(request) {
  const cache = await caches.open(RECORDINGS)
  let response = await cache.match(request.url)
  if (!response) {
    // Fetch the complete file once so later audio seeks can work offline.
    try { response = await fetch(request.url) }
    catch { return new Response(null, { status: 503 }) }
    if (!response.ok || response.status !== 200 || !response.headers.get('Content-Type')?.startsWith('audio/')) return response
    await cache.put(request.url, response.clone()).catch(() => {})
  }

  const range = request.headers.get('Range')?.match(/^bytes=(\d*)-(\d*)$/)
  if (!range || (!range[1] && !range[2])) return response
  const content = await response.arrayBuffer()
  const length = content.byteLength
  const start = range[1] ? Number(range[1]) : Math.max(0, length - Number(range[2]))
  const end = range[1] && range[2] ? Math.min(Number(range[2]), length - 1) : length - 1
  if (start > end || start >= length) {
    return new Response(null, { status: 416, headers: { 'Content-Range': `bytes */${length}` } })
  }
  return new Response(content.slice(start, end + 1), {
    status: 206,
    headers: {
      'Content-Type': response.headers.get('Content-Type'),
      'Content-Length': String(end - start + 1),
      'Accept-Ranges': 'bytes',
      'Content-Range': `bytes ${start}-${end}/${length}`,
    },
  })
}
