from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from shipments.models import Shipment
from .models import ParcelDetail, Notification
from .ai_logic import get_ai_recommendation, calculate_pricing, estimate_delivery_time

@login_required
def book_courier(request):
    """Main booking page - redirects to step 1"""
    return redirect('bookings:book_courier_step', step=1)


@login_required
def book_courier_step(request, step):
    """Step-based booking form"""
    if step < 1 or step > 4:
        messages.error(request, 'Invalid step.')
        return redirect('bookings:book_courier')
    
    context = {'current_step': step}
    
    if request.method == 'POST':
        # Store form data in session
        if 'booking_data' not in request.session:
            request.session['booking_data'] = {}
        
        if step == 1:  # Sender Details
            request.session['booking_data']['sender_name'] = request.POST.get('sender_name')
            request.session['booking_data']['sender_phone'] = request.POST.get('sender_phone')
            request.session['booking_data']['sender_address'] = request.POST.get('sender_address')
            request.session['booking_data']['sender_city'] = request.POST.get('sender_city')
            request.session['booking_data']['sender_state'] = request.POST.get('sender_state')
            request.session['booking_data']['sender_postal_code'] = request.POST.get('sender_postal_code')
            request.session['booking_data']['sender_country'] = request.POST.get('sender_country', 'USA')
            request.session.modified = True
            return redirect('bookings:book_courier_step', step=2)
        
        elif step == 2:  # Receiver Details
            request.session['booking_data']['receiver_name'] = request.POST.get('receiver_name')
            request.session['booking_data']['receiver_phone'] = request.POST.get('receiver_phone')
            request.session['booking_data']['receiver_address'] = request.POST.get('receiver_address')
            request.session['booking_data']['receiver_city'] = request.POST.get('receiver_city')
            request.session['booking_data']['receiver_state'] = request.POST.get('receiver_state')
            request.session['booking_data']['receiver_postal_code'] = request.POST.get('receiver_postal_code')
            request.session['booking_data']['receiver_country'] = request.POST.get('receiver_country', 'USA')
            request.session.modified = True
            return redirect('bookings:book_courier_step', step=3)
        
        elif step == 3:  # Parcel Details
            request.session['booking_data']['parcel_type'] = request.POST.get('parcel_type')
            request.session['booking_data']['weight_category'] = request.POST.get('weight_category')
            request.session['booking_data']['weight_kg'] = request.POST.get('weight_kg')
            request.session['booking_data']['dimensions_length'] = request.POST.get('dimensions_length', '')
            request.session['booking_data']['dimensions_width'] = request.POST.get('dimensions_width', '')
            request.session['booking_data']['dimensions_height'] = request.POST.get('dimensions_height', '')
            request.session['booking_data']['description'] = request.POST.get('description', '')
            request.session['booking_data']['fragile'] = request.POST.get('fragile') == 'on'
            request.session.modified = True
            return redirect('bookings:book_courier_step', step=4)
        
        elif step == 4:  # Review & Confirm
            delivery_option = request.POST.get('delivery_option')
            request.session['booking_data']['delivery_option'] = delivery_option
            request.session.modified = True
            return redirect('bookings:confirm_booking')
    
    # Pre-fill form if data exists in session
    if 'booking_data' in request.session:
        context.update(request.session['booking_data'])
    
    # For step 4, calculate pricing and AI recommendations
    if step == 4 and 'booking_data' in request.session:
        booking_data = request.session['booking_data']
        if all(k in booking_data for k in ['weight_kg', 'weight_category', 'sender_city', 'receiver_city']):
            # Calculate pricing for all options
            standard_price = calculate_pricing('standard', booking_data['weight_category'], booking_data['weight_kg'], booking_data.get('fragile', False))
            express_price = calculate_pricing('express', booking_data['weight_category'], booking_data['weight_kg'], booking_data.get('fragile', False))
            overnight_price = calculate_pricing('overnight', booking_data['weight_category'], booking_data['weight_kg'], booking_data.get('fragile', False))
            
            # Get AI recommendation
            ai_recommendation = get_ai_recommendation(
                booking_data['weight_category'],
                booking_data['weight_kg'],
                booking_data['sender_city'],
                booking_data['receiver_city'],
                booking_data.get('fragile', False)
            )
            
            context.update({
                'standard_price': standard_price,
                'express_price': express_price,
                'overnight_price': overnight_price,
                'ai_recommendation': ai_recommendation,
            })
    
    return render(request, f'bookings/step_{step}.html', context)


@login_required
def confirm_booking(request):
    """Confirm and create the booking"""
    if 'booking_data' not in request.session:
        messages.error(request, 'No booking data found. Please start over.')
        return redirect('bookings:book_courier')
    
    booking_data = request.session['booking_data']
    
    # Validate required fields
    required_fields = ['sender_name', 'receiver_name', 'parcel_type', 'weight_category', 'weight_kg', 'delivery_option']
    if not all(field in booking_data for field in required_fields):
        messages.error(request, 'Missing required information. Please complete all steps.')
        return redirect('bookings:book_courier')
    
    try:
        # Create parcel detail
        parcel = ParcelDetail.objects.create(
            sender_name=sender_name,
            sender_phone=sender_phone,
            sender_address=sender_address,
            receiver_name=receiver_name,
            receiver_phone=receiver_phone,
            receiver_address=receiver_address,
            weight=weight,
            #parcel_type=booking_data['parcel_type'],
            #weight_category=booking_data['weight_category'],
            #weight_kg=Decimal(booking_data['weight_kg']),
            #dimensions_length=Decimal(booking_data['dimensions_length']) if booking_data.get('dimensions_length') else None,
            #dimensions_width=Decimal(booking_data['dimensions_width']) if booking_data.get('dimensions_width') else None,
            #dimensions_height=Decimal(booking_data['dimensions_height']) if booking_data.get('dimensions_height') else None,
            #description=booking_data.get('description', ''),
            #fragile=booking_data.get('fragile', False)
        )
        
        #create shipment
        shipment = Shipment.objects.create(
            user=request.user,
            parcel=parcel,
            tracking_id=tracking_id,
            status='Booked',
            delivery_option=delivery_option,
            total_price=total_price,
        )
        
        
        # Calculate pricing
        base_price, additional_charges, total_price = calculate_pricing(
            booking_data['delivery_option'],
            booking_data['weight_category'],
            Decimal(booking_data['weight_kg']),
            booking_data.get('fragile', False),
            return_breakdown=True
        )
        
        # Get AI recommendation
        ai_recommendation = get_ai_recommendation(
            booking_data['weight_category'],
            Decimal(booking_data['weight_kg']),
            booking_data['sender_city'],
            booking_data['receiver_city'],
            booking_data.get('fragile', False)
        )
        
        # Estimate delivery time
        estimated_hours = estimate_delivery_time(
            booking_data['delivery_option'],
            booking_data['sender_city'],
            booking_data['receiver_city']
        )
        estimated_delivery = timezone.now() + timedelta(hours=estimated_hours)
        
        # Create shipment
        shipment = Shipment.objects.create(
            user=request.user,
            parcel=parcel,
            sender_name=booking_data['sender_name'],
            sender_phone=booking_data['sender_phone'],
            sender_address=booking_data['sender_address'],
            sender_city=booking_data['sender_city'],
            sender_state=booking_data['sender_state'],
            sender_postal_code=booking_data['sender_postal_code'],
            sender_country=booking_data.get('sender_country', 'USA'),
            receiver_name=booking_data['receiver_name'],
            receiver_phone=booking_data['receiver_phone'],
            receiver_address=booking_data['receiver_address'],
            receiver_city=booking_data['receiver_city'],
            receiver_state=booking_data['receiver_state'],
            receiver_postal_code=booking_data['receiver_postal_code'],
            receiver_country=booking_data.get('receiver_country', 'USA'),
            delivery_option=booking_data['delivery_option'],
            base_price=base_price,
            additional_charges=additional_charges,
            total_price=total_price,
            estimated_delivery_date=estimated_delivery,
            ai_recommended_option=ai_recommendation['option'],
            ai_eta_hours=ai_recommendation['eta_hours'],
            ai_reason=ai_recommendation['reason'],
            status='pending'
        )
        
        # Create notification
        Notification.objects.create(
            user=request.user,
            shipment=shipment,
            notification_type='booking_confirmed',
            title='Booking Confirmed',
            message=f'Your shipment {shipment.shipment_id} has been confirmed. Please proceed to payment.'
        )
        
        # Clear session data
        del request.session['booking_data']
        
        messages.success(request, f'Booking confirmed! Shipment ID: {shipment.shipment_id}')
        return redirect('payments:payment', shipment_id=shipment.shipment_id)
    
    except Exception as e:
        messages.error(request, f'Error creating booking: {str(e)}')
        return redirect('bookings:book_courier')


@login_required
def shipment_list(request):
    """List all user shipments"""
    shipments = Shipment.objects.all()
    return render(request, 'bookings/shipment_list.html', {'shipments': shipments})


@login_required
def shipment_detail(request, shipment_id):
    """View shipment details"""
    shipment = get_object_or_404(Shipment, shipment_id=shipment_id, user=request.user)
    return render(request, 'bookings/shipment_detail.html', {'shipment': shipment})
