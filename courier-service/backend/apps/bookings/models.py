from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
import uuid


class Shipment(models.Model):
    """Shipment/Booking model"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    DELIVERY_TYPE_CHOICES = [
        ('normal', 'Normal'),
        ('express', 'Express'),
        ('eco', 'Eco'),
    ]
    
    tracking_id = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='shipments')
    
    # Sender details
    sender_name = models.CharField(max_length=100)
    sender_phone = models.CharField(max_length=15)
    sender_address = models.TextField()
    sender_city = models.CharField(max_length=100)
    sender_state = models.CharField(max_length=100)
    sender_postal_code = models.CharField(max_length=20)
    
    # Receiver details
    receiver_name = models.CharField(max_length=100)
    receiver_phone = models.CharField(max_length=15)
    receiver_address = models.TextField()
    receiver_city = models.CharField(max_length=100)
    receiver_state = models.CharField(max_length=100)
    receiver_postal_code = models.CharField(max_length=20)
    
    # Parcel details
    parcel_description = models.TextField()
    weight = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    dimensions_length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dimensions_width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dimensions_height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Delivery details
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPE_CHOICES, default='normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # in km
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_delivery_date = models.DateTimeField(null=True, blank=True)
    actual_delivery_date = models.DateTimeField(null=True, blank=True)
    
    # Agent assignment
    delivery_agent = models.ForeignKey('tracking.DeliveryAgent', on_delete=models.SET_NULL, null=True, blank=True, related_name='shipments')
    
    class Meta:
        db_table = 'shipments'
        verbose_name = 'Shipment'
        verbose_name_plural = 'Shipments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tracking_id} - {self.sender_name} to {self.receiver_name}"
    
    def save(self, *args, **kwargs):
        if not self.tracking_id:
            self.tracking_id = self.generate_tracking_id()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_tracking_id():
        """Generate a unique tracking ID"""
        return f"CS{uuid.uuid4().hex[:10].upper()}"


class PricingRule(models.Model):
    """Pricing rules for dynamic pricing calculation"""
    
    DELIVERY_TYPE_CHOICES = [
        ('normal', 'Normal'),
        ('express', 'Express'),
        ('eco', 'Eco'),
    ]
    
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPE_CHOICES, unique=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    distance_multiplier = models.DecimalField(max_digits=10, decimal_places=4, default=1.0)  # per km
    weight_multiplier = models.DecimalField(max_digits=10, decimal_places=4, default=1.0)  # per kg
    speed_multiplier = models.DecimalField(max_digits=10, decimal_places=4, default=1.0)  # urgency factor
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pricing_rules'
        verbose_name = 'Pricing Rule'
        verbose_name_plural = 'Pricing Rules'
    
    def __str__(self):
        return f"{self.get_delivery_type_display()} - Base: {self.base_price}"
