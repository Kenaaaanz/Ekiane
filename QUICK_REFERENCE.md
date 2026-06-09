# Quick Reference Card

## System Integration Status: ✅ COMPLETE

### What's New (June 2026)
1. ✅ **Email Notifications** - Admin receives purchase emails
2. ✅ **Google Analytics** - Track user behavior & purchases
3. ✅ **Tab Management** - Cross-tab synchronization

---

## Email Notifications

### File Locations
- **Signal Handler**: `payments/signals.py`
- **Config**: `ecommerce/settings.py`
- **HTML Template**: `templates/emails/order_notification.html`
- **Text Template**: `templates/emails/order_notification.txt`
- **Test Command**: `python manage.py send_test_order_email`

### .env Configuration
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@ekianeonsare.com
ADMIN_EMAIL=admin@ekianeonsare.com
```

### Gmail Setup (2 steps)
1. Enable 2FA: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use 16-char password in `EMAIL_HOST_PASSWORD`

### Test Email
```bash
python manage.py send_test_order_email
python manage.py send_test_order_email --email test@gmail.com
python manage.py send_test_order_email --order-id 5
```

### Email Triggered When
- Payment verified successfully on Paystack
- Order status changes to 'paid'
- Signal fires automatically

### Email Contains
- Order ID & date
- Customer name, email, phone
- Delivery location & method
- Product names, quantities, prices
- Subtotal, delivery fee, total, platform fee
- **Your profit** (calculated automatically)
- Admin panel link for fulfillment

---

## Google Analytics

### File Locations
- **GA Code**: `templates/base.html` (lines 16-220)
- **Config**: `.env` and `ecommerce/settings.py`

### .env Configuration
```env
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
GOOGLE_TAG_MANAGER_ID=GTM-XXXXXX  # Optional
```

### GA4 Setup
1. Go to https://analytics.google.com
2. Click "Create" → "Property"
3. Website URL: Your domain
4. Copy Measurement ID (G-XXXXX) to `.env`
5. Deploy & wait 24-48 hours for data

### Auto-Tracked Events
- ✅ Page views
- ✅ Product views
- ✅ Add to cart
- ✅ Remove from cart
- ✅ Checkout starts
- ✅ Purchases
- ✅ Search events
- ✅ Scroll depth (25%, 50%, 75%, 100%)
- ✅ Outbound links
- ✅ Tab visibility changes

### Custom Event Example
```javascript
gtag('event', 'my_custom_event', {
    'parameter_name': value
});
```

### View Reports
1. https://analytics.google.com
2. Select "Ekiane" property
3. Check "Realtime" for live traffic
4. Check "Reports" for trends

---

## Tab Management

### File Location
- **Script**: `static/js/tab-management.js`
- **Included**: `templates/base.html` (auto-loaded)

### Features (Automatic)
- ✅ Detects tab visibility changes
- ✅ Syncs localStorage across tabs
- ✅ BroadcastChannel API (modern browsers)
- ✅ Fallback to localStorage events

### Sync Cart Example
```javascript
// After updating cart in one tab
window.tabManager.broadcastCartUpdate({
    items: cartData,
    total: cartTotal
});

// Listen in all tabs
window.addEventListener('cartUpdated', (e) => {
    const newCart = e.detail;
    updateCartUI(newCart);
});
```

### Sync Login/Logout
```javascript
// When user logs in
window.tabManager.broadcastLogin({
    userId: user.id,
    name: user.name
});

// When user logs out
window.tabManager.broadcastLogout();

// Listen for changes
window.addEventListener('userLoggedIn', (e) => {
    console.log('User:', e.detail);
});
```

### Tab Visibility
```javascript
window.addEventListener('tabHidden', () => {
    // Pause animations, auto-refresh, etc
});

window.addEventListener('tabVisible', () => {
    // Resume animations, auto-refresh, etc
});
```

---

## Database Migrations

### Orders Model
**New Field**: `phone` (CharField, optional)
**Migration**: `orders/migrations/0003_order_phone.py`

**Applied**: ✅ Yes
**Status**: Ready for production

---

## File Changes Summary

### New Files Created
```
✅ templates/emails/order_notification.html (5.2 KB)
✅ templates/emails/order_notification.txt (1.8 KB)
✅ payments/signals.py (2.1 KB)
✅ payments/apps.py (updated)
✅ static/js/tab-management.js (9.4 KB)
✅ .env (template)
✅ EMAIL_SETUP.md (comprehensive guide)
✅ GOOGLE_ANALYTICS_TAB_MANAGEMENT.md (detailed)
✅ COMPLETE_SYSTEM_INTEGRATION.md (full guide)
✅ QUICK_REFERENCE.md (this file)
```

### Modified Files
```
✅ ecommerce/settings.py (email config)
✅ orders/models.py (phone field, helper methods)
✅ templates/base.html (added static load, tab-mgmt script)
✅ README.md (added new features)
```

### Migrations Created
```
✅ orders/migrations/0003_order_phone.py
```

---

## Testing Checklist

### Email Testing
- [ ] Configure .env with email settings
- [ ] Run `python manage.py send_test_order_email`
- [ ] Check admin email inbox
- [ ] Verify HTML & text versions
- [ ] Click admin link in email
- [ ] Test with real order (checkout)

### Analytics Testing
- [ ] Add `GOOGLE_ANALYTICS_ID` to .env
- [ ] Visit website in Chrome
- [ ] Open DevTools → Network
- [ ] Search for "gtag" or "google"
- [ ] Go to GA dashboard → Realtime
- [ ] Should see yourself in realtime

### Tab Management Testing
- [ ] Open website in Tab 1
- [ ] Open website in Tab 2
- [ ] Open browser console in both
- [ ] Should see "[Tab Manager]" messages
- [ ] Add to cart in Tab 1
- [ ] Refresh Tab 2
- [ ] Cart should reflect Tab 1's changes

---

## Common Issues & Solutions

### Email Not Sending
| Issue | Solution |
|-------|----------|
| 535 Login failed | Use app password for Gmail, not regular password |
| Connection timeout | Check `EMAIL_HOST` and `EMAIL_PORT` |
| "No module named email" | Run `pip install django` |
| .env not loading | Restart Django server after editing .env |

### Analytics Not Tracking
| Issue | Solution |
|-------|----------|
| No data in GA | Wait 24-48 hours for initial data |
| 404 on gtag script | Check `GOOGLE_ANALYTICS_ID` format |
| localhost excluded | GA excludes localhost - check production |

### Tab Sync Not Working
| Issue | Solution |
|-------|----------|
| Browser compatibility | Check browser supports BroadcastChannel |
| Private/incognito mode | May not work in private browsing |
| Console errors | Check DevTools for JavaScript errors |

---

## Command Reference

### Email Commands
```bash
# Test default admin email
python manage.py send_test_order_email

# Test with custom email
python manage.py send_test_order_email --email test@gmail.com

# Test with existing order
python manage.py send_test_order_email --order-id 1

# Create test order and send email
python manage.py send_test_order_email --create
```

### Django Commands
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Run tests
python manage.py test
```

---

## Environment Variables Checklist

### Required for Email
- [ ] `EMAIL_HOST` - SMTP server
- [ ] `EMAIL_PORT` - SMTP port (usually 587)
- [ ] `EMAIL_USE_TLS` - True for TLS
- [ ] `EMAIL_HOST_USER` - Email username
- [ ] `EMAIL_HOST_PASSWORD` - App password
- [ ] `ADMIN_EMAIL` - Admin email address

### Required for Analytics
- [ ] `GOOGLE_ANALYTICS_ID` - GA4 measurement ID

### Required for Site
- [ ] `SECRET_KEY` - Django secret key
- [ ] `DEBUG` - False in production
- [ ] `SITE_URL` - Your domain URL

### Optional
- [ ] `GOOGLE_TAG_MANAGER_ID` - GTM container ID
- [ ] `DEFAULT_FROM_EMAIL` - From email address
- [ ] `PAYSTACK_*` - Already configured

---

## Support Resources

### Documentation Files
1. **[COMPLETE_SYSTEM_INTEGRATION.md](./COMPLETE_SYSTEM_INTEGRATION.md)**
   - Full setup guide for all systems
   - Detailed checklist
   - Troubleshooting

2. **[EMAIL_SETUP.md](./EMAIL_SETUP.md)**
   - Email configuration guide
   - Multiple email provider setups
   - Security best practices

3. **[GOOGLE_ANALYTICS_TAB_MANAGEMENT.md](./GOOGLE_ANALYTICS_TAB_MANAGEMENT.md)**
   - Analytics tracking guide
   - Tab management implementation
   - Custom event examples

### External Resources
- [Django Email](https://docs.djangoproject.com/en/5.2/topics/email/)
- [Google Analytics](https://support.google.com/analytics)
- [Google Tag Manager](https://tagmanager.google.com/)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [BroadcastChannel API](https://developer.mozilla.org/en-US/docs/Web/API/BroadcastChannel)

---

## Key Contacts & Notes

### Email Support
- **Provider**: Gmail (or your SMTP provider)
- **Credentials Required**: SMTP host, port, username, password
- **Security**: Use app passwords, never plain passwords

### Analytics Support
- **Provider**: Google Analytics 4
- **Dashboard**: https://analytics.google.com
- **Support**: https://support.google.com/analytics

### Emergency
- If email breaks: Check .env → Check SMTP credentials → Test with `send_test_order_email`
- If analytics breaks: Check GA ID → Check property settings → Check realtime
- If tabs break: Refresh both tabs → Check console errors → Browser compatibility

---

**Last Updated**: June 8, 2026
**Version**: 1.0
**Status**: Production Ready ✅

For detailed information, see [COMPLETE_SYSTEM_INTEGRATION.md](./COMPLETE_SYSTEM_INTEGRATION.md)
