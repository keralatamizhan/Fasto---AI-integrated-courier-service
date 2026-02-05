from django.urls import path
from . import views

app_name = 'tracking'

urlpatterns = [
    path('track/<str:shipment_id>/', views.track_shipment, name='track_shipment'),
    path('update-location/<str:shipment_id>/', views.update_location, name='update_location'),
]
