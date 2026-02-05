"""
Mock GPS Tracking System
Simulates GPS coordinates and shipment movement
"""

from decimal import Decimal
from django.utils import timezone
from bookings.models import TrackingLog

# Predefined route points (mock GPS coordinates)
# These represent cities/checkpoints along common routes
ROUTE_POINTS = {
    'new york': [
        {'lat': Decimal('40.7128'), 'lon': Decimal('-74.0060'), 'name': 'New York, NY'},
        {'lat': Decimal('40.7589'), 'lon': Decimal('-73.9851'), 'name': 'Manhattan Hub'},
        {'lat': Decimal('40.6782'), 'lon': Decimal('-73.9442'), 'name': 'Brooklyn Distribution'},
    ],
    'los angeles': [
        {'lat': Decimal('34.0522'), 'lon': Decimal('-118.2437'), 'name': 'Los Angeles, CA'},
        {'lat': Decimal('34.0522'), 'lon': Decimal('-118.2637'), 'name': 'LA Processing Center'},
        {'lat': Decimal('34.0622'), 'lon': Decimal('-118.2537'), 'name': 'LA Distribution Hub'},
    ],
    'chicago': [
        {'lat': Decimal('41.8781'), 'lon': Decimal('-87.6298'), 'name': 'Chicago, IL'},
        {'lat': Decimal('41.8881'), 'lon': Decimal('-87.6398'), 'name': 'Chicago Hub'},
        {'lat': Decimal('41.8681'), 'lon': Decimal('-87.6198'), 'name': 'Chicago Distribution'},
    ],
    'houston': [
        {'lat': Decimal('29.7604'), 'lon': Decimal('-95.3698'), 'name': 'Houston, TX'},
        {'lat': Decimal('29.7704'), 'lon': Decimal('-95.3798'), 'name': 'Houston Processing'},
        {'lat': Decimal('29.7504'), 'lon': Decimal('-95.3598'), 'name': 'Houston Distribution'},
    ],
    'phoenix': [
        {'lat': Decimal('33.4484'), 'lon': Decimal('-112.0740'), 'name': 'Phoenix, AZ'},
        {'lat': Decimal('33.4584'), 'lon': Decimal('-112.0840'), 'name': 'Phoenix Hub'},
    ],
    'philadelphia': [
        {'lat': Decimal('39.9526'), 'lon': Decimal('-75.1652'), 'name': 'Philadelphia, PA'},
        {'lat': Decimal('39.9626'), 'lon': Decimal('-75.1752'), 'name': 'Philadelphia Hub'},
    ],
    'san antonio': [
        {'lat': Decimal('29.4241'), 'lon': Decimal('-98.4936'), 'name': 'San Antonio, TX'},
        {'lat': Decimal('29.4341'), 'lon': Decimal('-98.5036'), 'name': 'San Antonio Hub'},
    ],
    'san diego': [
        {'lat': Decimal('32.7157'), 'lon': Decimal('-117.1611'), 'name': 'San Diego, CA'},
        {'lat': Decimal('32.7257'), 'lon': Decimal('-117.1711'), 'name': 'San Diego Hub'},
    ],
    'dallas': [
        {'lat': Decimal('32.7767'), 'lon': Decimal('-96.7970'), 'name': 'Dallas, TX'},
        {'lat': Decimal('32.7867'), 'lon': Decimal('-96.8070'), 'name': 'Dallas Hub'},
    ],
    'san jose': [
        {'lat': Decimal('37.3382'), 'lon': Decimal('-121.8863'), 'name': 'San Jose, CA'},
        {'lat': Decimal('37.3482'), 'lon': Decimal('-121.8963'), 'name': 'San Jose Hub'},
    ],
}

# Default route points (used when city not found)
DEFAULT_ROUTE = [
    {'lat': Decimal('40.7128'), 'lon': Decimal('-74.0060'), 'name': 'Origin City'},
    {'lat': Decimal('40.7228'), 'lon': Decimal('-74.0160'), 'name': 'Distribution Center'},
    {'lat': Decimal('40.7328'), 'lon': Decimal('-74.0260'), 'name': 'Transit Hub'},
    {'lat': Decimal('40.7428'), 'lon': Decimal('-74.0360'), 'name': 'Destination City'},
]


def get_route_points(sender_city, receiver_city):
    """Get route points between sender and receiver cities"""
    sender_lower = sender_city.lower()
    receiver_lower = receiver_city.lower()
    
    sender_points = ROUTE_POINTS.get(sender_lower, DEFAULT_ROUTE[:2])
    receiver_points = ROUTE_POINTS.get(receiver_lower, DEFAULT_ROUTE[-2:])
    
    # Combine routes with intermediate points
    route = sender_points.copy()
    
    # Add intermediate transit points (simplified)
    if sender_lower != receiver_lower:
        # Add a transit hub (midpoint concept)
        mid_lat = (sender_points[-1]['lat'] + receiver_points[0]['lat']) / 2
        mid_lon = (sender_points[-1]['lon'] + receiver_points[0]['lon']) / 2
        route.append({
            'lat': mid_lat,
            'lon': mid_lon,
            'name': 'Transit Hub'
        })
    
    route.extend(receiver_points)
    return route


def initialize_tracking(shipment):
    """Initialize tracking with first location"""
    route_points = get_route_points(shipment.sender_city, shipment.receiver_city)
    
    if shipment.status == 'confirmed':
        # Starting point - sender location
        first_point = route_points[0]
        TrackingLog.objects.create(
            shipment=shipment,
            latitude=first_point['lat'],
            longitude=first_point['lon'],
            location_name=f"Pickup Location - {shipment.sender_city}",
            status='confirmed',
            description='Shipment confirmed, awaiting pickup'
        )
    elif shipment.status == 'picked_up':
        # Already picked up
        first_point = route_points[0]
        TrackingLog.objects.create(
            shipment=shipment,
            latitude=first_point['lat'],
            longitude=first_point['lon'],
            location_name=f"Picked Up - {shipment.sender_city}",
            status='picked_up',
            description='Shipment picked up from sender'
        )


def get_next_location(shipment, current_lat, current_lon):
    """Get next location in the route"""
    route_points = get_route_points(shipment.sender_city, shipment.receiver_city)
    tracking_logs = TrackingLog.objects.filter(shipment=shipment).order_by('timestamp')
    
    # Find current position in route
    current_index = 0
    min_distance = float('inf')
    
    for i, point in enumerate(route_points):
        # Calculate distance (simplified)
        lat_diff = abs(float(point['lat']) - float(current_lat))
        lon_diff = abs(float(point['lon']) - float(current_lon))
        distance = lat_diff + lon_diff
        
        if distance < min_distance:
            min_distance = distance
            current_index = i
    
    # Get next point
    next_index = current_index + 1
    
    if next_index >= len(route_points):
        # Reached destination
        return {
            'lat': route_points[-1]['lat'],
            'lon': route_points[-1]['lon'],
            'name': f"Delivered - {shipment.receiver_city}",
            'status': 'delivered',
            'description': f'Delivered to {shipment.receiver_name} at {shipment.receiver_address}'
        }
    
    next_point = route_points[next_index]
    
    # Determine status based on progress
    progress = (next_index + 1) / len(route_points)
    
    if progress < 0.3:
        status = 'picked_up'
    elif progress < 0.7:
        status = 'in_transit'
    elif progress < 1.0:
        status = 'out_for_delivery'
    else:
        status = 'delivered'
    
    return {
        'lat': next_point['lat'],
        'lon': next_point['lon'],
        'name': next_point['name'],
        'status': status,
        'description': f'In transit to {next_point["name"]}'
    }
