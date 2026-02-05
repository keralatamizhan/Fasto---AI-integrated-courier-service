from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/pricing/", include("apps.bookings.pricing_urls")),
    path("api/bookings/", include("apps.bookings.urls")),
    path("api/tracking/", include("apps.tracking.urls")),
    path("api/payments/", include("apps.payments.urls")),
    path("api/admin/", include("apps.admin_dashboard.urls")),
]

from __future__ import annotations

from django.contrib import admin
from django.urls import path


urlpatterns = [
    path("admin/", admin.site.urls),
]

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]

