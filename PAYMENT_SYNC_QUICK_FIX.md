# Quick Fix Reference

## Problem 1: Analytics Dashboard Shows Old Data
**Status:** ✅ FIXED
**Solution:** Cache now updates every 5 minutes (was 1 hour)
**Action:** No action needed - will refresh automatically

---

## Problem 2: Transactions Show "Pending" But Paystack Says "Completed"
**Status:** ✅ FIXED (with 3 new tools)

### Immediate Actions
1. **Update `.env` with Paystack Webhook Secret:**
   ```env
   PAYSTACK_WEBHOOK_SECRET=pk_live_xxx_or_your_actual_secret
   ```

2. **Configure webhook in Paystack Dashboard:**
   - URL: `https://ekianeonsare.com/payments/webhook/`
   - Events: `charge.success`, `payment.success`

3. **Sync existing mismatched payments:**
   ```bash
   python manage.py sync_paystack_payments --days 30
   ```

### Monitor & Fix Ongoing Issues

#### Option A: Admin Dashboard (Easiest)
1. Go to Admin → Payments
2. Look for ⚠ icon in "Paystack Sync" column (status mismatch)
3. Select those payments
4. Action dropdown → "Resync selected payments with Paystack" → Go

#### Option B: Command Line
```bash
# Check & sync automatically
python manage.py sync_paystack_payments

# Sync more transactions
python manage.py sync_paystack_payments --days 14 --limit 100
```

#### Option C: Debug Logs
```bash
# View live webhook events
tail -f payments.log
```

---

## Status Indicators (Admin)

| Icon | Meaning | Action |
|------|---------|--------|
| ✓ Synced | Status matches Paystack | None needed |
| ⚠ Mismatch | Status differs (needs sync) | Resync via action |
| ℹ | Different status but OK | Monitor |
| ⊘ | API error | Check secret/connection |
| ? | Can't check | Check internet |

---

## Troubleshooting

### "Still not getting live analytics"
- Analytics cache is now 5 minutes
- Clear browser cache
- Refresh page manually
- Check if orders are marked as `paid=True`

### "Still seeing pending payments that are completed"
1. Check `.env` has correct `PAYSTACK_WEBHOOK_SECRET`
2. Verify webhook URL in Paystack Dashboard
3. Run: `python manage.py sync_paystack_payments`
4. Check Admin → Payments for ⚠ icons
5. View `payments.log` for errors

### "Webhook not working"
Check `payments.log` for:
- `[WEBHOOK DEBUG] No signature header` → Webhook not configured in Paystack
- `[WEBHOOK DEBUG] Signature mismatch` → Secret doesn't match
- `[WEBHOOK DEBUG] No webhook secret` → `.env` missing PAYSTACK_WEBHOOK_SECRET

---

## Verification Checklist
- [ ] `.env` has `PAYSTACK_WEBHOOK_SECRET`
- [ ] Paystack Dashboard has webhook URL configured
- [ ] Paystack Dashboard webhook secret matches `.env`
- [ ] Run `sync_paystack_payments` command successfully
- [ ] Admin shows ✓ Synced for recent payments
- [ ] `payments.log` exists and has recent entries
- [ ] Analytics dashboard refreshes every 5 minutes

---

## Files Changed
- `analytics/signals.py` - Faster cache (5 min)
- `payments/views.py` - Better webhook logging
- `payments/utils.py` - Debug logging for signature validation
- `payments/admin.py` - Sync status display + bulk resync action
- `payments/management/commands/sync_paystack_payments.py` - NEW tool
- `ecommerce/settings.py` - Payment logging config
- `.env.example` - Added PAYSTACK_WEBHOOK_SECRET

---

For detailed help, see: `PAYMENT_SYNC_FIX.md`
