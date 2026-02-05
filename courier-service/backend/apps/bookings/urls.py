from django.urls import path

from .views import BookingDetailView, BookingListCreateView, UserStatsView


urlpatterns = [
    path("create/", BookingListCreateView.as_view(), name="booking-create"),
    path("list/", BookingListCreateView.as_view(), name="booking-list"),
    path("<int:booking_id>/", BookingDetailView.as_view(), name="booking-detail"),
    path("me/stats/", UserStatsView.as_view(), name="booking-user-stats"),
]

from django.urls import path

from . import views


urlpatterns = [
    path("create/", views.ShipmentCreateView.as_view(), name="booking-create"),
    path("list/", views.ShipmentListView.as_view(), name="booking-list"),
    path("<int:id>/", views.ShipmentDetailView.as_view(), name="booking-detail"),
]

