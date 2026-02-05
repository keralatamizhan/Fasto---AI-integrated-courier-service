from decimal import Decimal

from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bookings.models import Shipment

from .models import TrackingStatus
from .serializers import TrackingStatusSerializer


class TrackingDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, tracking_id: str):
        shipment = Shipment.objects.filter(tracking_id=tracking_id).first()
        if not shipment:
            return Response({"detail": "Tracking ID not found."}, status=404)

        statuses = TrackingStatus.objects.filter(shipment=shipment).select_related("agent").order_by("-timestamp")
        return Response(
            {
                "tracking_id": shipment.tracking_id,
                "status": shipment.status,
                "shipment": {
                    "sender_city": shipment.sender_city,
                    "receiver_city": shipment.receiver_city,
                    "delivery_type": shipment.delivery_type,
                    "estimated_delivery_date": shipment.estimated_delivery_date,
                },
                "timeline": TrackingStatusSerializer(statuses, many=True).data,
            }
        )


class TrackingLiveView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, tracking_id: str):
        """
        Simulated live tracking:
        - Returns latest tracking status
        - If an agent exists, nudges the agent coordinates slightly to simulate movement
        """
        shipment = Shipment.objects.select_related("delivery_agent").filter(tracking_id=tracking_id).first()
        if not shipment:
            return Response({"detail": "Tracking ID not found."}, status=404)

        latest = (
            TrackingStatus.objects.filter(shipment=shipment)
            .select_related("agent")
            .order_by("-timestamp")
            .first()
        )

        agent = shipment.delivery_agent
        if agent and agent.current_location_lat is not None and agent.current_location_lng is not None:
            # Small deterministic nudge based on seconds to look "alive"
            seconds = timezone.now().second
            delta = Decimal("0.00010") if (seconds % 2 == 0) else Decimal("-0.00010")
            agent.current_location_lat = Decimal(agent.current_location_lat) + delta
            agent.current_location_lng = Decimal(agent.current_location_lng) + (-delta)
            agent.save(update_fields=["current_location_lat", "current_location_lng", "updated_at"])

        return Response(
            {
                "tracking_id": shipment.tracking_id,
                "status": shipment.status,
                "latest_update": TrackingStatusSerializer(latest).data if latest else None,
                "agent": {
                    "id": agent.id if agent else None,
                    "name": agent.name if agent else None,
                    "lat": float(agent.current_location_lat) if agent and agent.current_location_lat is not None else None,
                    "lng": float(agent.current_location_lng) if agent and agent.current_location_lng is not None else None,
                    "status": agent.status if agent else None,
                }
                if agent
                else None,
            }
        )

