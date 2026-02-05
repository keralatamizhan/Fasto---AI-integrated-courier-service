from django.db import models
from django.contrib.auth import get_user_model
from bookings.models import Shipment

User = get_user_model()

class Payment(models.Model):
    """Payment model for shipments"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    payment_id = models.CharField(max_length=50, unique=True, editable=False)
    shipment = models.OneToOneField(Shipment, on_delete=models.CASCADE, related_name='payment')
    from django.conf import settings
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Payment details (simulated - no real payment processing)
    card_last_four = models.CharField(max_length=4, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = self.generate_payment_id()
        super().save(*args, **kwargs)

    def generate_payment_id(self):
        """Generate unique payment ID"""
        import uuid
        return f"PAY{str(uuid.uuid4())[:8].upper()}"

    def __str__(self):
        return f"{self.payment_id} - {self.shipment.shipment_id} - ${self.amount}"
