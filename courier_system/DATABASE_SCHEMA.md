# Database Schema Documentation

## Overview

The Smart Courier System uses MySQL database with the following tables:

## Tables

### 1. users
Extended Django User model with additional customer information.

| Column | Type | Description |
|--------|------|-------------|
| id | INT (PK) | Primary key |
| username | VARCHAR(150) | Unique username |
| email | VARCHAR(254) | Email address |
| password | VARCHAR(128) | Hashed password |
| first_name | VARCHAR(150) | First name |
| last_name | VARCHAR(150) | Last name |
| phone_number | VARCHAR(17) | Phone number |
| address | TEXT | Street address |
| city | VARCHAR(100) | City |
| state | VARCHAR(100) | State/Province |
| postal_code | VARCHAR(20) | Postal/ZIP code |
| country | VARCHAR(100) | Country |
| profile_picture | VARCHAR(100) | Profile image path |
| created_at | DATETIME | Account creation timestamp |
| updated_at | DATETIME | Last update timestamp |

### 2. parcel_details
Stores parcel/shipment item information.

| Column | Type | Description |
|--------|------|-------------|
| id | INT (PK) | Primary key |
| parcel_type | VARCHAR(100) | Type of parcel (e.g., Documents, Electronics) |
| weight_category | VARCHAR(20) | Weight category (light/medium/heavy/extra_heavy) |
| weight_kg | DECIMAL(5,2) | Weight in kilograms |
| dimensions_length | DECIMAL(5,2) | Length in cm (nullable) |
| dimensions_width | DECIMAL(5,2) | Width in cm (nullable) |
| dimensions_height | DECIMAL(5,2) | Height in cm (nullable) |
| description | TEXT | Additional description |
| fragile | BOOLEAN | Fragile item flag |
| created_at | DATETIME | Creation timestamp |

### 3. shipments
Main shipment record with sender, receiver, and delivery information.

| Column | Type | Description |
|--------|------|-------------|
| id | INT (PK) | Primary key |
| shipment_id | VARCHAR(20) | Unique shipment identifier (SHXXXXXXXX) |
| user_id | INT (FK) | Reference to users table |
| parcel_id | INT (FK) | Reference to parcel_details table |
| sender_name | VARCHAR(200) | Sender full name |
| sender_phone | VARCHAR(20) | Sender phone number |
| sender_address | TEXT | Sender address |
| sender_city | VARCHAR(100) | Sender city |
| sender_state | VARCHAR(100) | Sender state |
| sender_postal_code | VARCHAR(20) | Sender postal code |
| sender_country | VARCHAR(100) | Sender country |
| receiver_name | VARCHAR(200) | Receiver full name |
| receiver_phone | VARCHAR(20) | Receiver phone number |
| receiver_address | TEXT | Receiver address |
| receiver_city | VARCHAR(100) | Receiver city |
| receiver_state | VARCHAR(100) | Receiver state |
| receiver_postal_code | VARCHAR(20) | Receiver postal code |
| receiver_country | VARCHAR(100) | Receiver country |
| delivery_option | VARCHAR(20) | Delivery option (standard/express/overnight) |
| estimated_delivery_date | DATETIME | Estimated delivery date/time |
| actual_delivery_date | DATETIME | Actual delivery date/time (nullable) |
| status | VARCHAR(20) | Shipment status |
| base_price | DECIMAL(10,2) | Base price |
| additional_charges | DECIMAL(10,2) | Additional charges (fragile, etc.) |
| total_price | DECIMAL(10,2) | Total price |
| ai_recommended_option | VARCHAR(20) | AI recommended delivery option |
| ai_eta_hours | INT | AI estimated hours |
| ai_reason | TEXT | AI recommendation reason |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Last update timestamp |
| picked_up_at | DATETIME | Pickup timestamp (nullable) |
| in_transit_at | DATETIME | In transit timestamp (nullable) |

**Status Values:**
- pending
- confirmed
- picked_up
- in_transit
- out_for_delivery
- delivered
- cancelled

### 4. tracking_logs
GPS tracking history for shipments.

| Column | Type | Description |
|--------|------|-------------|
| id | INT (PK) | Primary key |
| shipment_id | INT (FK) | Reference to shipments table |
| latitude | DECIMAL(9,6) | GPS latitude |
| longitude | DECIMAL(9,6) | GPS longitude |
| location_name | VARCHAR(200) | Location name/description |
| status | VARCHAR(50) | Status at this location |
| description | TEXT | Additional description |
| timestamp | DATETIME | Tracking timestamp |

### 5. payments
Payment records for shipments.

| Column | Type | Description |
|--------|------|-------------|
| id | INT (PK) | Primary key |
| payment_id | VARCHAR(50) | Unique payment identifier (PAYXXXXXXXX) |
| shipment_id | INT (FK) | Reference to shipments table (OneToOne) |
| user_id | INT (FK) | Reference to users table |
| amount | DECIMAL(10,2) | Payment amount |
| payment_method | VARCHAR(20) | Payment method |
| payment_status | VARCHAR(20) | Payment status |
| card_last_four | VARCHAR(4) | Last 4 digits of card (nullable) |
| transaction_id | VARCHAR(100) | Transaction ID (nullable) |
| created_at | DATETIME | Creation timestamp |
| processed_at | DATETIME | Processing timestamp (nullable) |
| completed_at | DATETIME | Completion timestamp (nullable) |

**Payment Status Values:**
- pending
- processing
- completed
- failed
- refunded

**Payment Method Values:**
- credit_card
- debit_card
- paypal
- bank_transfer

### 6. notifications
User notifications for various events.

| Column | Type | Description |
|--------|------|-------------|
| id | INT (PK) | Primary key |
| user_id | INT (FK) | Reference to users table |
| shipment_id | INT (FK) | Reference to shipments table (nullable) |
| notification_type | VARCHAR(30) | Notification type |
| title | VARCHAR(200) | Notification title |
| message | TEXT | Notification message |
| is_read | BOOLEAN | Read status |
| created_at | DATETIME | Creation timestamp |

**Notification Types:**
- booking_confirmed
- payment_received
- picked_up
- in_transit
- out_for_delivery
- delivered
- delay_alert
- issue_detected

## Relationships

1. **User → Shipments**: One-to-Many (one user can have many shipments)
2. **Shipment → Parcel**: One-to-One (one shipment has one parcel)
3. **Shipment → Payment**: One-to-One (one shipment has one payment)
4. **Shipment → Tracking Logs**: One-to-Many (one shipment has many tracking logs)
5. **User → Notifications**: One-to-Many (one user has many notifications)
6. **Shipment → Notifications**: One-to-Many (one shipment can have multiple notifications)

## Indexes

- `shipment_id` (shipments) - Unique index
- `payment_id` (payments) - Unique index
- `user_id` - Foreign key indexes on all related tables
- `shipment_id` - Foreign key indexes on tracking_logs and notifications

## Notes

- All timestamps use UTC timezone
- Decimal fields use appropriate precision for currency and measurements
- Foreign keys have CASCADE delete where appropriate
- Unique constraints ensure data integrity
