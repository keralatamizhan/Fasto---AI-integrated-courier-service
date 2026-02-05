from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class ParcelDetail(models.Model):
    """Parcel details for shipments"""
    WEIGHT_CHOICES = [
        ('light', 'Light (< 1kg)'),
        ('medium', 'Medium (1-5kg)'),
        ('heavy', 'Heavy (5-10kg)'),
        ('extra_heavy', 'Extra Heavy (> 10kg)'),
    ]
    sender_name=models.CharField(max_length=100)
    receiver_name = models.CharField(max_length=100)
    weight = models.FloatField()
    fragile=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender_name} -> {self.receiver_name}"

class Shipment(models.Model):
    """Main shipment model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    DELIVERY_OPTIONS = [
        ('standard', 'Standard (3-5 days)'),
        ('express', 'Express (1-2 days)'),
        ('overnight', 'Overnight (24 hours)'),
    ]
    
    shipment_id = models.CharField(max_length=20, unique=True, editable=False)
    from django.conf import settings
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shipments')
    parcel = models.OneToOneField(ParcelDetail, on_delete=models.CASCADE, related_name='shipment')
    
    # Sender details
    sender_name = models.CharField(max_length=200)
    sender_phone = models.CharField(max_length=20)
    sender_address = models.TextField()
    sender_city = models.CharField(max_length=100)
    sender_state = models.CharField(max_length=100)
    sender_postal_code = models.CharField(max_length=20)
    sender_country = models.CharField(max_length=100, default='USA')
    
    # Receiver details
    receiver_name = models.CharField(max_length=200)
    receiver_phone = models.CharField(max_length=20)
    receiver_address = models.TextField()
    receiver_city = models.CharField(max_length=100)
    receiver_state = models.CharField(max_length=100)
    receiver_postal_code = models.CharField(max_length=20)
    receiver_country = models.CharField(max_length=100, default='USA')
    
    # Delivery details
    delivery_option = models.CharField(max_length=20, choices=DELIVERY_OPTIONS, default='standard')
    estimated_delivery_date = models.DateTimeField(null=True, blank=True)
    actual_delivery_date = models.DateTimeField(null=True, blank=True)
    
    # Status and pricing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    additional_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # AI recommendations
    ai_recommended_option = models.CharField(max_length=20, choices=DELIVERY_OPTIONS, null=True, blank=True)
    ai_eta_hours = models.IntegerField(null=True, blank=True)
    ai_reason = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    in_transit_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'shipments'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.shipment_id:
            self.shipment_id = self.generate_shipment_id()
        super().save(*args, **kwargs)

    def generate_shipment_id(self):
        """Generate unique shipment ID"""
        return f"SH{str(uuid.uuid4())[:8].upper()}"

    def __str__(self):
        return f"{self.shipment_id} - {self.user.username}"


class TrackingLog(models.Model):
    """Tracking logs for shipment movement"""
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='tracking_logs')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    location_name = models.CharField(max_length=200)
    status = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tracking_logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.shipment.shipment_id} - {self.location_name}"


class Notification(models.Model):
    """Notifications for users"""
    NOTIFICATION_TYPES = [
        ('booking_confirmed', 'Booking Confirmed'),
        ('payment_received', 'Payment Received'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('delay_alert', 'Delay Alert'),
        ('issue_detected', 'Issue Detected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"
