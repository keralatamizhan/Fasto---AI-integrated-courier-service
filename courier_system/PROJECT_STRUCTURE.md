# Project Structure & Module-Wise Explanation

## Navigation Flow

### Public Pages (Unauthenticated Users)
1. **Home** (`/`) - Landing page with features and how it works
2. **About Us** (`/about/`) - Project information and technology stack
3. **Services** (`/services/`) - Service offerings and pricing
4. **Contact Us** (`/contact/`) - Contact form
5. **Register** (`/accounts/register/`) - User registration
6. **Login** (`/accounts/login/`) - User login

### Authenticated User Pages
1. **Dashboard** (`/accounts/dashboard/`) - Main dashboard with statistics and recent shipments
2. **Profile** (`/accounts/profile/`) - User profile management
3. **Book Courier** (`/bookings/book/`) - 4-step booking process
4. **My Shipments** (`/bookings/list/`) - List of all user shipments
5. **Payment** (`/payments/payment/<shipment_id>/`) - Payment page
6. **Track Shipment** (`/tracking/track/<shipment_id>/`) - Real-time tracking

## Module-Wise Explanation

### 1. User Management Module (`accounts/`)

**Purpose**: Handle user authentication, registration, and profile management.

**Components**:
- **models.py**: Extended User model with phone, address, and profile picture
- **views.py**: 
  - `register()` - User registration
  - `login_view()` - User authentication
  - `logout_view()` - User logout
  - `dashboard()` - Main dashboard with statistics
  - `profile()` - Profile view
  - `update_profile()` - Profile update
- **urls.py**: URL routing for account-related pages
- **Templates**:
  - `register.html` - Registration form
  - `login.html` - Login form
  - `dashboard.html` - Dashboard with sidebar navigation
  - `profile.html` - Profile management form

**Features**:
- Secure password hashing
- Session-based authentication
- Profile picture upload
- Address management

### 2. Booking Module (`bookings/`)

**Purpose**: Handle courier booking process with step-based form and AI recommendations.

**Components**:
- **models.py**:
  - `ParcelDetail` - Parcel information
  - `Shipment` - Main shipment record
  - `TrackingLog` - GPS tracking history
  - `Notification` - User notifications
- **views.py**:
  - `book_courier()` - Main booking entry point
  - `book_courier_step()` - Step-based booking form (4 steps)
  - `confirm_booking()` - Create shipment record
  - `shipment_list()` - List all user shipments
  - `shipment_detail()` - View shipment details
- **ai_logic.py**: Simulated AI logic
  - `calculate_pricing()` - Dynamic pricing calculation
  - `estimate_delivery_time()` - ETA estimation
  - `get_ai_recommendation()` - AI recommendation engine
  - `calculate_distance()` - Distance calculation between cities
- **Templates**:
  - `step_1.html` - Sender details form
  - `step_2.html` - Receiver details form
  - `step_3.html` - Parcel details form
  - `step_4.html` - Review and delivery option selection
  - `shipment_list.html` - List of shipments
  - `shipment_detail.html` - Shipment details view

**Features**:
- 4-step booking process with session storage
- AI-powered delivery option recommendations
- Dynamic pricing based on weight, distance, and options
- Fragile item handling
- Automatic shipment ID generation

### 3. Payment Module (`payments/`)

**Purpose**: Handle payment processing (simulated).

**Components**:
- **models.py**:
  - `Payment` - Payment records
- **views.py**:
  - `payment()` - Payment page
  - `process_payment()` - Simulated payment processing
  - `payment_success()` - Payment success page
- **Templates**:
  - `payment.html` - Payment form
  - `payment_success.html` - Success confirmation

**Features**:
- Multiple payment methods (Credit Card, Debit Card, PayPal, Bank Transfer)
- Simulated payment processing (always succeeds)
- Payment status tracking
- Transaction ID generation
- Automatic shipment status update after payment

### 4. Tracking Module (`tracking/`)

**Purpose**: Real-time shipment tracking with mock GPS.

**Components**:
- **views.py**:
  - `track_shipment()` - Main tracking page
  - `update_location()` - AJAX endpoint for location updates
- **mock_gps.py**: Mock GPS tracking logic
  - `get_route_points()` - Get route between cities
  - `initialize_tracking()` - Initialize tracking logs
  - `get_next_location()` - Get next location in route
- **issue_detection.py**: Issue detection system
  - `check_delays()` - Detect delivery delays
  - `detect_issues()` - Detect various shipment issues
- **Templates**:
  - `track_shipment.html` - Tracking page with timeline

**Features**:
- Mock GPS tracking with predefined city coordinates
- Real-time location updates
- Timeline view of shipment progress
- Automatic delay detection
- Issue detection and alerts
- Auto-refresh functionality

### 5. Public Pages Module (`courier_system/views.py`)

**Purpose**: Public-facing pages for marketing and information.

**Components**:
- `home()` - Landing page
- `about()` - About us page
- `services()` - Services page
- `contact()` - Contact form handler

**Templates**:
- `public/home.html` - Landing page
- `public/about.html` - About page
- `public/services.html` - Services page
- `public/contact.html` - Contact page

## AI Logic Explanation

### Simulated AI Features

1. **Delivery Option Recommendation** (`bookings/ai_logic.py`)
   - Analyzes weight category, distance, and fragile status
   - Uses rule-based logic to recommend best option
   - Considers cost-effectiveness and delivery speed
   - Provides reasoning for recommendations

2. **Pricing Calculation**
   - Base prices for each delivery option and weight category
   - Additional charges for fragile items
   - Weight-based surcharges for extra heavy items
   - Dynamic total calculation

3. **ETA Estimation**
   - Calculates distance between cities
   - Uses average speeds for each delivery option
   - Adds processing time
   - Returns estimated hours

4. **Issue Detection** (`tracking/issue_detection.py`)
   - Monitors delivery delays
   - Detects stuck shipments
   - Identifies missing tracking updates
   - Creates automatic notifications

## Mock GPS System

### How It Works

1. **Predefined Routes**: City coordinates stored in `ROUTE_POINTS` dictionary
2. **Route Generation**: Creates route between sender and receiver cities
3. **Step-by-Step Movement**: Simulates movement through route points
4. **Status Updates**: Updates shipment status based on progress
5. **Location Logging**: Creates tracking logs at each point

### Route Points

- Major US cities have predefined coordinates
- Intermediate transit hubs added automatically
- Default route used for unknown cities

## Database Flow

1. **User Registration** → Creates `users` record
2. **Booking** → Creates `parcel_details` and `shipments` records
3. **Payment** → Creates `payments` record, updates shipment status
4. **Tracking** → Creates `tracking_logs` records as shipment moves
5. **Notifications** → Creates `notifications` records for events

## Status Flow

```
pending → confirmed → picked_up → in_transit → out_for_delivery → delivered
```

## Key Features Implementation

### 1. Step-Based Booking
- Uses Django sessions to store form data
- Progressive form completion
- Data validation at each step
- Review before final submission

### 2. AI Recommendations
- Logic-based rules (ready for ML integration)
- Considers multiple factors
- Provides reasoning
- Displays on step 4 of booking

### 3. Dynamic Pricing
- Calculated in real-time
- Based on weight, distance, and options
- Additional charges for special handling
- Transparent pricing display

### 4. Real-Time Tracking
- Mock GPS coordinates
- Timeline visualization
- Auto-refresh capability
- Status-based updates

### 5. Notification System
- Automatic notifications for:
  - Booking confirmation
  - Payment received
  - Status changes
  - Delays detected
  - Issues found

## Security Features

- Password hashing (Django default)
- CSRF protection
- SQL injection prevention (Django ORM)
- XSS protection (template escaping)
- Authentication required for protected pages
- Session-based authentication

## Responsive Design

- Bootstrap 5 framework
- Mobile-friendly navigation
- Responsive tables and cards
- Sidebar navigation for dashboard
- Touch-friendly buttons and forms

## Future Enhancement Ready

The system is architected to easily integrate:
- Real GPS APIs (replace mock_gps.py)
- Machine Learning models (replace ai_logic.py)
- Real payment gateways (replace payment processing)
- Mobile app (REST API ready)
- Real-time WebSocket updates (tracking)

## Testing Recommendations

1. **User Flow**: Register → Login → Book → Pay → Track
2. **AI Recommendations**: Test with different weights and distances
3. **Tracking**: Verify mock GPS updates
4. **Notifications**: Check automatic notification creation
5. **Issue Detection**: Test delay scenarios

## Deployment Notes

- Update `SECRET_KEY` in production
- Set `DEBUG = False` in production
- Configure proper database credentials
- Set up static file serving
- Configure media file storage
- Use environment variables for sensitive data
