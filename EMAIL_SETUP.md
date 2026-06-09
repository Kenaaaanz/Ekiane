# Email Notification Setup Guide

## Overview
This guide explains how to set up email notifications for your Ekiane e-commerce system. When a customer completes a purchase, an automated email is sent to the admin with complete order details.

## Features
- **Admin Order Notifications**: Receive detailed emails when orders are completed
- **HTML & Plain Text**: Emails include both formatted HTML and text versions
- **Complete Order Details**: Includes customer info, products, pricing, delivery details, and profit calculations
- **Professional Design**: Beautiful email template with your brand colors

## Quick Setup

### 1. Update .env File
Add or update these email configuration variables in your `.env` file:

```env
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
DEFAULT_FROM_EMAIL=noreply@ekianeonsare.com
ADMIN_EMAIL=admin@ekianeonsare.com
SITE_URL=https://ekianeonsare.com
```

### 2. Gmail Setup (Recommended)
If using Gmail:

1. **Enable 2-Factor Authentication**:
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Google will generate a 16-character password
   - Copy this password to `EMAIL_HOST_PASSWORD` in `.env`

3. **Alternative Domains**:
   - If your domain has email, use your domain's SMTP settings instead
   - Common: `EMAIL_HOST=mail.yourdomain.com`, `EMAIL_PORT=587`

### 3. Test Email Setup
Run the test command to verify email configuration:

```bash
# Test with default admin email
python manage.py send_test_order_email

# Test with specific order
python manage.py send_test_order_email --order-id 1

# Test with different email address
python manage.py send_test_order_email --email your-test-email@gmail.com

# Create and test with a new test order
python manage.py send_test_order_email
```

## Email Configuration Options

### Environment Variables
| Variable | Purpose | Example |
|----------|---------|---------|
| `EMAIL_HOST` | SMTP server address | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP server port | `587` |
| `EMAIL_USE_TLS` | Enable TLS encryption | `True` |
| `EMAIL_HOST_USER` | Email account username | `your-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Email account password or app password | (app-specific password) |
| `DEFAULT_FROM_EMAIL` | Sender email address | `noreply@ekianeonsare.com` |
| `ADMIN_EMAIL` | Admin email (receives order notifications) | `admin@ekianeonsare.com` |
| `SITE_URL` | Your site URL (for admin links) | `https://ekianeonsare.com` |

### Supported Email Providers

#### Gmail
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
```

#### Outlook/Microsoft 365
```env
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@outlook.com
EMAIL_HOST_PASSWORD=your-password
```

#### Custom Domain Email
```env
EMAIL_HOST=mail.yourdomain.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-password
```

#### SendGrid (API-based)
If you prefer SendGrid, install sendgrid: `pip install sendgrid`

Then in settings.py:
```python
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = config('SENDGRID_API_KEY')
```

## Email Customization

### Email Templates
Email templates are located in `templates/emails/`:
- `order_notification.html` - HTML version (styled)
- `order_notification.txt` - Plain text version

### Customizing Templates
Edit the HTML template to match your brand:

1. **Colors**: Update CSS colors in `<style>` section
2. **Logo/Header**: Add your company logo
3. **Footer**: Add support contact info or social media
4. **Content**: Modify any text or structure

Example custom header:
```html
<div class="header">
    <img src="https://your-domain.com/logo.png" alt="Ekiane" style="max-width: 200px;">
    <h1>New Order from Ekiane</h1>
</div>
```

## Email Content

### What's Included in Order Notifications
1. **Order Details**:
   - Order ID and creation date
   - Order status (Pending, Paid, Fulfilled, Cancelled)
   - Total amount

2. **Customer Information**:
   - Customer name
   - Email address
   - Phone number

3. **Delivery Information**:
   - Delivery option (Delivery or Collection)
   - Exact location and house number
   - Distance and delivery fee (if applicable)

4. **Products Ordered**:
   - Product names
   - Quantities
   - Unit prices
   - Subtotals

5. **Order Summary**:
   - Subtotal
   - Delivery fee
   - Total amount
   - Platform fee (8% default)
   - **Your profit** (highlighted)

6. **Payment Status**:
   - Payment verification time
   - Payment status badge

7. **Action Link**:
   - Direct link to order in admin panel

## Troubleshooting

### Email Not Being Sent
1. **Check Environment Variables**:
   - Verify all email config vars are in `.env`
   - Restart Django server after changing `.env`

2. **Check Settings**:
   ```bash
   python manage.py shell
   >>> from django.conf import settings
   >>> print(settings.EMAIL_HOST)
   >>> print(settings.ADMIN_EMAIL)
   ```

3. **Test Manually**:
   ```bash
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> send_mail('Test', 'This is a test', 'noreply@ekianeonsare.com', ['admin@example.com'])
   >>> # Should return 1 if successful
   ```

### Gmail Authentication Failed
- **Error**: "Login credentials invalid" or "535-5.7.8 Username and password not accepted"
- **Solution**: 
  - Use the 16-character App Password (not your regular Google password)
  - Verify 2FA is enabled
  - Check EMAIL_HOST_USER matches your Gmail address exactly

### TLS/SSL Errors
- **Error**: "STARTTLS extension not supported by server"
- **Solution**: 
  - For Gmail: Use `EMAIL_PORT=587` with `EMAIL_USE_TLS=True`
  - Some providers require `EMAIL_PORT=465` with `EMAIL_USE_SSL=True`

### Production (Render) Email Setup
For Render deployments:

1. Use environment variables in Render dashboard:
   - Add all `EMAIL_*` variables
   - Use full domain name for `SITE_URL`

2. Test after deployment:
   ```bash
   # On production server
   python manage.py send_test_order_email
   ```

## Testing Workflow

### Local Development
```bash
# Set DEBUG=True in .env
# Emails appear in console (default backend)

# When ready to test actual sending:
# Set DEBUG=False in .env and configure SMTP
python manage.py send_test_order_email
```

### Staging
```bash
# Test with real SMTP
python manage.py send_test_order_email --email your-test@gmail.com

# Monitor actual orders
# Check order completion emails
```

### Production
```bash
# Verify emails are sent automatically on purchase
# Monitor admin inbox
# Check logs for any email errors
```

## Email Scheduling (Optional)

### Retry Failed Emails
If you want to retry failed emails, install celery:

```bash
pip install celery redis
```

Then modify `payments/signals.py` to use async tasks.

### Digest Emails
To send a daily digest of orders instead of individual emails:

1. Create a management command: `send_daily_digest`
2. Schedule with cron or Celery Beat

## Performance Considerations

### Async Email Sending
For high-traffic sites, send emails asynchronously to avoid blocking requests:

```python
# In settings.py
EMAIL_BACKEND = 'django_celery_email.backends.CeleryEmailBackend'
CELERY_EMAIL_TASK_CONFIG = {
    'rate_limit': '50/m'  # Rate limit emails
}
```

### Email Limits
- **Gmail**: 500 emails/day for development
- **SendGrid**: Varies by plan
- **Custom SMTP**: Check with your provider

## Security Best Practices

1. **Never commit `.env` to git**
   - Add `.env` to `.gitignore`
   - Use environment variables in production

2. **Use App Passwords**
   - Never use your main account password
   - Generate provider-specific passwords

3. **Enable TLS/SSL**
   - Always use `EMAIL_USE_TLS=True` or `EMAIL_USE_SSL=True`

4. **Monitor Email Logs**
   - Log failed sends
   - Monitor bounce rates

5. **SPF/DKIM Configuration**
   - Add SPF record: `v=spf1 include:sendgrid.net ~all`
   - Configure DKIM in DNS

## Additional Resources

- [Django Email Documentation](https://docs.djangoproject.com/en/5.2/topics/email/)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [SendGrid Setup](https://sendgrid.com/docs/for-developers/sending-email/django/)
- [Email Best Practices](https://docs.djangoproject.com/en/5.2/topics/email/#email-backends)

## Support

For issues with email setup:
1. Check `.env` configuration
2. Run test command with verbose output
3. Check Django logs for error messages
4. Verify SMTP credentials with provider
