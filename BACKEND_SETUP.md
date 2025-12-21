# Django Backend Setup Guide

## Overview
This is the Django REST API backend for the Ultamine Pro Hub earning platform. It handles all business logic including:
- User authentication and management
- Mining package management
- Investment deposits and approvals
- Daily earning calculations
- Referral system
- Withdrawal requests
- Product catalog and orders

## Prerequisites
- Python 3.10+
- PostgreSQL (or use the provided Neon database)
- Virtual environment tool

## Installation

### 1. Create and Activate Virtual Environment
```bash
cd backend
python -m venv venv

# On Windows:
.\venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the backend directory:
```bash
cp .env.example .env
```

Configure the `.env` file with your database credentials. The provided Neon PostgreSQL connection is already in the `.env.example`.

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Create Initial Data
```bash
python manage.py setup_initial_data
```

This creates:
- 13 Mining packages (from PKR 500 to PKR 250,000)
- ROI setting (0.8% - 1.2%)
- Auto reinvest setting (30%)

### 6. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 7. Run Development Server
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`
Admin panel: `http://localhost:8000/admin`

## API Endpoints

### Authentication
- `POST /api/users/auth/register/` - Register new user
- `POST /api/users/auth/login/` - Login user
- `GET /api/users/auth/me/` - Get current user profile
- `PUT /api/users/auth/update_profile/` - Update user profile
- `POST /api/users/auth/logout/` - Logout user

### Packages & Deposits
- `GET /api/core/packages/` - List all packages
- `POST /api/core/deposits/` - Create deposit request
- `GET /api/core/deposits/my_deposits/` - Get user's deposits
- `GET /api/core/deposits/pending/` - Get pending deposits (admin only)
- `POST /api/core/deposits/{id}/approve/` - Approve deposit (admin only)
- `POST /api/core/deposits/{id}/reject/` - Reject deposit (admin only)

### Wallet & Transactions
- `GET /api/core/wallet/my_wallet/` - Get wallet details
- `GET /api/core/wallet/balance/` - Get wallet balance
- `GET /api/core/transactions/` - Get transaction history
- `GET /api/core/daily-earnings/my_earnings/` - Get daily earnings

### Referrals
- `GET /api/users/auth/referral_code/` - Get referral code
- `GET /api/users/auth/my_referrals/` - Get referred users
- `GET /api/core/referrals/my_team/` - Get team statistics
- `GET /api/core/referrals/team_statistics/` - Get detailed team stats

### Withdrawals
- `POST /api/core/withdrawals/` - Create withdrawal request
- `GET /api/core/withdrawals/my_withdrawals/` - Get user's withdrawals
- `GET /api/core/withdrawals/pending/` - Get pending withdrawals (admin only)
- `POST /api/core/withdrawals/{id}/approve/` - Approve withdrawal (admin only)
- `POST /api/core/withdrawals/{id}/reject/` - Reject withdrawal (admin only)

### Products & Orders
- `GET /api/core/products/` - List products
- `GET /api/core/products/categories/` - Get product categories
- `GET /api/core/products/by_category/` - Get products by category
- `POST /api/core/orders/` - Create order
- `GET /api/core/orders/my_orders/` - Get user's orders
- `GET /api/core/orders/pending/` - Get pending orders (admin only)
- `POST /api/core/orders/{id}/confirm/` - Confirm order (admin only)
- `POST /api/core/orders/{id}/deliver/` - Mark order delivered (admin only)

### Settings (Admin Only)
- `GET /api/core/roi-settings/current/` - Get current ROI setting
- `GET /api/core/reinvest-settings/current/` - Get current reinvest setting
- `PUT /api/core/roi-settings/{id}/` - Update ROI setting
- `PUT /api/core/reinvest-settings/{id}/` - Update reinvest setting

## Scheduled Tasks

### Daily Earnings Calculation
Run this command daily (preferably at midnight):
```bash
python manage.py calculate_daily_earnings
```

This command:
1. Calculates mining income for all active deposits
2. Calculates ROI earnings based on wallet balance
3. Processes auto reinvestment (30% by default)
4. Processes referral commissions (5% Level 1, 2% Level 2, 1% Level 3)

### Setting Up Celery (Optional)
For production, you can use Celery with Redis to automate daily calculations:

```bash
pip install celery redis
```

Then configure in `config/celery.py` and set up scheduled tasks.

## Admin Panel Features

### User Management
- View all users with verification status
- Suspend or ban users
- View user referral info

### Deposit Management
- View pending deposits
- Approve/reject deposits with bulk actions
- Track deposit history

### Package Management
- Create new mining packages
- Edit existing packages
- Set daily earnings

### Withdrawal Management
- View pending withdrawals
- Approve/reject with explanations
- Track withdrawal history

### Order Management
- View pending orders
- Confirm and mark as delivered
- Track order status

### Settings Management
- Adjust ROI percentage range
- Change auto-reinvest percentage
- Configure system settings

## Database Schema

### Core Models
- **User**: Custom user with referral system
- **MiningPackage**: Investment packages
- **Deposit**: Investment deposits with approval workflow
- **Wallet**: User wallet with balances
- **DailyEarning**: Daily mining and ROI records
- **Transaction**: All financial transactions
- **Referral**: Referral relationships and earnings
- **Withdrawal**: Withdrawal requests with approvals
- **Product**: Catalog products
- **Order**: Product orders with COD/Bank Transfer
- **ROISetting**: System ROI percentage settings
- **ReinvestSetting**: Auto-reinvest percentage

## Key Features

### Approval Workflow
- All deposits require admin approval before activation
- Only approved deposits generate earnings
- Withdrawals require referral checks and approval

### Automatic Calculations
- Daily mining income = package.daily_earning
- Daily ROI = wallet.balance * roi_percentage / 100
- Auto-reinvest = (mining + roi) * reinvest_percentage / 100
- Referral commission = earned_amount * commission_percentage / 100

### Withdrawal Rules
- Minimum withdrawal: PKR 1,000
- First withdrawal: No referral requirement
- Subsequent withdrawals: Require 2+ referrals
- Auto 20% tax deduction
- Admin approval required

### Referral System
- Level 1: 5% commission (direct referrals)
- Level 2: 2% commission (second level)
- Level 3: 1% commission (third level)
- Automatic referral tracking on deposit

### Shopping Features
- 10% discount for authenticated users
- Guest checkout supported
- COD and Bank Transfer payment options
- 3-step order management (Pending → Confirmed → Delivered)

## Troubleshooting

### Database Connection Issues
Ensure PostgreSQL is running and connection string is correct in `.env`

### Port Already in Use
```bash
python manage.py runserver 8001  # Use different port
```

### Migration Errors
```bash
python manage.py migrate --fake-initial  # If needed
python manage.py migrate zero <app_name>  # To rollback
```

### Permission Errors
Ensure admin user is created with `createsuperuser`

## Development Tips

1. **Test User Registration**:
   ```bash
   curl -X POST http://localhost:8000/api/users/auth/register/ \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"testpass123","password2":"testpass123"}'
   ```

2. **Get Auth Token**:
   ```bash
   curl -X POST http://localhost:8000/api/users/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"testpass123"}'
   ```

3. **Use Token in Requests**:
   ```bash
   curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/core/wallet/balance/
   ```

## Environment Variables

- `SECRET_KEY`: Django secret key for security
- `DEBUG`: Set to False in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed domains
- `DATABASE_*`: PostgreSQL connection details
- `CORS_ALLOWED_ORIGINS`: Frontend URLs for CORS

## Security Notes

1. Never commit `.env` to version control
2. Use strong SECRET_KEY in production
3. Set DEBUG=False in production
4. Use HTTPS in production
5. Configure appropriate CORS settings
6. Regularly backup database
7. Use environment variables for sensitive data

## Support

For issues or questions, contact the development team.
