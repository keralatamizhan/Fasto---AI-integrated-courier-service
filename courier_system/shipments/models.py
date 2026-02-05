from django.db import models
from bookings.models import ParcelDetail
from django.conf import settings


class Shipment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    parcel = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    tracking_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50)
    delivery_option = models.CharField(max_length=50)
    estimated_delivary_date = models.DateField(null=True,blank=True)
    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    
    def __str__(self):
        return self.tracking_id
     
class Notification(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    message=models.CharField(max_length=255)
    is_read=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.message