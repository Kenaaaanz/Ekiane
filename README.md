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

Update the Paystack keys and subaccount in `ecommerce/settings.py`:

- `PAYSTACK_PUBLIC_KEY`
- `PAYSTACK_SECRET_KEY`
- `PAYSTACK_SUBACCOUNT_CODE`
- `PLATFORM_FEE_PERCENT`

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