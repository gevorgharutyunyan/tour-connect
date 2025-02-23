from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from.models import Booking, Payment
from.forms import BookingForm, PaymentForm
from apps.tours.models import TourDate, Tour
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

@login_required
def create_booking(request, tour_date_id):
    tour_date = get_object_or_404(TourDate, pk=tour_date_id)
    tour = Tour.objects.get(pk=tour_date.tour_id)
    if request.method == 'POST':
        booking_form = BookingForm(request.POST)
        payment_form = PaymentForm(request.POST)
        if booking_form.is_valid() and payment_form.is_valid():
            if tour.is_active:
                booking = booking_form.save(commit=False)
                booking.tourist = request.user
                booking.tour_date = tour_date
                booking.total_price = tour_date.tour.price * booking.number_of_participants  # Calculate total price
                print("Tour Date:", booking.tour_date)
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
    print(booking.tour_date)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})


@login_required
def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    booking.status = 'confirmed'
    booking.save()
    return redirect('accounts:guide_dashboard')  # Redirect back to the guide dashboard

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    booking.status = 'cancelled'
    booking.save()
    return redirect('accounts:guide_dashboard')

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return Booking.objects.filter(tourist=self.request.user)
