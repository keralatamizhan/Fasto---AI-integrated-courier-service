"""
Simulated AI Logic for Courier System
This module provides logic-based AI recommendations and calculations
"""

from decimal import Decimal
from datetime import timedelta

# Mock city coordinates for distance calculation
CITY_COORDINATES = {
    'new york': {'lat': 40.7128, 'lon': -74.0060},
    'los angeles': {'lat': 34.0522, 'lon': -118.2437},
    'chicago': {'lat': 41.8781, 'lon': -87.6298},
    'houston': {'lat': 29.7604, 'lon': -95.3698},
    'phoenix': {'lat': 33.4484, 'lon': -112.0740},
    'philadelphia': {'lat': 39.9526, 'lon': -75.1652},
    'san antonio': {'lat': 29.4241, 'lon': -98.4936},
    'san diego': {'lat': 32.7157, 'lon': -117.1611},
    'dallas': {'lat': 32.7767, 'lon': -96.7970},
    'san jose': {'lat': 37.3382, 'lon': -121.8863},
}

# Base pricing per weight category and delivery option
BASE_PRICES = {
    'standard': {
        'light': Decimal('15.00'),
        'medium': Decimal('25.00'),
        'heavy': Decimal('40.00'),
        'extra_heavy': Decimal('60.00'),
    },
    'express': {
        'light': Decimal('30.00'),
        'medium': Decimal('45.00'),
        'heavy': Decimal('65.00'),
        'extra_heavy': Decimal('90.00'),
    },
    'overnight': {
        'light': Decimal('50.00'),
        'medium': Decimal('75.00'),
        'heavy': Decimal('100.00'),
        'extra_heavy': Decimal('140.00'),
    },
}

def calculate_distance(city1, city2):
    """Calculate approximate distance between two cities (simplified)"""
    city1_lower = city1.lower()
    city2_lower = city2.lower()
    
    if city1_lower not in CITY_COORDINATES or city2_lower not in CITY_COORDINATES:
        # Default distance if city not found
        return 500  # miles
    
    coord1 = CITY_COORDINATES[city1_lower]
    coord2 = CITY_COORDINATES[city2_lower]
    
    # Simplified distance calculation (Haversine formula approximation)
    from math import radians, sin, cos, sqrt, atan2
    
    lat1, lon1 = radians(coord1['lat']), radians(coord1['lon'])
    lat2, lon2 = radians(coord2['lat']), radians(coord2['lon'])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    distance_miles = 3959 * c  # Earth radius in miles
    return distance_miles


def calculate_pricing(delivery_option, weight_category, weight_kg, fragile=False, return_breakdown=False):
    """Calculate pricing based on delivery option, weight, and additional factors"""
    base_price = BASE_PRICES[delivery_option][weight_category]
    
    # Additional charges
    additional_charges = Decimal('0.00')
    
    # Fragile handling fee
    if fragile:
        additional_charges += Decimal('10.00')
    
    # Weight-based surcharge for extra heavy
    if weight_category == 'extra_heavy' and weight_kg > Decimal('15'):
        additional_charges += Decimal('5.00') * (weight_kg - Decimal('15'))
    
    total_price = base_price + additional_charges
    
    if return_breakdown:
        return base_price, additional_charges, total_price
    return total_price


def estimate_delivery_time(delivery_option, sender_city, receiver_city):
    """Estimate delivery time in hours"""
    distance = calculate_distance(sender_city, receiver_city)
    
    # Base speeds (miles per hour)
    speeds = {
        'standard': 50,  # Average truck speed
        'express': 60,   # Faster truck
        'overnight': 70, # Express truck
    }
    
    # Base time + distance-based time
    base_hours = {
        'standard': 24,  # Processing time
        'express': 12,
        'overnight': 6,
    }
    
    speed = speeds[delivery_option]
    base_time = base_hours[delivery_option]
    
    # Calculate travel time
    travel_hours = distance / speed
    
    # Total estimated hours
    total_hours = base_time + travel_hours
    
    return int(total_hours)


def get_ai_recommendation(weight_category, weight_kg, sender_city, receiver_city, fragile=False):
    """
    Simulated AI recommendation system
    Returns best delivery option based on logic-based rules
    """
    distance = calculate_distance(sender_city, receiver_city)
    
    # Calculate prices for all options
    standard_price = calculate_pricing('standard', weight_category, weight_kg, fragile)
    express_price = calculate_pricing('express', weight_category, weight_kg, fragile)
    overnight_price = calculate_pricing('overnight', weight_category, weight_kg, fragile)
    
    # AI Logic Rules
    recommendation = {
        'option': 'standard',
        'eta_hours': estimate_delivery_time('standard', sender_city, receiver_city),
        'reason': 'Standard delivery recommended for cost-effectiveness.'
    }
    
    # Rule 1: If fragile and heavy, recommend express (better handling)
    if fragile and weight_category in ['heavy', 'extra_heavy']:
        recommendation = {
            'option': 'express',
            'eta_hours': estimate_delivery_time('express', sender_city, receiver_city),
            'reason': 'Express delivery recommended for fragile and heavy items to ensure better handling and faster delivery.'
        }
    
    # Rule 2: If distance > 1000 miles, recommend express or overnight
    elif distance > 1000:
        if weight_category == 'light':
            recommendation = {
                'option': 'overnight',
                'eta_hours': estimate_delivery_time('overnight', sender_city, receiver_city),
                'reason': 'Overnight delivery recommended for long-distance light parcels to ensure timely delivery.'
            }
        else:
            recommendation = {
                'option': 'express',
                'eta_hours': estimate_delivery_time('express', sender_city, receiver_city),
                'reason': 'Express delivery recommended for long-distance shipments to reduce transit time.'
            }
    
    # Rule 3: If weight is light and price difference is small, recommend faster option
    elif weight_category == 'light' and (express_price - standard_price) < Decimal('20.00'):
        recommendation = {
            'option': 'express',
            'eta_hours': estimate_delivery_time('express', sender_city, receiver_city),
            'reason': 'Express delivery recommended for light items with minimal price difference for faster service.'
        }
    
    # Rule 4: If distance < 200 miles, standard is usually sufficient
    elif distance < 200:
        recommendation = {
            'option': 'standard',
            'eta_hours': estimate_delivery_time('standard', sender_city, receiver_city),
            'reason': 'Standard delivery is cost-effective for short-distance shipments.'
        }
    
    # Rule 5: Eco-friendly option (cheapest for medium distances)
    elif 200 <= distance <= 500:
        recommendation = {
            'option': 'standard',
            'eta_hours': estimate_delivery_time('standard', sender_city, receiver_city),
            'reason': 'Standard delivery recommended for medium distances - eco-friendly and cost-effective.'
        }
    
    return recommendation
