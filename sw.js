/* My Study — Service Worker (オフライン対応) */
const CACHE = 'mystudy-v11';
const ASSETS = [
  './',
  './index.html',
  './css/style.css',
  './js/app.js',
  './js/marked.min.js',
  './manifest.webmanifest',
  './content/manifest.json',
  './content/plan.md',
  './content/notes/cheatsheet.md',
  './content/notes/ai-history.md',
  './content/notes/ml-methods.md',
  './content/notes/deep-learning.md',
  './content/notes/law-ethics.md',
  './content/notes/math-stats.md',
  './content/notes/english.md',
  './data/manifest.json',
  './data/decks/ai-history.json',
  './data/decks/ml.json',
  './data/decks/dl.json',
  './data/decks/law.json',
  './data/decks/abbr.json',
  './data/decks/english.json',
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

/* network-first：データの更新を優先しつつ、オフライン時はキャッシュへ */
self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request)
      .then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(e.request, copy)).catch(() => {});
        return res;
      })
      .catch(() => caches.match(e.request).then((r) => r || caches.match('./index.html')))
  );
});
