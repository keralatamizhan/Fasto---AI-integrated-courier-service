from django.contrib import admin
from .models import Shipment, ParcelDetail, TrackingLog, Notification

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['shipment_id', 'user', 'status', 'delivery_option', 'total_price', 'created_at']
    list_filter = ['status', 'delivery_option', 'created_at']
    search_fields = ['shipment_id', 'user__username', 'sender_name', 'receiver_name']

@admin.register(ParcelDetail)
class ParcelDetailAdmin(admin.ModelAdmin):
    #list_display = ['parcel_type', 'weight_category', 'weight_kg', 'fragile', 'created_at']
    list_display = ['id', 'sender_name', 'receiver_name', 'weight', 'fragile', 'created_at']

@admin.register(TrackingLog)
class TrackingLogAdmin(admin.ModelAdmin):
    list_display = ['shipment', 'location_name', 'status', 'timestamp']
    list_filter = ['status', 'timestamp']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
