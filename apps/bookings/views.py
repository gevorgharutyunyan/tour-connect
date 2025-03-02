from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Booking
from .forms import BookingForm
from apps.tours.models import TourDate
from apps.payments.forms import PaymentForm
from django.contrib import messages
from django.utils import timezone

@login_required
def create_booking(request, tour_date_id):
    tour_date = get_object_or_404(TourDate, id=tour_date_id)
    
    if request.method == 'POST':
        booking_form = BookingForm(request.POST)
        payment_form = PaymentForm(request.POST)
        if booking_form.is_valid() and payment_form.is_valid():
            number_of_participants = booking_form.cleaned_data['number_of_participants']
            
            # Check if there are enough spots available
            if tour_date.available_spots < number_of_participants:
                messages.error(request, 'Not enough spots available for this tour.')
                return redirect('tours:tour-detail', pk=tour_date.tour.id)
            
            # Calculate total price
            total_price = tour_date.tour.price * number_of_participants
            
            # Create booking
            booking = booking_form.save(commit=False)
            booking.tourist = request.user
            booking.tour_date = tour_date
            booking.total_price = total_price
            booking.save()
            
            # Update available spots
            tour_date.booked_spots += number_of_participants
            tour_date.save()
            
            # Store payment method in session for payment page
            request.session['payment_method_id'] = payment_form.cleaned_data['payment_method'].id
            
            # Redirect to payment
            return redirect('payments:payment_page', booking_id=booking.id)
    else:
        booking_form = BookingForm()
        payment_form = PaymentForm()
    
    context = {
        'tour_date': tour_date,
        'booking_form': booking_form,
        'payment_form': payment_form,
        'min_participants': 1,
        'max_participants': min(tour_date.available_spots, 10)  # Limit to 10 or available spots
    }
    return render(request, 'bookings/create_booking.html', context)

@login_required
def booking_list(request):
    if request.user.user_type == 'guide':
        # For guides, show bookings for their tours
        bookings = Booking.objects.filter(
            tour_date__tour__guide=request.user
        ).select_related('tourist', 'tour_date', 'tour_date__tour').order_by('-created_at')
    else:
        # For tourists, show their bookings
        bookings = Booking.objects.filter(
            tourist=request.user
        ).select_related('tour_date', 'tour_date__tour').order_by('-created_at')
    
    return render(request, 'bookings/booking_list.html', {'bookings': bookings})

@login_required
def booking_detail(request, booking_id):
    if request.user.user_type == 'guide':
        booking = get_object_or_404(Booking, id=booking_id, tour_date__tour__guide=request.user)
    else:
        booking = get_object_or_404(Booking, id=booking_id, tourist=request.user)
    
    return render(request, 'bookings/booking_detail.html', {'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    # Get the booking
    if request.user.user_type == 'guide':
        booking = get_object_or_404(Booking, id=booking_id, tour_date__tour__guide=request.user)
    else:
        booking = get_object_or_404(Booking, id=booking_id, tourist=request.user)
    
    if request.method == 'POST':
        # Check if the booking can be cancelled
        if booking.can_be_cancelled():
            # Update tour date available spots
            tour_date = booking.tour_date
            tour_date.booked_spots -= booking.number_of_participants
            tour_date.save()
            
            # Update booking status
            booking.status = 'cancelled'
            booking.cancelled_at = timezone.now()
            booking.save()
            
            messages.success(request, 'Booking cancelled successfully.')
            return redirect('bookings:booking_list')
        else:
            messages.error(request, 'This booking cannot be cancelled.')
    
    return render(request, 'bookings/cancel_booking.html', {'booking': booking})
