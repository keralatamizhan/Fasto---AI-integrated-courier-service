from django.urls import path

from . import views


urlpatterns = [
    path("<str:tracking_id>/", views.TrackingDetailView.as_view(), name="tracking-detail"),
    path("live/<str:tracking_id>/", views.TrackingLiveView.as_view(), name="tracking-live"),
]

