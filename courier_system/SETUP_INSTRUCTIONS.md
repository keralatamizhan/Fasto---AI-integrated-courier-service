# Quick Setup Instructions

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.8+ installed
- ✅ MySQL 8.0+ installed and running
- ✅ pip (Python package manager)

## Step-by-Step Setup

### 1. Navigate to Project Directory
```bash
cd courier_system
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: If `mysqlclient` installation fails on Windows, you may need to:
- Install MySQL Connector/C or use `pip install mysql-connector-python`
- Update `settings.py` to use `mysql.connector.django` backend

### 4. Create MySQL Database
```sql
CREATE DATABASE courier_system_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Configure Database Settings
Edit `courier_system/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'courier_system_db',
        'USER': 'your_username',      # Change this
        'PASSWORD': 'your_password',  # Change this
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 6. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 8. Run Development Server
```bash
python manage.py runserver
```

### 9. Access the Application
Open your browser and navigate to:
- **Home**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/ (if superuser created)

## Testing the System

### 1. Register a New User
- Go to http://127.0.0.1:8000/accounts/register/
- Fill in the registration form
- Login with your credentials

### 2. Book a Courier
- Click "Book Courier" from dashboard
- Complete all 4 steps:
  - Step 1: Enter sender details
  - Step 2: Enter receiver details
  - Step 3: Enter parcel details
  - Step 4: Review and select delivery option (see AI recommendations)
- Confirm booking

### 3. Make Payment
- After booking, you'll be redirected to payment page
- Fill in payment details (simulated - any card number works)
- Complete payment

### 4. Track Shipment
- Go to "My Shipments" or click "Track" from dashboard
- View real-time tracking with mock GPS
- Click "Refresh Location" to simulate movement

## Troubleshooting

### Issue: MySQL Connection Error
**Solution**: 
- Verify MySQL is running
- Check database credentials in settings.py
- Ensure database exists

### Issue: mysqlclient Installation Fails
**Solution (Windows)**:
```bash
pip install mysql-connector-python
```
Then update settings.py:
```python
'ENGINE': 'mysql.connector.django',
```

### Issue: Migration Errors
**Solution**:
```bash
python manage.py makemigrations --run-syncdb
python manage.py migrate
```

### Issue: Static Files Not Loading
**Solution**:
```bash
python manage.py collectstatic
```

## Project Files Overview

### Core Django Files
- `manage.py` - Django management script
- `courier_system/settings.py` - Project settings
- `courier_system/urls.py` - Main URL configuration

### Apps
- `accounts/` - User management
- `bookings/` - Booking system
- `payments/` - Payment processing
- `tracking/` - Tracking system

### Templates
- `templates/base.html` - Base template
- `templates/public/` - Public pages
- `templates/accounts/` - User pages
- `templates/bookings/` - Booking pages
- `templates/payments/` - Payment pages
- `templates/tracking/` - Tracking pages

### Documentation
- `README.md` - Main documentation
- `DATABASE_SCHEMA.md` - Database structure
- `PROJECT_STRUCTURE.md` - Module explanations
- `SETUP_INSTRUCTIONS.md` - This file

## Next Steps

1. ✅ Complete setup and test basic functionality
2. ✅ Create test user and make a booking
3. ✅ Test AI recommendations with different scenarios
4. ✅ Verify tracking system works
5. ✅ Check notifications are created
6. ✅ Test issue detection

## Important Notes

- **No Real Payments**: Payment system is simulated
- **Mock GPS**: Tracking uses predefined coordinates
- **Simulated AI**: AI features are logic-based (ready for ML)
- **Development Mode**: DEBUG=True for development only

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Review PROJECT_STRUCTURE.md for module explanations
3. Check DATABASE_SCHEMA.md for database structure
4. Review code comments in source files

## Production Deployment

Before deploying to production:
1. Set `DEBUG = False`
2. Generate new `SECRET_KEY`
3. Configure proper database
4. Set up static file serving
5. Configure media file storage
6. Use environment variables for sensitive data
7. Set up proper logging
8. Configure HTTPS
9. Set up backup system
10. Review security settings
