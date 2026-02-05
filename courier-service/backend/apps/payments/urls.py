from django.urls import path

from . import views


urlpatterns = [
    path("create/", views.PaymentCreateView.as_view(), name="payment-create"),
    path("verify/", views.PaymentVerifyView.as_view(), name="payment-verify"),
]

