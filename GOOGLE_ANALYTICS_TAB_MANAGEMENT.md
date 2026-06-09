# Google Analytics & Tab Management Setup

This document describes how to integrate Google Analytics and implement tab management throughout your Ekiane e-commerce system.

## Google Analytics Setup

### 1. Create Google Analytics Property
1. Go to [analytics.google.com](https://analytics.google.com)
2. Click "Start measuring"
3. Create a new account named "Ekiane"
4. Select property type: "Web"
5. Set up your web data stream for your domain

### 2. Get Your Measurement IDs
After setup, you'll receive:
- **Measurement ID** (GA4): Format `G-XXXXXXXXXX`
- **Google Tag Manager ID** (optional): Format `GTM-XXXXXX`

### 3. Configure in .env
```env
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
GOOGLE_TAG_MANAGER_ID=GTM-XXXXXX
```

### 4. Implementation
The analytics tracking is already configured in your templates. All pages will automatically track:
- Page views
- User interactions
- E-commerce events
- Custom events

## Tab Management Features

### What's Included
1. **Tab Activity Tracking** - Track which tabs users have open
2. **Tab Communication** - Send messages between tabs
3. **Session Synchronization** - Keep data in sync across tabs
4. **Storage Sync** - LocalStorage changes sync across tabs

### Implementation

#### 1. Add Tab Management Script
Add this to your `templates/base.html`:

```html
<script src="{% static 'js/tab-management.js' %}"></script>
```

#### 2. Tab Management Features

**Track Tab Activity**:
```javascript
// Detects when user switches tabs
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        console.log('Tab hidden');
    } else {
        console.log('Tab visible');
    }
});
```

**Send Messages Between Tabs**:
```javascript
// Send message from one tab to others
const channel = new BroadcastChannel('app_channel');
channel.postMessage({
    type: 'CART_UPDATED',
    data: { items: 3 }
});

// Receive messages
channel.onmessage = (event) => {
    console.log('Message from another tab:', event.data);
};
```

**Sync LocalStorage**:
```javascript
// Updates automatically sync across tabs
window.addEventListener('storage', function(e) {
    if (e.key === 'cart') {
        console.log('Cart updated in another tab:', e.newValue);
    }
});
```

## Creating Tab Management Script

### File: `static/js/tab-management.js`

```javascript
/**
 * Tab Management System
 * Handles communication and synchronization across browser tabs
 */

class TabManager {
    constructor() {
        this.tabId = this.generateTabId();
        this.channel = new BroadcastChannel('ekiane_app');
        this.init();
    }

    generateTabId() {
        return 'tab_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    init() {
        // Listen for messages from other tabs
        this.channel.addEventListener('message', (event) => {
            this.handleMessage(event.data);
        });

        // Track visibility changes
        document.addEventListener('visibilitychange', () => {
            this.onVisibilityChange();
        });

        // Listen for storage changes
        window.addEventListener('storage', (event) => {
            this.onStorageChange(event);
        });

        // Notify other tabs that this one is open
        this.broadcastTabOpen();
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
            default:
                console.log('Unknown message type:', type);
        }
    }

    broadcastTabOpen() {
        this.channel.postMessage({
            type: 'TAB_OPEN',
            tabId: this.tabId,
            timestamp: new Date().toISOString()
        });
    }

    broadcastCartUpdate(cartData) {
        this.channel.postMessage({
            type: 'CART_UPDATED',
            payload: cartData,
            tabId: this.tabId
        });
    }

    broadcastLogin(userData) {
        this.channel.postMessage({
            type: 'USER_LOGIN',
            payload: userData,
            tabId: this.tabId
        });
    }

    broadcastLogout() {
        this.channel.postMessage({
            type: 'LOGOUT',
            tabId: this.tabId
        });
    }

    handleCartUpdate(payload) {
        // Update cart UI
        const event = new CustomEvent('cartUpdated', { detail: payload });
        window.dispatchEvent(event);
    }

    handleUserLogin(payload) {
        // Update user info
        const event = new CustomEvent('userLoggedIn', { detail: payload });
        window.dispatchEvent(event);
    }

    handleLogout() {
        const event = new CustomEvent('userLoggedOut');
        window.dispatchEvent(event);
    }

    onVisibilityChange() {
        if (document.hidden) {
            console.log('[Tab Manager] Tab hidden');
            window.dispatchEvent(new CustomEvent('tabHidden'));
        } else {
            console.log('[Tab Manager] Tab visible');
            window.dispatchEvent(new CustomEvent('tabVisible'));
        }
    }

    onStorageChange(event) {
        if (event.key === 'cart') {
            console.log('[Tab Manager] Cart synced:', event.newValue);
        } else if (event.key === 'user') {
            console.log('[Tab Manager] User data synced:', event.newValue);
        }
    }

    // Utility methods
    setItem(key, value) {
        localStorage.setItem(key, JSON.stringify(value));
    }

    getItem(key) {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    }
}

// Initialize tab manager globally
window.tabManager = new TabManager();
```

## Analytics Implementation

### Google Analytics Code (in base.html)

```html
<!-- Google Analytics with GTM (optional) -->
{% if google_tag_manager_id %}
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={{ google_tag_manager_id }}"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
{% endif %}

<!-- Google Analytics -->
{% if google_analytics_id %}
<script async src="https://www.googletagmanager.com/gtag/js?id={{ google_analytics_id }}"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', '{{ google_analytics_id }}');

    // Track page views
    gtag('event', 'page_view', {
        'page_path': window.location.pathname,
        'page_title': document.title
    });

    // Track products viewed
    {% if product %}
    gtag('event', 'view_item', {
        'items': [{
            'item_id': '{{ product.id }}',
            'item_name': '{{ product.name }}',
            'price': {{ product.price }},
            'currency': '{{ currency_code }}'
        }]
    });
    {% endif %}

    // Track add to cart
    function trackAddToCart(productId, productName, price) {
        gtag('event', 'add_to_cart', {
            'items': [{
                'item_id': productId,
                'item_name': productName,
                'price': price,
                'currency': '{{ currency_code }}'
            }]
        });
    }

    // Track purchase
    function trackPurchase(orderId, total, items) {
        gtag('event', 'purchase', {
            'transaction_id': orderId,
            'value': total,
            'currency': '{{ currency_code }}',
            'items': items
        });
    }
</script>
{% endif %}
```

### Tracking Custom Events

#### Product View
```javascript
gtag('event', 'view_item', {
    'items': [{
        'item_id': productId,
        'item_name': productName,
        'price': productPrice,
        'currency': 'KES'
    }]
});
```

#### Add to Cart
```javascript
gtag('event', 'add_to_cart', {
    'items': [{
        'item_id': productId,
        'item_name': productName,
        'quantity': quantity,
        'price': price,
        'currency': 'KES'
    }]
});
```

#### Purchase
```javascript
gtag('event', 'purchase', {
    'transaction_id': orderId,
    'value': totalAmount,
    'currency': 'KES',
    'items': [
        {
            'item_id': '1',
            'item_name': 'Product Name',
            'price': 1300,
            'quantity': 1
        }
    ]
});
```

## Viewing Analytics Data

### Main Dashboard
1. Log into [analytics.google.com](https://analytics.google.com)
2. Select your property
3. View real-time data:
   - Active users
   - Page views
   - Traffic source
   - User behavior

### Key Reports
- **Realtime**: See current users
- **Acquisition**: Where users come from
- **Behavior**: Which pages they visit
- **Conversions**: Purchase tracking
- **E-commerce**: Product performance

## Best Practices

### 1. Use Meaningful Event Names
```javascript
// Good
gtag('event', 'purchase_complete', {...});

// Avoid
gtag('event', 'event1', {...});
```

### 2. Include User Properties
```javascript
gtag('set', {
    'user_id': userId,
    'user_class': 'premium'  // or 'standard'
});
```

### 3. Track Funnel Steps
```javascript
// Track checkout steps
gtag('event', 'begin_checkout', {...});
gtag('event', 'add_shipping_info', {...});
gtag('event', 'add_payment_info', {...});
gtag('event', 'purchase', {...});
```

### 4. Privacy Considerations
- Respect user privacy
- Implement consent management
- Check GDPR/local regulations
- Use anonymized data when possible

## Troubleshooting

### Analytics Not Tracking
1. **Check Measurement ID**: Verify `GOOGLE_ANALYTICS_ID` is correct
2. **Check Filters**: Exclude `localhost` from filters in Analytics settings
3. **Wait for Data**: GA takes 24-48 hours for first data to appear
4. **Verify Script**: Check page source for GA script tag

### GTM Not Loading
1. **Check Container ID**: Verify `GOOGLE_TAG_MANAGER_ID` is correct
2. **Container Status**: Ensure container is published
3. **Check Console**: Look for JavaScript errors

### Tab Sync Not Working
1. **Check Browser Support**: BroadcastChannel API requires modern browsers
2. **Check Privacy Mode**: Might not work in private/incognito
3. **Check Console**: Look for errors in browser console

## Advanced Features

### Custom Dimensions
```javascript
// Set custom dimension
gtag('set', {
    'dimension1': 'premium_user',
    'dimension2': 'has_loyalty_card'
});
```

### Event Parameters
```javascript
gtag('event', 'search', {
    'search_term': 'shea butter',
    'number_of_results': 12
});
```

### E-commerce Tracking
```javascript
gtag('event', 'view_item_list', {
    'items': [
        {
            'item_id': '1',
            'item_name': 'Organic Shea Butter',
            'item_category': 'Hair Care'
        }
    ]
});
```

## Integration with Django

### Template Tags for Analytics
You can create custom template tags to simplify analytics:

```python
# In a template tag file
from django import template

register = template.Library()

@register.filter
def to_json(value):
    import json
    return json.dumps(value)
```

Then use in templates:
```html
<script>
    trackPurchase({{ order.id }}, {{ order.total }}, {{ items|to_json }});
</script>
```

## Monitoring & Alerts

### Set up alerts in Google Analytics:
1. Go to Admin → Alerts
2. Create conditions:
   - High bounce rate (> 80%)
   - No traffic for 24 hours
   - Unusual traffic spike

## Resources

- [Google Analytics Documentation](https://support.google.com/analytics)
- [Google Tag Manager Setup](https://tagmanager.google.com)
- [E-commerce Tracking Guide](https://support.google.com/analytics/answer/9268037)
- [BroadcastChannel API](https://developer.mozilla.org/en-US/docs/Web/API/BroadcastChannel)

## Support

For setup help:
1. Verify IDs in `.env`
2. Check Analytics dashboard for data
3. Use browser dev tools to verify GA script loads
4. Check Analytics documentation for specific events
