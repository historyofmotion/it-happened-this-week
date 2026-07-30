/*
 * Copyright 2026 David Johnson
 * Licensed under the Apache License, Version 2.0.
 * http://www.apache.org/licenses/LICENSE-2.0
 */

// Bumped from v1: v1 precached ./icon-192.png and ./icon-512.png, which were
// blank orange squares, and ./icon.svg, which no longer exists. Anyone who
// installed the app under v1 is holding those in cache — the version bump is
// what evicts them, since the activate handler deletes every cache whose key
// isn't the current one.
const CACHE_NAME = 'ihtw-v2';

const ASSETS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './favicon.ico',
  './icons/favicon.svg',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-512-maskable.png',
  './icons/apple-touch-icon.png',
  './this-week-sample.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      // addAll is all-or-nothing: one 404 and the whole install fails, leaving
      // no offline support at all. Cache each asset independently so a missing
      // file costs only that file.
      .then((cache) => Promise.all(
        ASSETS.map((url) => cache.add(url).catch((err) => {
          console.warn('[sw] could not cache', url, err);
        }))
      ))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = event.request.url;

  // Never touch the model API — these are POSTs with an auth header and must
  // not be cached or replayed.
  if (url.includes('api.anthropic.com')) return;

  // Only GETs are cacheable; cache.put throws on anything else.
  if (event.request.method !== 'GET') return;

  // The user's data file is read through the File System Access API, not fetch,
  // so it never reaches here — but be explicit about it anyway.
  if (url.includes('this-week-db')) return;

  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) {
        // Stale-while-revalidate: serve the cached copy now, quietly refresh
        // it for next time.
        fetch(event.request).then((res) => {
          if (res && res.status === 200 && res.type === 'basic') {
            const copy = res.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
          }
        }).catch(() => {});
        return cached;
      }
      return fetch(event.request);
    })
  );
});
