// Service Worker for Gitako Farm Management PWA

const CACHE_NAME = 'gitako-farm-v1.0.0';
const STATIC_CACHE = 'gitako-static-v1.0.0';
const DYNAMIC_CACHE = 'gitako-dynamic-v1.0.0';

// Files to cache immediately
const STATIC_FILES = [
    '/',
    '/dashboard/',
    '/static/css/mobile.css',
    '/static/js/pwa.js',
    '/static/css/dashboard.css',
    '/static/css/financials.css',
    'https://fonts.googleapis.com/css?family=Roboto:300,400,500',
    'https://fonts.googleapis.com/css?family=Material+Icons&display=block',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdn.jsdelivr.net/npm/chart.js',
    '/manifest.json'
];

// API endpoints to cache
const API_CACHE_PATTERNS = [
    /\/api\/crops\//,
    /\/api\/activities\//,
    /\/api\/inventory\//,
    /\/farms\/crop_dashboard\//,
    /\/activities\/activity_list\//,
    /\/inventory\/inventory_dashboard\//
];

// Install event - cache static files
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('Caching static files...');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => {
                console.log('Static files cached successfully');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('Failed to cache static files:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker activating...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== STATIC_CACHE && 
                            cacheName !== DYNAMIC_CACHE && 
                            cacheName !== CACHE_NAME) {
                            console.log('Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('Service Worker activated');
                return self.clients.claim();
            })
    );
});

// Fetch event - handle network requests
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests for caching
    if (request.method !== 'GET') {
        return;
    }
    
    // Handle different types of requests
    if (isStaticAsset(request)) {
        event.respondWith(handleStaticAsset(request));
    } else if (isAPIRequest(request)) {
        event.respondWith(handleAPIRequest(request));
    } else if (isPageRequest(request)) {
        event.respondWith(handlePageRequest(request));
    } else {
        event.respondWith(handleOtherRequest(request));
    }
});

// Check if request is for a static asset
function isStaticAsset(request) {
    const url = new URL(request.url);
    return url.pathname.includes('/static/') || 
           url.hostname !== location.hostname ||
           request.destination === 'style' ||
           request.destination === 'script' ||
           request.destination === 'font' ||
           request.destination === 'image';
}

// Check if request is for API
function isAPIRequest(request) {
    const url = new URL(request.url);
    return url.pathname.startsWith('/api/') ||
           API_CACHE_PATTERNS.some(pattern => pattern.test(url.pathname));
}

// Check if request is for a page
function isPageRequest(request) {
    return request.destination === 'document';
}

// Handle static assets - cache first strategy
async function handleStaticAsset(request) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.error('Failed to handle static asset:', error);
        return caches.match(request);
    }
}

// Handle API requests - network first, cache fallback
async function handleAPIRequest(request) {
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('Network failed for API request, checking cache...');
        const cachedResponse = await caches.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline response for API requests
        return new Response(
            JSON.stringify({
                error: 'Offline',
                message: 'This feature is not available offline',
                offline: true
            }),
            {
                status: 503,
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );
    }
}

// Handle page requests - network first, cache fallback
async function handlePageRequest(request) {
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('Network failed for page request, checking cache...');
        const cachedResponse = await caches.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page
        return caches.match('/dashboard/') || 
               caches.match('/') ||
               createOfflinePage();
    }
}

// Handle other requests
async function handleOtherRequest(request) {
    try {
        return await fetch(request);
    } catch (error) {
        const cachedResponse = await caches.match(request);
        return cachedResponse || new Response('Offline', { status: 503 });
    }
}

// Create offline page
function createOfflinePage() {
    const offlineHTML = `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Offline - Gitako Farm Management</title>
            <style>
                body {
                    font-family: 'Roboto', sans-serif;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    margin: 0;
                    background: #f5f5f5;
                    color: #333;
                }
                .offline-container {
                    text-align: center;
                    padding: 2rem;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    max-width: 400px;
                }
                .offline-icon {
                    font-size: 4rem;
                    color: #2e7d32;
                    margin-bottom: 1rem;
                }
                .offline-title {
                    font-size: 1.5rem;
                    font-weight: 600;
                    margin-bottom: 1rem;
                    color: #2e7d32;
                }
                .offline-message {
                    color: #666;
                    margin-bottom: 2rem;
                    line-height: 1.5;
                }
                .retry-button {
                    background: #2e7d32;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-size: 1rem;
                    cursor: pointer;
                    transition: background 0.3s ease;
                }
                .retry-button:hover {
                    background: #1b5e20;
                }
            </style>
        </head>
        <body>
            <div class="offline-container">
                <div class="offline-icon">🌱</div>
                <h1 class="offline-title">You're Offline</h1>
                <p class="offline-message">
                    It looks like you're not connected to the internet. 
                    Some features may not be available, but you can still view cached content.
                </p>
                <button class="retry-button" onclick="window.location.reload()">
                    Try Again
                </button>
            </div>
        </body>
        </html>
    `;
    
    return new Response(offlineHTML, {
        headers: {
            'Content-Type': 'text/html'
        }
    });
}

// Background sync for form submissions
self.addEventListener('sync', (event) => {
    console.log('Background sync triggered:', event.tag);
    
    if (event.tag === 'sync-forms') {
        event.waitUntil(syncOfflineForms());
    } else if (event.tag === 'sync-activities') {
        event.waitUntil(syncOfflineActivities());
    } else if (event.tag === 'sync-inventory') {
        event.waitUntil(syncOfflineInventory());
    }
});

// Sync offline forms
async function syncOfflineForms() {
    try {
        console.log('Syncing offline forms...');
        
        // This would typically retrieve data from IndexedDB
        // and send it to the server when connection is restored
        
        const response = await fetch('/api/sync/forms/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'sync_offline_forms'
            })
        });
        
        if (response.ok) {
            console.log('Forms synced successfully');
        }
    } catch (error) {
        console.error('Failed to sync forms:', error);
        throw error;
    }
}

// Sync offline activities
async function syncOfflineActivities() {
    try {
        console.log('Syncing offline activities...');
        
        const response = await fetch('/api/sync/activities/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'sync_offline_activities'
            })
        });
        
        if (response.ok) {
            console.log('Activities synced successfully');
        }
    } catch (error) {
        console.error('Failed to sync activities:', error);
        throw error;
    }
}

// Sync offline inventory
async function syncOfflineInventory() {
    try {
        console.log('Syncing offline inventory...');
        
        const response = await fetch('/api/sync/inventory/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'sync_offline_inventory'
            })
        });
        
        if (response.ok) {
            console.log('Inventory synced successfully');
        }
    } catch (error) {
        console.error('Failed to sync inventory:', error);
        throw error;
    }
}

// Push notification handling
self.addEventListener('push', (event) => {
    console.log('Push notification received:', event);
    
    const options = {
        body: 'You have new farm updates!',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'View Updates',
                icon: '/static/icons/checkmark.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/icons/xmark.png'
            }
        ]
    };
    
    if (event.data) {
        const pushData = event.data.json();
        options.body = pushData.body || options.body;
        options.title = pushData.title || 'Gitako Farm';
    }
    
    event.waitUntil(
        self.registration.showNotification('Gitako Farm', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
    console.log('Notification clicked:', event);
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/dashboard/')
        );
    } else if (event.action === 'close') {
        // Just close the notification
        return;
    } else {
        // Default action - open the app
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Message handling from main thread
self.addEventListener('message', (event) => {
    console.log('Message received in SW:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

console.log('Service Worker script loaded successfully');