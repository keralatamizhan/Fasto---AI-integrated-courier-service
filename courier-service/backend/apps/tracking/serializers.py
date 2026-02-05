from rest_framework import serializers

from .models import DeliveryAgent, TrackingStatus


class DeliveryAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAgent
        fields = "__all__"


class TrackingStatusSerializer(serializers.ModelSerializer):
    agent = DeliveryAgentSerializer(read_only=True)

    class Meta:
        model = TrackingStatus
        fields = "__all__"

