from django.db import models
from django.utils import timezone


class Payment(models.Model):
    """Payment model for shipment payments"""
    
    PAYMENT_METHOD_CHOICES = [
        ('online', 'Online Payment'),
        ('cash_on_delivery', 'Cash on Delivery'),
        ('card', 'Card Payment'),
        ('wallet', 'Wallet'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    shipment = models.OneToOneField('bookings.Shipment', on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True, db_index=True)
    payment_gateway = models.CharField(max_length=50, blank=True, null=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    failure_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment for {self.shipment.tracking_id} - {self.amount} ({self.get_status_display()})"
    
    def mark_as_completed(self, transaction_id=None):
        """Mark payment as completed"""
        self.status = 'completed'
        self.payment_date = timezone.now()
        if transaction_id:
            self.transaction_id = transaction_id
        self.save()
    
    def mark_as_failed(self, reason=None):
        """Mark payment as failed"""
        self.status = 'failed'
        if reason:
            self.failure_reason = reason
        self.save()
