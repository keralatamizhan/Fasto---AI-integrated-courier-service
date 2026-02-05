import uuid
from decimal import Decimal

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bookings.models import Shipment

from .models import Payment
from .serializers import PaymentCreateSerializer, PaymentSerializer


class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shipment: Shipment = serializer.validated_data["shipment"]
        if shipment.user_id != request.user.id:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        amount = serializer.validated_data.get("amount")
        if amount is None:
            amount = shipment.price
        try:
            amount = Decimal(str(amount))
        except Exception:
            return Response({"detail": "amount must be numeric."}, status=status.HTTP_400_BAD_REQUEST)

        payment, created = Payment.objects.get_or_create(
            shipment=shipment,
            defaults={
                "amount": amount,
                "method": serializer.validated_data["method"],
                "payment_gateway": serializer.validated_data.get("payment_gateway"),
                "status": "pending",
            },
        )
        if not created:
            # Update existing pending payment
            payment.amount = amount
            payment.method = serializer.validated_data["method"]
            payment.payment_gateway = serializer.validated_data.get("payment_gateway")
            payment.status = "pending"
            payment.save()

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentVerifyView(APIView):
    """
    Simulated verify endpoint.
    Body: {shipment: <shipment_id> OR transaction_id: "...", success: true|false (optional)}
    """

    def post(self, request):
        shipment_id = request.data.get("shipment")
        transaction_id = request.data.get("transaction_id")
        success = request.data.get("success", True)

        if shipment_id:
            payment = Payment.objects.select_related("shipment").filter(shipment_id=shipment_id).first()
        elif transaction_id:
            payment = Payment.objects.select_related("shipment").filter(transaction_id=transaction_id).first()
        else:
            return Response({"detail": "Provide shipment or transaction_id."}, status=status.HTTP_400_BAD_REQUEST)

        if not payment or payment.shipment.user_id != request.user.id:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if bool(success):
            if not payment.transaction_id:
                payment.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
            payment.status = "completed"
            payment.payment_date = timezone.now()
            payment.save(update_fields=["transaction_id", "status", "payment_date", "updated_at"])
        else:
            payment.status = "failed"
            payment.failure_reason = request.data.get("reason") or "Payment verification failed."
            payment.save(update_fields=["status", "failure_reason", "updated_at"])

        return Response(PaymentSerializer(payment).data)

