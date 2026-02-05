from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from bookings.models import Shipment, TrackingLog, Notification
from .mock_gps import get_next_location, initialize_tracking

@login_required
def track_shipment(request, shipment_id):
    """Track shipment with mock GPS"""
    shipment = get_object_or_404(Shipment, shipment_id=shipment_id, user=request.user)
    
    # Initialize tracking if not started
    if shipment.status in ['confirmed', 'picked_up', 'in_transit', 'out_for_delivery']:
        tracking_logs = TrackingLog.objects.filter(shipment=shipment).order_by('timestamp')
        
        # If no tracking logs exist, initialize
        if not tracking_logs.exists():
            initialize_tracking(shipment)
            tracking_logs = TrackingLog.objects.filter(shipment=shipment).order_by('timestamp')
        
        # Get latest location
        latest_log = tracking_logs.last()
        
        # Check for delays and issues
        from .issue_detection import check_delays, detect_issues
        delay_info = check_delays(shipment)
        issues = detect_issues(shipment)
        
        context = {
            'shipment': shipment,
            'tracking_logs': tracking_logs,
            'latest_log': latest_log,
            'delay_info': delay_info,
            'issues': issues,
        }
    else:
        context = {
            'shipment': shipment,
            'tracking_logs': [],
            'latest_log': None,
        }
    
    return render(request, 'tracking/track_shipment.html', context)


@login_required
def update_location(request, shipment_id):
    """Update shipment location (AJAX endpoint for real-time updates)"""
    shipment = get_object_or_404(Shipment, shipment_id=shipment_id, user=request.user)
    
    if shipment.status not in ['picked_up', 'in_transit', 'out_for_delivery']:
        return JsonResponse({'error': 'Tracking not available for this shipment status.'}, status=400)
    
    # Get next location
    latest_log = TrackingLog.objects.filter(shipment=shipment).order_by('-timestamp').first()
    
    if latest_log:
        next_location = get_next_location(
            shipment,
            latest_log.latitude,
            latest_log.longitude
        )
        
        if next_location:
            # Create new tracking log
            tracking_log = TrackingLog.objects.create(
                shipment=shipment,
                latitude=next_location['lat'],
                longitude=next_location['lon'],
                location_name=next_location['name'],
                status=next_location['status'],
                description=next_location.get('description', '')
            )
            
            # Update shipment status if needed
            if next_location['status'] != shipment.status:
                shipment.status = next_location['status']
                if next_location['status'] == 'in_transit' and not shipment.in_transit_at:
                    shipment.in_transit_at = timezone.now()
                shipment.save()
            
            # Check if delivered
            if next_location['status'] == 'delivered':
                shipment.status = 'delivered'
                shipment.actual_delivery_date = timezone.now()
                shipment.save()
                
                Notification.objects.create(
                    user=shipment.user,
                    shipment=shipment,
                    notification_type='delivered',
                    title='Shipment Delivered',
                    message=f'Your shipment {shipment.shipment_id} has been delivered successfully!'
                )
            
            return JsonResponse({
                'success': True,
                'location': {
                    'lat': float(tracking_log.latitude),
                    'lon': float(tracking_log.longitude),
                    'name': tracking_log.location_name,
                    'status': tracking_log.status,
                    'timestamp': tracking_log.timestamp.isoformat(),
                }
            })
    
    return JsonResponse({'success': False, 'message': 'No update available'})
