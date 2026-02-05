"""
Issue Detection System
Simulated AI-based issue detection and delay prediction
"""

from django.utils import timezone
from datetime import timedelta
from bookings.models import Notification

def check_delays(shipment):
    """Check if shipment is delayed"""
    if not shipment.estimated_delivery_date:
        return None
    
    current_time = timezone.now()
    estimated_time = shipment.estimated_delivery_date
    
    # Check if delayed
    if current_time > estimated_time and shipment.status != 'delivered':
        delay_hours = (current_time - estimated_time).total_seconds() / 3600
        
        # Create delay notification if not already created
        existing_notification = Notification.objects.filter(
            shipment=shipment,
            notification_type='delay_alert'
        ).first()
        
        if not existing_notification:
            Notification.objects.create(
                user=shipment.user,
                shipment=shipment,
                notification_type='delay_alert',
                title='Delivery Delay Detected',
                message=f'Your shipment {shipment.shipment_id} is delayed by approximately {int(delay_hours)} hours. We apologize for the inconvenience.'
            )
        
        return {
            'is_delayed': True,
            'delay_hours': int(delay_hours),
            'estimated_delivery': estimated_time,
            'current_time': current_time,
        }
    
    # Check if approaching delay (within 2 hours of estimated time and not in transit)
    time_remaining = (estimated_time - current_time).total_seconds() / 3600
    if 0 < time_remaining <= 2 and shipment.status not in ['out_for_delivery', 'delivered']:
        return {
            'is_delayed': False,
            'is_at_risk': True,
            'hours_remaining': int(time_remaining),
            'estimated_delivery': estimated_time,
        }
    
    return {
        'is_delayed': False,
        'is_at_risk': False,
        'hours_remaining': int(time_remaining) if time_remaining > 0 else 0,
        'estimated_delivery': estimated_time,
    }


def detect_issues(shipment):
    """Detect potential issues with shipment"""
    issues = []
    
    # Check for long pending status
    if shipment.status == 'pending':
        pending_duration = (timezone.now() - shipment.created_at).total_seconds() / 3600
        if pending_duration > 24:
            issues.append({
                'type': 'pending_too_long',
                'severity': 'medium',
                'message': f'Shipment has been pending for {int(pending_duration)} hours. Please contact support.',
            })
    
    # Check for stuck in transit
    if shipment.status == 'in_transit' and shipment.in_transit_at:
        transit_duration = (timezone.now() - shipment.in_transit_at).total_seconds() / 3600
        if transit_duration > 72:  # 3 days
            issues.append({
                'type': 'stuck_in_transit',
                'severity': 'high',
                'message': f'Shipment has been in transit for {int(transit_duration)} hours. There may be a delay.',
            })
    
    # Check for payment issues
    if hasattr(shipment, 'payment'):
        if shipment.payment.payment_status == 'failed':
            issues.append({
                'type': 'payment_failed',
                'severity': 'high',
                'message': 'Payment failed. Please update payment method.',
            })
    
    # Check for missing tracking updates
    from bookings.models import TrackingLog
    tracking_logs = TrackingLog.objects.filter(shipment=shipment).order_by('-timestamp')
    if tracking_logs.exists():
        last_update = tracking_logs.first().timestamp
        hours_since_update = (timezone.now() - last_update).total_seconds() / 3600
        
        if hours_since_update > 12 and shipment.status not in ['delivered', 'cancelled']:
            issues.append({
                'type': 'no_recent_updates',
                'severity': 'low',
                'message': f'No tracking updates for {int(hours_since_update)} hours. Shipment may be in transit.',
            })
    
    return issues
