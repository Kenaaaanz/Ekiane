# Payment Status & Analytics Sync - Complete Fix Guide

## Issues Fixed

### 1. Analytics Dashboard Not Showing Live Data
**Problem:** Dashboard cache was set to 1 hour, showing stale data.
**Fix:** Reduced cache timeout from 3600 seconds to 300 seconds (5 minutes).
**File:** `analytics/signals.py` line ~164

```python
# Now caches for 5 minutes instead of 1 hour
cache.set('analytics_dashboard_data', analytics_data, 300)
```

### 2. Payment Status Mismatch (Pending vs Completed)
**Problem:** Transactions completed on Paystack but marked as "pending" in your system.
**Root Causes:**
- Webhook may not be firing for all transactions
- Webhook signature validation could fail if secret not properly configured
- Some payments only synced via user callback, not server webhook

**Fixes Applied:**

#### A. Enhanced Webhook Logging (`payments/utils.py` & `payments/views.py`)
- Added debug logging to identify signature validation failures
- Logs show whether headers are present and if secrets match
- Logs include event type and order ID for each webhook

#### B. Created Payment Sync Command
**File:** `payments/management/commands/sync_paystack_payments.py`

Manually sync pending payments with Paystack API:
```bash
# Check last 7 days of pending payments
python manage.py sync_paystack_payments

# Check more payments
python manage.py sync_paystack_payments --limit 100 --days 14
```

This command:
- Queries Paystack API for each pending transaction
- Updates local status if Paystack shows completed
- Creates order records if missing
- Provides detailed sync report

#### C. Enhanced Admin Interface (`payments/admin.py`)
- Added "Paystack Sync" column showing status match indicator
- ✓ Synced = status matches Paystack
- ⚠ Mismatch = status differs (e.g., Paystack=Success, Local=Pending)
- Admin action "Resync selected payments with Paystack" for bulk updates
- Readonly field showing detailed Paystack info (status, amount, paid time)

#### D. Improved Webhook Validation
- Better error handling in webhook receiver
- Logs all webhook events (success/ignored/error)
- Handles missing order IDs gracefully

#### E. Added Payment Logging (`ecommerce/settings.py`)
Logging to `payments.log` captures:
- All webhook events
- Signature validation attempts
- Order status updates
- Failed verification attempts

## Configuration Checklist

### 1. Ensure Webhook Secret is Set
In `.env.example`:
```env
PAYSTACK_WEBHOOK_SECRET=your-webhook-secret-from-paystack
```

**To get your webhook secret:**
1. Log in to Paystack Dashboard
2. Go to Settings → API Keys & Webhooks
3. Copy "Webhook Secret"
4. Add to `.env` and restart app

### 2. Configure Webhook URL in Paystack Dashboard
1. Log in to Paystack Dashboard
2. Settings → API Keys & Webhooks → Webhooks
3. Add webhook URL: `https://yourdomain.com/payments/webhook/`
4. Select events: `charge.success` and `payment.success`
5. Webhook Secret should match your `.env` setting

### 3. Verify SMTP Credentials (from previous fix)
Ensure in `.env.example`:
```env
EMAIL_HOST_USER=valid-email@gmail.com
EMAIL_HOST_PASSWORD=valid-app-password-from-google
```

## Troubleshooting

### Check Webhook Status
```bash
# View payment sync logs
tail -f payments.log

# Check specific payment
python manage.py shell
>>> from payments.models import Payment
>>> p = Payment.objects.get(reference='EKIANE-xxx')
>>> print(p.status, p.verified_at)
```

### Admin Manual Resync
1. Go to Django Admin → Payments
2. Select payments with mismatched status (⚠ icon)
3. Choose "Resync selected payments with Paystack" action
4. Click "Go"

### Debug Webhook Signature Issues
Check `payments.log` for errors like:
```
[WEBHOOK DEBUG] No signature header found
[WEBHOOK DEBUG] Signature mismatch
[WEBHOOK DEBUG] No webhook secret configured
```

**If you see these:**
1. Verify `PAYSTACK_WEBHOOK_SECRET` in `.env`
2. Verify webhook URL in Paystack Dashboard matches exactly
3. Verify webhook secret in Dashboard matches `.env`

### Check Recent Webhook Failures
```bash
python manage.py shell
>>> from payments.models import Payment
>>> # Find pending payments from last 7 days
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> recent = Payment.objects.filter(
...     status='initialized',
...     created_at__gte=timezone.now() - timedelta(days=7)
... )
>>> for p in recent:
...     print(f"{p.reference}: {p.status} (verified: {p.verified_at})")
```

## Manual Sync in Bulk
When first deploying this fix, sync all pending/old payments:
```bash
# Sync last 30 days of transactions
python manage.py sync_paystack_payments --days 30 --limit 200
```

## Analytics Dashboard
- Data now refreshes every 5 minutes (was 1 hour)
- Click "Refresh" button in dashboard for immediate refresh
- All charts show live order/revenue data
- Product batch metrics update in real-time

## Files Modified
1. `analytics/signals.py` - Reduced cache timeout
2. `payments/utils.py` - Added webhook signature debug logging
3. `payments/views.py` - Enhanced webhook error handling & logging
4. `payments/admin.py` - Added sync status display & bulk resync action
5. `ecommerce/settings.py` - Added payment logging config
6. `payments/management/commands/sync_paystack_payments.py` - NEW: Manual sync command

## Next Steps
1. Update `.env` with real `PAYSTACK_WEBHOOK_SECRET` from Dashboard
2. Configure webhook URL in Paystack: `https://yourdomain.com/payments/webhook/`
3. Run: `python manage.py sync_paystack_payments --days 30` to fix existing mismatches
4. Monitor `payments.log` for future webhook issues
5. Check Admin → Payments regularly for status mismatches (⚠ icon)

## Support
If you see webhook failures:
- Check `payments.log` for detailed error messages
- Verify webhook secret matches in both `.env` and Paystack Dashboard
- Verify webhook URL is exactly: `https://yourdomain.com/payments/webhook/`
- Test webhook delivery in Paystack Dashboard "Logs" section
