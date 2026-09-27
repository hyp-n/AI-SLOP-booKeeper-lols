const CACHE_NAME = 'booKeeper-v1.0.0';
const OFFLINE_URL = '/offline.html';

// Install service worker and cache assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll([
        '/',
        '/index.html',
        '/src/main.tsx',
        '/src/App.jsx',
        '/src/components/Navbar.jsx',
        '/src/pages/LoginPage.jsx',
        '/src/pages/ProfilePage.jsx',
        '/src/pages/FriendsPage.jsx',
        '/src/pages/ChatPage.jsx',
        '/src/api/client.js',
        '/manifest.json'
      ]))
  );
});

// Activate and clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(cacheNames =>
        Promise.all(
          cacheNames
            .filter(cacheName => cacheName !== CACHE_NAME)
            .map(cacheName => caches.delete(cacheName))
        )
      )
  );
});

// Fetch strategy: cache first, fallback to network
async function fetchWithCache(url, request) {
  const cache = await caches.open(CACHE_NAME);
  try {
    // Try cache first
    const cachedResponse = await cache.match(url);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // If not in cache, fetch from network
    const networkResponse = await fetch(url);
    
    // Cache successful responses
    if (networkResponse.ok) {
      cache.put(url, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    // If network fails, try to return offline page
    const offlineResponse = await cache.match(OFFLINE_URL);
    return offlineResponse || new Response('Offline content not available', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

// Intercept all requests
self.addEventListener('fetch', event => {
  // Skip non-GET requests and API calls
  if (event.request.method !== 'GET' || event.request.url.includes('/api/')) {
    return;
  }
  
  event.respondWith(fetchWithCache(event.request.url, event.request));
});