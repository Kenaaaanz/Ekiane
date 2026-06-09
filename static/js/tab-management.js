/**
 * Tab Management System
 * Handles communication and synchronization across browser tabs
 * Features: Cart sync, User session sync, Tab visibility tracking
 */

class TabManager {
    constructor() {
        this.tabId = this.generateTabId();
        this.canUseBroadcastChannel = 'BroadcastChannel' in window;
        
        if (this.canUseBroadcastChannel) {
            this.channel = new BroadcastChannel('ekiane_app');
        }
        
        this.init();
    }

    generateTabId() {
        return 'tab_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    init() {
        if (this.canUseBroadcastChannel) {
            // Listen for messages from other tabs
            this.channel.addEventListener('message', (event) => {
                this.handleMessage(event.data);
            });
        }

        // Track visibility changes
        document.addEventListener('visibilitychange', () => {
            this.onVisibilityChange();
        });

        // Listen for storage changes (fallback if BroadcastChannel not available)
        window.addEventListener('storage', (event) => {
            this.onStorageChange(event);
        });

        // Notify other tabs that this one is open
        this.broadcastTabOpen();
        
        console.log('[Tab Manager] Initialized - Tab ID:', this.tabId);
    }

    handleMessage(data) {
        const { type, payload } = data;
        
        switch(type) {
            case 'CART_UPDATED':
                this.handleCartUpdate(payload);
                break;
            case 'USER_LOGIN':
                this.handleUserLogin(payload);
                break;
            case 'LOGOUT':
                this.handleLogout();
                break;
            case 'TAB_OPEN':
                console.log('[Tab Manager] Another tab opened:', data.tabId);
                break;
            default:
                console.log('[Tab Manager] Unknown message type:', type);
        }
    }

    broadcastTabOpen() {
        this.broadcast({
            type: 'TAB_OPEN',
            tabId: this.tabId,
            timestamp: new Date().toISOString()
        });
    }

    broadcastCartUpdate(cartData) {
        this.broadcast({
            type: 'CART_UPDATED',
            payload: cartData,
            tabId: this.tabId
        });
    }

    broadcastLogin(userData) {
        this.broadcast({
            type: 'USER_LOGIN',
            payload: userData,
            tabId: this.tabId
        });
    }

    broadcastLogout() {
        this.broadcast({
            type: 'LOGOUT',
            tabId: this.tabId
        });
    }

    broadcast(message) {
        if (this.canUseBroadcastChannel) {
            this.channel.postMessage(message);
        }
        // Messages also sync via localStorage
    }

    handleCartUpdate(payload) {
        console.log('[Tab Manager] Cart updated:', payload);
        // Dispatch custom event for cart update
        const event = new CustomEvent('cartUpdated', { detail: payload });
        window.dispatchEvent(event);
    }

    handleUserLogin(payload) {
        console.log('[Tab Manager] User logged in:', payload);
        // Dispatch custom event for user login
        const event = new CustomEvent('userLoggedIn', { detail: payload });
        window.dispatchEvent(event);
    }

    handleLogout() {
        console.log('[Tab Manager] User logged out');
        // Dispatch custom event for logout
        const event = new CustomEvent('userLoggedOut');
        window.dispatchEvent(event);
    }

    onVisibilityChange() {
        if (document.hidden) {
            console.log('[Tab Manager] Tab is now hidden');
            window.dispatchEvent(new CustomEvent('tabHidden'));
        } else {
            console.log('[Tab Manager] Tab is now visible');
            window.dispatchEvent(new CustomEvent('tabVisible'));
        }
    }

    onStorageChange(event) {
        if (event.key === 'cart') {
            console.log('[Tab Manager] Cart synced from localStorage:', event.newValue);
            this.handleCartUpdate(JSON.parse(event.newValue || '{}'));
        } else if (event.key === 'user') {
            console.log('[Tab Manager] User data synced from localStorage:', event.newValue);
            this.handleUserLogin(JSON.parse(event.newValue || '{}'));
        }
    }

    // Utility methods for localStorage
    setItem(key, value) {
        localStorage.setItem(key, JSON.stringify(value));
        this.broadcastStorageUpdate(key, value);
    }

    getItem(key) {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    }

    removeItem(key) {
        localStorage.removeItem(key);
    }

    broadcastStorageUpdate(key, value) {
        // This is handled automatically by localStorage 'storage' event
        // But we can add custom broadcast here if needed
        if (this.canUseBroadcastChannel) {
            this.broadcast({
                type: 'STORAGE_UPDATED',
                key: key,
                value: value
            });
        }
    }

    // Get active tab count
    getActiveTabCount() {
        return sessionStorage.getItem('activeTabCount') || 1;
    }

    // Check if this is the only tab
    isOnlyTab() {
        return parseInt(this.getActiveTabCount()) === 1;
    }
}

// Initialize tab manager globally
window.tabManager = new TabManager();

// Example usage - Listen for cart updates across tabs
window.addEventListener('cartUpdated', function(e) {
    console.log('Cart was updated in another tab:', e.detail);
    // Update your cart UI here
});

// Example usage - Listen for user login
window.addEventListener('userLoggedIn', function(e) {
    console.log('User logged in from another tab:', e.detail);
    // Update your UI here
    location.reload(); // Or update UI without reload
});

// Example usage - Listen for visibility changes
window.addEventListener('tabHidden', function() {
    // Pause auto-refresh, analytics, etc
});

window.addEventListener('tabVisible', function() {
    // Resume auto-refresh, analytics, etc
});
