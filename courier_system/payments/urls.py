from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('payment/<str:shipment_id>/', views.payment, name='payment'),
    path('process/<str:shipment_id>/', views.process_payment, name='process_payment'),
    path('success/<str:payment_id>/', views.payment_success, name='payment_success'),
]
