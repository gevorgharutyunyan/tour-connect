from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from.models import Booking, Payment
from.forms import BookingForm, PaymentForm
from apps.tours.models import TourDate, Tour
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required, user_passes_test
from apps.messaging.utils import create_booking_notification
from django.contrib import messages

@login_required
def create_booking(request, tour_date_id):
    tour_date = get_object_or_404(TourDate, pk=tour_date_id)
    tour = Tour.objects.get(pk=tour_date.tour_id)
    if request.method == 'POST':
        booking_form = BookingForm(request.POST)
        payment_form = PaymentForm(request.POST)
        if booking_form.is_valid() and payment_form.is_valid():
            if tour.is_available:
                # Validate number of participants against available spots
                num_participants = booking_form.cleaned_data['number_of_participants']
                if num_participants > tour_date.available_spots:
                    messages.error(request, f"Sorry, only {tour_date.available_spots} spots are available.")
                    return render(request, 'bookings/create_booking.html', {
                        'booking_form': booking_form,
                        'payment_form': payment_form,
                        'tour_date': tour_date
                    })

                booking = booking_form.save(commit=False)
                booking.tourist = request.user
                booking.tour_date = tour_date
                booking.total_price = tour_date.tour.price * booking.number_of_participants
                booking.save()

                # Update booked spots
                tour_date.booked_spots += num_participants
                tour_date.save()

                payment = payment_form.save(commit=False)
                payment.booking = booking
                payment.save()

                # Create notification for the guide
                create_booking_notification(booking)

                messages.success(request, "Booking created successfully!")
                return redirect('bookings:booking_detail', booking.id)
            else:
                messages.error(request, "Sorry, this tour is no longer available.")
    else:
        booking_form = BookingForm()
        payment_form = PaymentForm()
    return render(request, 'bookings/create_booking.html', {
        'booking_form': booking_form,
        'payment_form': payment_form,
        'tour_date': tour_date
    })

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
    
    # Create notification for the tourist
    create_booking_notification(booking)
    
    return redirect('accounts:guide_dashboard')  # Redirect back to the guide dashboard

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    booking.status = 'cancelled'
    booking.save()
    
    # Create notification for the tourist
    create_booking_notification(booking)
    
    return redirect('accounts:guide_dashboard')

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return Booking.objects.filter(tourist=self.request.user)

def is_guide(user):
    return user.is_authenticated and user.user_type == 'guide'

@login_required
@user_passes_test(is_guide)
def booking_requests(request):
    booking_requests = Booking.objects.filter(
        tour_date__tour__guide=request.user
    ).select_related(
        'tourist',
        'tour_date__tour'
    ).order_by('-booking_date')

    return render(request, 'bookings/booking_requests.html', {
        'booking_requests': booking_requests
    })

@login_required
@user_passes_test(is_guide)
def complete_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    
    # Verify that the guide owns this tour
    if booking.tour_date.tour.guide != request.user:
        messages.error(request, "You don't have permission to complete this booking.")
        return redirect('accounts:guide_dashboard')
    
    # Only confirmed bookings can be completed
    if booking.status != 'confirmed':
        messages.error(request, "Only confirmed bookings can be marked as completed.")
        return redirect('accounts:guide_dashboard')
    
    booking.status = 'completed'
    booking.save()
    
    # Create notification for the tourist
    create_booking_notification(booking)
    
    messages.success(request, f"Tour marked as completed. The tourist can now leave a review.")
    return redirect('accounts:guide_dashboard')
