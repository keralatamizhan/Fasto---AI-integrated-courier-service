from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('book/', views.book_courier, name='book_courier'),
    path('book/step/<int:step>/', views.book_courier_step, name='book_courier_step'),
    path('confirm/', views.confirm_booking, name='confirm_booking'),
    path('list/', views.shipment_list, name='shipment_list'),
    path('detail/<str:shipment_id>/', views.shipment_detail, name='shipment_detail'),
]
