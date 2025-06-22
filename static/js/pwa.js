// Progressive Web App functionality for Gitako Farm Management

// Service Worker registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful with scope: ', registration.scope);
                
                // Check for updates
                registration.addEventListener('updatefound', function() {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', function() {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            // New service worker installed, show update notification
                            showUpdateNotification();
                        }
                    });
                });
            })
            .catch(function(error) {
                console.log('ServiceWorker registration failed: ', error);
            });
    });
}

// Install prompt handling
let deferredPrompt;
const installButton = document.getElementById('install-app');

window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent Chrome 67 and earlier from automatically showing the prompt
    e.preventDefault();
    // Stash the event so it can be triggered later
    deferredPrompt = e;
    // Show install button
    if (installButton) {
        installButton.style.display = 'block';
    }
    showInstallBanner();
});

// Install button click handler
if (installButton) {
    installButton.addEventListener('click', (e) => {
        // Hide the install button
        installButton.style.display = 'none';
        // Show the install prompt
        if (deferredPrompt) {
            deferredPrompt.prompt();
            // Wait for the user to respond to the prompt
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('User accepted the install prompt');
                    gtag('event', 'pwa_install_accepted');
                } else {
                    console.log('User dismissed the install prompt');
                    gtag('event', 'pwa_install_dismissed');
                }
                deferredPrompt = null;
            });
        }
    });
}

// Show install banner
function showInstallBanner() {
    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
        return;
    }
    
    const banner = document.createElement('div');
    banner.id = 'install-banner';
    banner.className = 'install-banner';
    banner.innerHTML = `
        <div class="install-banner-content">
            <div class="install-banner-icon">
                <i class="material-icons">get_app</i>
            </div>
            <div class="install-banner-text">
                <h6>Install Gitako App</h6>
                <p>Add to your home screen for a better experience</p>
            </div>
            <div class="install-banner-actions">
                <button class="btn btn-success btn-sm" onclick="triggerInstall()">Install</button>
                <button class="btn btn-outline-secondary btn-sm" onclick="dismissInstallBanner()">Later</button>
            </div>
        </div>
    `;
    
    // Add CSS for banner
    const style = document.createElement('style');
    style.textContent = `
        .install-banner {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            border-top: 1px solid #e9ecef;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
            z-index: 1050;
            padding: 16px;
            animation: slideUp 0.3s ease;
        }
        
        .install-banner-content {
            display: flex;
            align-items: center;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .install-banner-icon {
            margin-right: 16px;
            color: var(--primary-color);
        }
        
        .install-banner-text {
            flex: 1;
            margin-right: 16px;
        }
        
        .install-banner-text h6 {
            margin: 0 0 4px 0;
            font-size: 0.9rem;
            font-weight: 600;
        }
        
        .install-banner-text p {
            margin: 0;
            font-size: 0.8rem;
            color: #6c757d;
        }
        
        .install-banner-actions {
            display: flex;
            gap: 8px;
        }
        
        @keyframes slideUp {
            from { transform: translateY(100%); }
            to { transform: translateY(0); }
        }
        
        @media (max-width: 768px) {
            .install-banner-content {
                flex-direction: column;
                text-align: center;
            }
            
            .install-banner-icon {
                margin: 0 0 12px 0;
            }
            
            .install-banner-text {
                margin: 0 0 12px 0;
            }
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(banner);
    
    // Auto-dismiss after 10 seconds
    setTimeout(() => {
        dismissInstallBanner();
    }, 10000);
}

// Trigger install
function triggerInstall() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the install prompt');
            }
            deferredPrompt = null;
            dismissInstallBanner();
        });
    }
}

// Dismiss install banner
function dismissInstallBanner() {
    const banner = document.getElementById('install-banner');
    if (banner) {
        banner.remove();
    }
}

// Show update notification
function showUpdateNotification() {
    const notification = document.createElement('div');
    notification.className = 'update-notification';
    notification.innerHTML = `
        <div class="alert alert-info alert-dismissible fade show" role="alert">
            <i class="material-icons align-middle me-2">system_update</i>
            <strong>App Update Available!</strong> Refresh to get the latest features.
            <button type="button" class="btn btn-sm btn-outline-info ms-2" onclick="refreshApp()">
                Refresh Now
            </button>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('.container-fluid') || document.body;
    container.insertBefore(notification, container.firstChild);
}

// Refresh app for updates
function refreshApp() {
    window.location.reload();
}

// Offline detection
window.addEventListener('online', function() {
    showConnectivityStatus('online');
    syncOfflineData();
});

window.addEventListener('offline', function() {
    showConnectivityStatus('offline');
});

// Show connectivity status
function showConnectivityStatus(status) {
    const existingStatus = document.getElementById('connectivity-status');
    if (existingStatus) {
        existingStatus.remove();
    }
    
    const statusBar = document.createElement('div');
    statusBar.id = 'connectivity-status';
    statusBar.className = `connectivity-status ${status}`;
    
    if (status === 'offline') {
        statusBar.innerHTML = `
            <div class="connectivity-content">
                <i class="material-icons">wifi_off</i>
                <span>You're offline. Changes will sync when connected.</span>
            </div>
        `;
        statusBar.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: #ff9800;
            color: white;
            padding: 8px 16px;
            font-size: 0.85rem;
            z-index: 1060;
            text-align: center;
        `;
    } else {
        statusBar.innerHTML = `
            <div class="connectivity-content">
                <i class="material-icons">wifi</i>
                <span>Back online! Syncing data...</span>
            </div>
        `;
        statusBar.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: #4caf50;
            color: white;
            padding: 8px 16px;
            font-size: 0.85rem;
            z-index: 1060;
            text-align: center;
        `;
        
        // Auto-hide online notification after 3 seconds
        setTimeout(() => {
            statusBar.remove();
        }, 3000);
    }
    
    document.body.appendChild(statusBar);
}

// Offline data management
class OfflineManager {
    constructor() {
        this.dbName = 'GitakoFarmDB';
        this.dbVersion = 1;
        this.db = null;
        this.init();
    }
    
    async init() {
        try {
            this.db = await this.openDB();
            console.log('Offline database initialized');
        } catch (error) {
            console.error('Failed to initialize offline database:', error);
        }
    }
    
    openDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => resolve(request.result);
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                // Create object stores for offline data
                if (!db.objectStoreNames.contains('activities')) {
                    const activitiesStore = db.createObjectStore('activities', { keyPath: 'id', autoIncrement: true });
                    activitiesStore.createIndex('timestamp', 'timestamp');
                    activitiesStore.createIndex('synced', 'synced');
                }
                
                if (!db.objectStoreNames.contains('crops')) {
                    const cropsStore = db.createObjectStore('crops', { keyPath: 'id', autoIncrement: true });
                    cropsStore.createIndex('timestamp', 'timestamp');
                }
                
                if (!db.objectStoreNames.contains('inventory')) {
                    const inventoryStore = db.createObjectStore('inventory', { keyPath: 'id', autoIncrement: true });
                    inventoryStore.createIndex('timestamp', 'timestamp');
                    inventoryStore.createIndex('synced', 'synced');
                }
                
                if (!db.objectStoreNames.contains('forms')) {
                    const formsStore = db.createObjectStore('forms', { keyPath: 'id', autoIncrement: true });
                    formsStore.createIndex('timestamp', 'timestamp');
                    formsStore.createIndex('synced', 'synced');
                }
            };
        });
    }
    
    async saveOfflineData(storeName, data) {
        if (!this.db) await this.init();
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            
            data.timestamp = Date.now();
            data.synced = false;
            
            const request = store.add(data);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }
    
    async getUnsynced(storeName) {
        if (!this.db) await this.init();
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const index = store.index('synced');
            
            const request = index.getAll(false);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }
    
    async markAsSynced(storeName, id) {
        if (!this.db) await this.init();
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            
            const getRequest = store.get(id);
            getRequest.onsuccess = () => {
                const data = getRequest.result;
                if (data) {
                    data.synced = true;
                    const updateRequest = store.put(data);
                    updateRequest.onsuccess = () => resolve();
                    updateRequest.onerror = () => reject(updateRequest.error);
                } else {
                    resolve();
                }
            };
            getRequest.onerror = () => reject(getRequest.error);
        });
    }
}

// Initialize offline manager
const offlineManager = new OfflineManager();

// Sync offline data when coming back online
async function syncOfflineData() {
    try {
        const stores = ['activities', 'inventory', 'forms'];
        
        for (const storeName of stores) {
            const unsyncedData = await offlineManager.getUnsynced(storeName);
            
            for (const item of unsyncedData) {
                try {
                    await syncSingleItem(storeName, item);
                    await offlineManager.markAsSynced(storeName, item.id);
                    console.log(`Synced ${storeName} item:`, item.id);
                } catch (error) {
                    console.error(`Failed to sync ${storeName} item:`, error);
                }
            }
        }
        
        console.log('Offline data sync completed');
    } catch (error) {
        console.error('Failed to sync offline data:', error);
    }
}

// Sync individual item
async function syncSingleItem(storeName, item) {
    const endpoints = {
        activities: '/activities/sync/',
        inventory: '/inventory/sync/',
        forms: '/api/forms/sync/'
    };
    
    const endpoint = endpoints[storeName];
    if (!endpoint) return;
    
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(item)
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
}

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Offline form handling
function handleOfflineForm(formData, formType) {
    if (navigator.onLine) {
        return submitFormOnline(formData, formType);
    } else {
        return submitFormOffline(formData, formType);
    }
}

async function submitFormOffline(formData, formType) {
    try {
        const data = {
            formType: formType,
            data: formData,
            timestamp: Date.now()
        };
        
        await offlineManager.saveOfflineData('forms', data);
        
        showNotification('Form saved offline. Will sync when connected.', 'info');
        return { success: true, offline: true };
    } catch (error) {
        console.error('Failed to save form offline:', error);
        showNotification('Failed to save form. Please try again.', 'error');
        return { success: false, error: error.message };
    }
}

async function submitFormOnline(formData, formType) {
    try {
        const response = await fetch(`/api/forms/${formType}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification('Form submitted successfully!', 'success');
            return { success: true, data: result };
        } else {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
    } catch (error) {
        console.error('Failed to submit form online:', error);
        return submitFormOffline(formData, formType);
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1070;
        min-width: 300px;
        max-width: 400px;
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Export for global use
window.OfflineManager = OfflineManager;
window.offlineManager = offlineManager;
window.handleOfflineForm = handleOfflineForm;
window.showNotification = showNotification;