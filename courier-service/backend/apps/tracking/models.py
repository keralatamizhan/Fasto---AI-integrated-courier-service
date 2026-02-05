from django.db import models
from django.utils import timezone


class DeliveryAgent(models.Model):
    """Delivery agent model"""
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('offline', 'Offline'),
    ]
    
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    current_location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    vehicle_type = models.CharField(max_length=50, blank=True, null=True)
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'delivery_agents'
        verbose_name = 'Delivery Agent'
        verbose_name_plural = 'Delivery Agents'
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"


class TrackingStatus(models.Model):
    """Tracking status history for shipments"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('delayed', 'Delayed'),
        ('exception', 'Exception'),
    ]
    
    shipment = models.ForeignKey('bookings.Shipment', on_delete=models.CASCADE, related_name='tracking_statuses')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    location = models.CharField(max_length=200, blank=True, null=True)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    agent = models.ForeignKey('DeliveryAgent', on_delete=models.SET_NULL, null=True, blank=True, related_name='tracking_updates')
    notes = models.TextField(blank=True, null=True)
    is_issue_detected = models.BooleanField(default=False)
    issue_description = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'tracking_statuses'
        verbose_name = 'Tracking Status'
        verbose_name_plural = 'Tracking Statuses'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.shipment.tracking_id} - {self.get_status_display()} at {self.timestamp}"
