from __future__ import annotations

from rest_framework import serializers


class PricingCalculateSerializer(serializers.Serializer):
    sender_city = serializers.CharField(max_length=100)
    receiver_city = serializers.CharField(max_length=100)
    weight = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    delivery_type = serializers.ChoiceField(choices=["normal", "express", "eco"], default="normal")
    urgency = serializers.ChoiceField(choices=["low", "medium", "high"], required=False, allow_null=True)
    waypoints = serializers.ListField(
        child=serializers.CharField(max_length=120),
        required=False,
        allow_empty=True,
        default=list,
    )

from rest_framework import serializers

from .models import PricingRule, Shipment


class ShipmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        exclude = ["id", "tracking_id", "user", "status", "created_at", "updated_at", "actual_delivery_date", "delivery_agent"]

    def create(self, validated_data):
        request = self.context["request"]
        return Shipment.objects.create(user=request.user, **validated_data)


class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = "__all__"
        read_only_fields = ["id", "tracking_id", "user", "created_at", "updated_at"]


class PricingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingRule
        fields = "__all__"

