from __future__ import annotations

from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .ai import detect_issues, estimate_delivery_datetime, estimate_distance_km, optimize_route, recommend_service
from .models import PricingRule, Shipment
from .serializers import PricingCalculateSerializer


class PricingCalculateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = PricingCalculateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.validated_data

        sender_city = data["sender_city"]
        receiver_city = data["receiver_city"]
        weight = Decimal(str(data["weight"]))
        delivery_type = data["delivery_type"]
        urgency = data.get("urgency") or "medium"
        waypoints = data.get("waypoints") or []

        distance_km = Decimal(str(estimate_distance_km(sender_city, receiver_city)))

        rule = PricingRule.objects.filter(delivery_type=delivery_type, is_active=True).first()
        if not rule:
            # Defaults if DB not seeded yet
            defaults = {
                "normal": dict(base=Decimal("50.00"), dist=Decimal("1.20"), weight=Decimal("8.00"), speed=Decimal("1.00")),
                "express": dict(base=Decimal("80.00"), dist=Decimal("1.60"), weight=Decimal("10.50"), speed=Decimal("1.35")),
                "eco": dict(base=Decimal("35.00"), dist=Decimal("1.00"), weight=Decimal("7.00"), speed=Decimal("0.90")),
            }[delivery_type]
            base_price = defaults["base"]
            distance_multiplier = defaults["dist"]
            weight_multiplier = defaults["weight"]
            speed_multiplier = defaults["speed"]
        else:
            base_price = rule.base_price
            distance_multiplier = rule.distance_multiplier
            weight_multiplier = rule.weight_multiplier
            speed_multiplier = rule.speed_multiplier

        # Simulated demand multiplier: busier during business hours
        hour = timezone.localtime().hour
        demand_multiplier = Decimal("1.00")
        if 9 <= hour <= 11 or 16 <= hour <= 19:
            demand_multiplier = Decimal("1.10")
        elif 0 <= hour <= 6:
            demand_multiplier = Decimal("0.95")

        price = (base_price + (distance_km * distance_multiplier) + (weight * weight_multiplier)) * speed_multiplier * demand_multiplier
        price = price.quantize(Decimal("0.01"))

        rec = recommend_service(float(distance_km), float(weight), urgency=urgency)
        route = optimize_route(sender_city, receiver_city, waypoints=waypoints)
        eta_dt = estimate_delivery_datetime(float(distance_km), delivery_type)
        issue = detect_issues("pending", float(distance_km), delivery_type, created_at=timezone.now())

        return Response(
            {
                "distance_km": float(distance_km),
                "price": float(price),
                "currency": "USD",
                "delivery_type": delivery_type,
                "recommendation": {
                    "recommended_delivery_type": rec.recommended_delivery_type,
                    "confidence": rec.confidence,
                    "reasons": rec.reasons,
                },
                "route": route,
                "eta": eta_dt.isoformat(),
                "issue_detection": issue,
            }
        )


class BookingListCreateView(APIView):
    """
    Minimal booking endpoints used by the frontend.
    """

    def get(self, request):
        qs = Shipment.objects.filter(user=request.user).order_by("-created_at")
        return Response(
            [
                {
                    "id": sh.id,
                    "tracking_id": sh.tracking_id,
                    "status": sh.status,
                    "delivery_type": sh.delivery_type,
                    "price": float(sh.price),
                    "distance_km": float(sh.distance or 0),
                    "created_at": sh.created_at.isoformat(),
                }
                for sh in qs
            ]
        )

    def post(self, request):
        payload = request.data or {}
        required = [
            "sender_name",
            "sender_phone",
            "sender_address",
            "sender_city",
            "sender_state",
            "sender_postal_code",
            "receiver_name",
            "receiver_phone",
            "receiver_address",
            "receiver_city",
            "receiver_state",
            "receiver_postal_code",
            "parcel_description",
            "weight",
            "delivery_type",
        ]
        missing = [k for k in required if k not in payload or payload.get(k) in (None, "")]
        if missing:
            return Response({"detail": f"Missing fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

        sender_city = payload["sender_city"]
        receiver_city = payload["receiver_city"]
        weight = Decimal(str(payload["weight"]))
        delivery_type = payload.get("delivery_type") or "normal"

        distance_km = Decimal(str(estimate_distance_km(sender_city, receiver_city)))

        # Reuse pricing engine
        rule = PricingRule.objects.filter(delivery_type=delivery_type, is_active=True).first()
        if not rule:
            defaults = {
                "normal": dict(base=Decimal("50.00"), dist=Decimal("1.20"), weight=Decimal("8.00"), speed=Decimal("1.00")),
                "express": dict(base=Decimal("80.00"), dist=Decimal("1.60"), weight=Decimal("10.50"), speed=Decimal("1.35")),
                "eco": dict(base=Decimal("35.00"), dist=Decimal("1.00"), weight=Decimal("7.00"), speed=Decimal("0.90")),
            }[delivery_type]
            base_price = defaults["base"]
            distance_multiplier = defaults["dist"]
            weight_multiplier = defaults["weight"]
            speed_multiplier = defaults["speed"]
        else:
            base_price = rule.base_price
            distance_multiplier = rule.distance_multiplier
            weight_multiplier = rule.weight_multiplier
            speed_multiplier = rule.speed_multiplier

        price = (base_price + (distance_km * distance_multiplier) + (weight * weight_multiplier)) * speed_multiplier
        price = price.quantize(Decimal("0.01"))

        sh = Shipment.objects.create(
            user=request.user,
            sender_name=payload["sender_name"],
            sender_phone=payload["sender_phone"],
            sender_address=payload["sender_address"],
            sender_city=sender_city,
            sender_state=payload["sender_state"],
            sender_postal_code=payload["sender_postal_code"],
            receiver_name=payload["receiver_name"],
            receiver_phone=payload["receiver_phone"],
            receiver_address=payload["receiver_address"],
            receiver_city=receiver_city,
            receiver_state=payload["receiver_state"],
            receiver_postal_code=payload["receiver_postal_code"],
            parcel_description=payload["parcel_description"],
            weight=weight,
            delivery_type=delivery_type,
            price=price,
            distance=distance_km,
            estimated_delivery_date=estimate_delivery_datetime(float(distance_km), delivery_type),
            status="pending",
        )

        return Response(
            {
                "id": sh.id,
                "tracking_id": sh.tracking_id,
                "status": sh.status,
                "price": float(sh.price),
                "distance_km": float(distance_km),
                "estimated_delivery_date": sh.estimated_delivery_date.isoformat() if sh.estimated_delivery_date else None,
            },
            status=status.HTTP_201_CREATED,
        )


class BookingDetailView(APIView):
    def get(self, request, booking_id: int):
        sh = Shipment.objects.filter(id=booking_id, user=request.user).first()
        if not sh:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {
                "id": sh.id,
                "tracking_id": sh.tracking_id,
                "status": sh.status,
                "delivery_type": sh.delivery_type,
                "price": float(sh.price),
                "distance_km": float(sh.distance or 0),
                "sender_city": sh.sender_city,
                "receiver_city": sh.receiver_city,
                "created_at": sh.created_at.isoformat(),
            }
        )


class UserStatsView(APIView):
    def get(self, request):
        totals = Shipment.objects.filter(user=request.user).aggregate(
            total_spent=Sum("price"),
        )
        return Response(
            {
                "shipments_count": Shipment.objects.filter(user=request.user).count(),
                "total_spent": float(totals["total_spent"] or 0),
            }
        )

from decimal import Decimal

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PricingRule, Shipment
from .serializers import ShipmentCreateSerializer, ShipmentSerializer


class ShipmentCreateView(generics.CreateAPIView):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentCreateSerializer


class ShipmentListView(generics.ListAPIView):
    serializer_class = ShipmentSerializer

    def get_queryset(self):
        return Shipment.objects.filter(user=self.request.user).select_related("delivery_agent")


class ShipmentDetailView(generics.RetrieveAPIView):
    serializer_class = ShipmentSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Shipment.objects.filter(user=self.request.user).select_related("delivery_agent")


class PricingCalculateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Calculate a dynamic price based on distance, weight and delivery type.
        Body: {distance: km, weight: kg, delivery_type: normal|express|eco, demand: 0..1 (optional)}
        """
        try:
            distance = Decimal(str(request.data.get("distance", "0")))
            weight = Decimal(str(request.data.get("weight", "0")))
        except Exception:
            return Response({"detail": "distance and weight must be numeric."}, status=status.HTTP_400_BAD_REQUEST)

        delivery_type = (request.data.get("delivery_type") or "normal").lower()
        demand = request.data.get("demand", 0)
        try:
            demand = Decimal(str(demand))
        except Exception:
            demand = Decimal("0")

        if distance <= 0 or weight <= 0:
            return Response({"detail": "distance and weight must be > 0."}, status=status.HTTP_400_BAD_REQUEST)

        rule = PricingRule.objects.filter(delivery_type=delivery_type, is_active=True).first()
        if not rule:
            # Sensible defaults if rules not seeded yet
            defaults = {
                "normal": dict(base=Decimal("5.00"), dist=Decimal("0.8"), wt=Decimal("1.2"), speed=Decimal("1.0")),
                "express": dict(base=Decimal("8.00"), dist=Decimal("1.2"), wt=Decimal("1.5"), speed=Decimal("1.5")),
                "eco": dict(base=Decimal("4.00"), dist=Decimal("0.6"), wt=Decimal("1.0"), speed=Decimal("0.9")),
            }.get(delivery_type, dict(base=Decimal("5.00"), dist=Decimal("0.8"), wt=Decimal("1.2"), speed=Decimal("1.0")))
            base_price = defaults["base"]
            distance_multiplier = defaults["dist"]
            weight_multiplier = defaults["wt"]
            speed_multiplier = defaults["speed"]
        else:
            base_price = rule.base_price
            distance_multiplier = rule.distance_multiplier
            weight_multiplier = rule.weight_multiplier
            speed_multiplier = rule.speed_multiplier

        # Demand multiplier: 0..1 -> 1.0..1.25
        demand = max(Decimal("0"), min(Decimal("1"), demand))
        demand_multiplier = Decimal("1.0") + (demand * Decimal("0.25"))

        price = (base_price + (distance * distance_multiplier) + (weight * weight_multiplier)) * speed_multiplier * demand_multiplier
        price = price.quantize(Decimal("0.01"))

        return Response(
            {
                "delivery_type": delivery_type,
                "distance": float(distance),
                "weight": float(weight),
                "demand": float(demand),
                "price": float(price),
            }
        )

