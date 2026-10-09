/* Ancient Aliens GIS — offline shell.
 *
 * Strategy
 *   app shell (HTML/CSS/JS)  stale-while-revalidate
 *   catalogue JSON           stale-while-revalidate
 *   map tiles & CDN          not cached here at all — the browser's HTTP
 *                            cache already handles them, and a service
 *                            worker cache would blow past storage quotas
 *                            within a few minutes of panning.
 */
/* Derived by scripts/build_data.py from a digest of every file in
 * SHELL_FILES — do not edit by hand. Any change to the shell or the
 * catalogue changes this line, which is what makes the browser install a
 * new worker and drop the stale caches on activate. CI fails the build if
 * it is out of date. */
const VERSION = 'aagis-2a6ada67f3ef';
const SHELL = `${VERSION}-shell`;
const DATA = `${VERSION}-data`;

const SHELL_FILES = [
  './',
  './index.html',
  './manifest.webmanifest',
  './assets/css/tokens.css',
  './assets/css/base.css',
  './assets/css/app.css',
  './assets/js/main.js',
  './assets/js/config.js',
  './assets/js/util.js',
  './assets/js/ogc.js',
  './assets/js/store.js',
  './assets/js/globe.js',
  './assets/js/ui.js',
  './assets/img/favicon.svg',
  './data/app-index.json',
];

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(SHELL);
    // addAll() rejects the whole install if any single file 404s, which is a
    // bad trade for an optional offline bonus.
    await Promise.allSettled(SHELL_FILES.map((f) => cache.add(f)));
    self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keep = new Set([SHELL, DATA]);
    for (const key of await caches.keys()) {
      if (!keep.has(key)) await caches.delete(key);
    }
    await self.clients.claim();
  })());
});

function sameOrigin(url) {
  return new URL(url, self.location.href).origin === self.location.origin;
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;
  if (!sameOrigin(request.url)) return;          // tiles, fonts, Cesium CDN

  const url = new URL(request.url);
  const isData = url.pathname.includes('/data/');
  const cacheName = isData ? DATA : SHELL;

  event.respondWith((async () => {
    const cache = await caches.open(cacheName);
    const cached = await cache.match(request, { ignoreSearch: !isData });

    const network = fetch(request).then((resp) => {
      if (resp.ok) cache.put(request, resp.clone()).catch(() => {});
      return resp;
    }).catch(() => null);

    if (cached) { event.waitUntil(network); return cached; }
    const fresh = await network;
    if (fresh) return fresh;
    // Last resort for a navigation: hand back the shell.
    if (request.mode === 'navigate') {
      const shell = await caches.open(SHELL);
      return (await shell.match('./index.html'))
        ?? (await shell.match('./'))
        ?? Response.error();
    }
    return Response.error();
  })());
});
