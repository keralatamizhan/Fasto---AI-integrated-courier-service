from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from bookings.models import Shipment, Notification
from .models import Payment

@login_required
def payment(request, shipment_id):
    """Payment page for a shipment"""
    shipment = get_object_or_404(Shipment, shipment_id=shipment_id, user=request.user)
    
    # Check if payment already exists
    if hasattr(shipment, 'payment') and shipment.payment.payment_status == 'completed':
        messages.info(request, 'Payment already completed for this shipment.')
        return redirect('tracking:track_shipment', shipment_id=shipment_id)
    
    context = {
        'shipment': shipment,
    }
    return render(request, 'payments/payment.html', context)


@login_required
def process_payment(request, shipment_id):
    """Process payment (simulated)"""
    shipment = get_object_or_404(Shipment, shipment_id=shipment_id, user=request.user)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        card_number = request.POST.get('card_number', '').replace(' ', '').replace('-', '')
        card_name = request.POST.get('card_name')
        card_expiry = request.POST.get('card_expiry')
        card_cvv = request.POST.get('card_cvv')
        
        # Validate payment details (simulated validation)
        if not all([payment_method, card_number, card_name, card_expiry, card_cvv]):
            messages.error(request, 'Please fill in all payment details.')
            return redirect('payments:payment', shipment_id=shipment_id)
        
        if len(card_number) < 13 or len(card_number) > 19:
            messages.error(request, 'Invalid card number.')
            return redirect('payments:payment', shipment_id=shipment_id)
        
        # Create payment record
        payment = Payment.objects.create(
            shipment=shipment,
            user=request.user,
            amount=shipment.total_price,
            payment_method=payment_method,
            payment_status='processing',
            card_last_four=card_number[-4:] if len(card_number) >= 4 else '',
        )
        
        # Simulate payment processing delay
        import time
        time.sleep(1)  # Simulate processing
        
        # Update payment status (simulated - always succeeds)
        payment.payment_status = 'completed'
        payment.processed_at = timezone.now()
        payment.completed_at = timezone.now()
        payment.transaction_id = f"TXN{payment.payment_id}"
        payment.save()
        
        # Update shipment status
        shipment.status = 'confirmed'
        shipment.save()
        
        # Create notifications
        Notification.objects.create(
            user=request.user,
            shipment=shipment,
            notification_type='payment_received',
            title='Payment Received',
            message=f'Payment of ${shipment.total_price} received for shipment {shipment.shipment_id}.'
        )
        
        Notification.objects.create(
            user=request.user,
            shipment=shipment,
            notification_type='booking_confirmed',
            title='Shipment Confirmed',
            message=f'Your shipment {shipment.shipment_id} has been confirmed and will be picked up soon.'
        )
        
        messages.success(request, 'Payment processed successfully!')
        return redirect('payments:payment_success', payment_id=payment.payment_id)
    
    return redirect('payments:payment', shipment_id=shipment_id)


@login_required
def payment_success(request, payment_id):
    """Payment success page"""
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user)
    context = {
        'payment': payment,
        'shipment': payment.shipment,
    }
    return render(request, 'payments/payment_success.html', context)
