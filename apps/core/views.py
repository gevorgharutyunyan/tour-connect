from django.shortcuts import render, redirect
from apps.tours.models import Tour  # Import your Tour model
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from apps.bookings.models import Booking

def home(request):
    tours = Tour.objects.filter(is_active=True)
    bookings =  []
    if request.user.is_authenticated:
        bookings = Booking.objects.filter(tourist=request.user)
    return render(request,
                  'core/home.html',
                  {'tours': tours,
                   'bookings': bookings})

@login_required
def add_to_wishlist(request, tour_id):
    return redirect('home')