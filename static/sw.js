// Warehouse Management - Service Worker
// Cache-busting and pass-through network policy for real-time warehouse operations

const CACHE_NAME = 'warehouse-ai-v4';

self.addEventListener('install', function(event) {
  // Activate worker immediately
  self.skipWaiting();
});

self.addEventListener('activate', function(event) {
  // Purge any older cached versions
  event.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.map(function(key) {
          return caches.delete(key);
        })
      );
    }).then(function() {
      return self.clients.claim();
    })
  );
});

self.addEventListener('fetch', function(event) {
  // Always fetch fresh network requests for all real-time pages, API calls, and posts
  event.respondWith(
    fetch(event.request).catch(function() {
      return caches.match(event.request);
    })
  );
});
