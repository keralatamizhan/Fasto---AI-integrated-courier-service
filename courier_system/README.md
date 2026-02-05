# Smart AI-Enabled Courier Booking & Tracking System

A comprehensive courier booking and tracking system with simulated AI recommendations, mock GPS tracking, and intelligent issue detection.

## Project Overview

This is an MSc Computer Science Final Year Project that implements a smart courier booking system with the following features:

- **User Management**: Registration, login, and profile management
- **Courier Booking**: Step-based booking form with sender, receiver, and parcel details
- **AI Recommendations**: Logic-based AI suggestions for delivery options
- **Dynamic Pricing**: Automatic price calculation based on weight, distance, and delivery option
- **Payment Processing**: Simulated payment system (no real transactions)
- **Real-Time Tracking**: Mock GPS tracking with predefined route points
- **Issue Detection**: Automated delay detection and notification system

## Technology Stack

- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Backend**: Python 3.8+, Django 4.2+
- **Database**: MySQL 8.0+
- **AI**: Simulated logic-based AI (ready for ML integration)

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

### Step 1: Clone/Download the Project

```bash
cd courier_system
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Database Setup

1. Create MySQL database:
```sql
CREATE DATABASE courier_system_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Update database settings in `courier_system/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'courier_system_db',
        'USER': 'your_mysql_username',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Step 5: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### Step 7: Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Project Structure

```
courier_system/
├── accounts/              # User management app
│   ├── models.py         # User model
│   ├── views.py          # Authentication views
│   └── urls.py           # Account URLs
├── bookings/             # Booking management app
│   ├── models.py         # Shipment, Parcel, Tracking models
│   ├── views.py          # Booking views
│   ├── ai_logic.py       # Simulated AI logic
│   └── urls.py           # Booking URLs
├── payments/             # Payment processing app
│   ├── models.py         # Payment model
│   ├── views.py          # Payment views
│   └── urls.py           # Payment URLs
├── tracking/             # Tracking app
│   ├── views.py          # Tracking views
│   ├── mock_gps.py       # Mock GPS tracking logic
│   └── issue_detection.py # Issue detection logic
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── public/           # Public pages
│   ├── accounts/         # User pages
│   ├── bookings/         # Booking pages
│   ├── payments/         # Payment pages
│   └── tracking/         # Tracking pages
└── courier_system/       # Main project settings
    ├── settings.py        # Django settings
    ├── urls.py           # Main URL configuration
    └── views.py          # Public page views
```

## Database Schema

### Tables

1. **users** - Extended user model with profile information
2. **parcel_details** - Parcel information (type, weight, dimensions)
3. **shipments** - Main shipment records
4. **tracking_logs** - GPS tracking history
5. **payments** - Payment records
6. **notifications** - User notifications

## Features

### 1. User Management
- User registration and login
- Profile management with address details
- Secure authentication

### 2. Courier Booking
- 4-step booking process:
  - Step 1: Sender details
  - Step 2: Receiver details
  - Step 3: Parcel details
  - Step 4: Review and select delivery option
- AI-powered delivery option recommendations
- Dynamic pricing calculation

### 3. Simulated AI Features
- **Delivery Option Recommendation**: Suggests best option based on:
  - Weight category
  - Distance between cities
  - Fragile items
  - Cost-effectiveness
- **ETA Estimation**: Calculates estimated delivery time
- **Issue Detection**: Detects delays and potential problems

### 4. Payment System
- Simulated payment processing
- Multiple payment methods (Credit Card, Debit Card, PayPal, Bank Transfer)
- Payment status tracking

### 5. Tracking System
- Mock GPS tracking with predefined route points
- Real-time location updates
- Timeline view of shipment progress
- Status updates (Pending → Confirmed → Picked Up → In Transit → Out for Delivery → Delivered)

### 6. Notifications
- Booking confirmation
- Payment received
- Status updates
- Delay alerts
- Issue notifications

## Usage

1. **Register/Login**: Create an account or login
2. **Book Courier**: Navigate to "Book Courier" and complete the 4-step form
3. **Review AI Recommendations**: See AI-suggested delivery options on step 4
4. **Make Payment**: Complete payment for the booking
5. **Track Shipment**: View real-time tracking with mock GPS coordinates
6. **Receive Notifications**: Get alerts for status changes and delays

## AI Logic Explanation

The simulated AI uses rule-based logic:

1. **Fragile + Heavy Items**: Recommends Express delivery for better handling
2. **Long Distance (>1000 miles)**: Recommends Express or Overnight
3. **Light Items with Small Price Difference**: Recommends faster option
4. **Short Distance (<200 miles)**: Recommends Standard (cost-effective)
5. **Medium Distance (200-500 miles)**: Recommends Standard (eco-friendly)

## Future Enhancements

- Real GPS/Map API integration
- Machine Learning-based delivery prediction
- Mobile application
- Multi-courier support
- Real-time chat support
- Advanced analytics

## Notes

- This is a simulated system - no real payments or GPS tracking
- All AI features are logic-based, ready for ML integration
- Mock GPS uses predefined city coordinates
- Payment processing is simulated (always succeeds)

## License

This project is developed for academic purposes as part of an MSc Computer Science Final Year Project.

## Author

MSc Computer Science Student

## Contact

For questions or support, please use the contact form on the website.
