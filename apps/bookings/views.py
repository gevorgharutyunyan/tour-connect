from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from.models import Booking, Payment
from.forms import BookingForm, PaymentForm
from apps.tours.models import TourDate

@login_required
def create_booking(request, tour_date_id):
    tour_date = get_object_or_404(TourDate, pk=tour_date_id)
    if request.method == 'POST':
        booking_form = BookingForm(request.POST)
        payment_form = PaymentForm(request.POST)
        if booking_form.is_valid() and payment_form.is_valid():
            booking = booking_form.save(commit=False)
            booking.tourist = request.user
            booking.tour_date = tour_date
            booking.total_price = tour_date.tour.price * booking.number_of_participants  # Calculate total price
            booking.save()

            payment = payment_form.save(commit=False)
            payment.booking = booking
            payment.save()
            return redirect('bookings:booking_detail', booking.id)  # Redirect to booking detail page
    else:
        booking_form = BookingForm()
        payment_form = PaymentForm()
    return render(request, 'bookings/create_booking.html', {'booking_form': booking_form, 'payment_form': payment_form, 'tour_date': tour_date})

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})
