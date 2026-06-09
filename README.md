# Luxury Organic Hair Products E-commerce

This is a Django-based e-commerce website for luxury organic hair products like Shea Butter, Shampoo, Conditioners, and Beard Oils.

## Features

- Admin panel for managing products, tracking sales, analytics, and profit calculations
- Optional customer signup; purchase without accounts
- Paystack payment integration with 8% platform fee via subaccount
- Luxurious design with emerald green, gold, and beige colors

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Create database migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`
4. Create a superuser: `python manage.py createsuperuser`
5. Run the development server: `python manage.py runserver`

## Configuration

### Paystack Settings
Update the Paystack keys and subaccount in `ecommerce/settings.py`:

- `PAYSTACK_PUBLIC_KEY`
- `PAYSTACK_SECRET_KEY`
- `PAYSTACK_SUBACCOUNT_CODE`
- `PLATFORM_FEE_PERCENT`

### Cloudinary Setup (Production Media Storage)
For production deployment, images are stored on Cloudinary:

1. Create a free account at [cloudinary.com](https://cloudinary.com)
2. Get your Cloud Name, API Key, and API Secret
3. Set these environment variables:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`
   Or use the combined format:
   - `CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME`

4. If you have existing images, run: `python manage.py migrate_images`

See `CLOUDINARY_SETUP.md` for detailed instructions.

## Usage

- Admin panel: `/admin/`
- Store homepage: `/`
- Products by category: `/category/<category_slug>/`
- Product detail: `/<id>/<slug>/`

## Apps

- `store`: Product catalog
- `orders`: Order management
- `payments`: Paystack integration
- `analytics`: Sales analytics and profit tracking
- `accounts`: User accounts (optional)

## Recent Additions (June 2026)

### 1. Email Notifications System
Admin receives detailed email notifications when customers complete purchases.

**Features**:
- HTML & plain text email templates
- Complete order information (products, customer details, delivery, pricing)
- Profit calculations included in email
- Direct link to order in admin panel

**Setup**: See [EMAIL_SETUP.md](./EMAIL_SETUP.md)

**Quick Start**:
```bash
# Configure email in .env
EMAIL_HOST=smtp.gmail.com
ADMIN_EMAIL=admin@ekianeonsare.com

# Test email setup
python manage.py send_test_order_email
```

### 2. Google Analytics & Tag Manager
Track user behavior, purchases, and site performance with Google Analytics 4.

**Features**:
- Automatic page view tracking
- Product view tracking
- Add to cart events
- Purchase tracking
- Custom user properties
- Scroll depth tracking
- Outbound link tracking

**Setup**: See [GOOGLE_ANALYTICS_TAB_MANAGEMENT.md](./GOOGLE_ANALYTICS_TAB_MANAGEMENT.md)

**Quick Start**:
```env
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
GOOGLE_TAG_MANAGER_ID=GTM-XXXXXX  # Optional
```

### 3. Tab Management System
Automatically synchronize cart, user session, and data across browser tabs.

**Features**:
- Cart synchronization across tabs
- User login/logout sync
- Tab visibility tracking
- LocalStorage sync
- BroadcastChannel API with fallback

**Status**: Automatically enabled in all pages

**Implementation**:
```javascript
// Sync cart across tabs
window.tabManager.broadcastCartUpdate(cartData);

// Listen for updates
window.addEventListener('cartUpdated', (e) => {
    console.log('Cart updated in another tab:', e.detail);
});
```

## Configuration Guide

### Environment Variables (.env)

#### Email Configuration
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@ekianeonsare.com
ADMIN_EMAIL=admin@ekianeonsare.com
```

#### Google Analytics
```env
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
GOOGLE_TAG_MANAGER_ID=GTM-XXXXXX
```

#### Paystack
```env
PAYSTACK_PUBLIC_KEY=pk_test_...
PAYSTACK_SECRET_KEY=sk_test_...
PAYSTACK_SUBACCOUNT_CODE=ACCT_...
PLATFORM_FEE_PERCENT=8
```

#### Site Configuration
```env
SITE_URL=https://ekianeonsare.com
DEBUG=False  # Use True for development
```

### Complete Setup Instructions

For comprehensive setup instructions covering all systems, see:
- **[COMPLETE_SYSTEM_INTEGRATION.md](./COMPLETE_SYSTEM_INTEGRATION.md)** - Full integration guide
- **[EMAIL_SETUP.md](./EMAIL_SETUP.md)** - Detailed email configuration
- **[GOOGLE_ANALYTICS_TAB_MANAGEMENT.md](./GOOGLE_ANALYTICS_TAB_MANAGEMENT.md)** - Analytics & tab management guide
- **[CLOUDINARY_SETUP.md](./CLOUDINARY_SETUP.md)** - Media storage (production)