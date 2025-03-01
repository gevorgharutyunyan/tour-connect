from django.shortcuts import render, redirect
from apps.tours.models import Tour  # Import your Tour model
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from apps.bookings.models import Booking
from apps.reviews.models import Wishlist
from django.utils import timezone
from datetime import timedelta

def home(request):
    # Get featured tours (most recent tours with upcoming dates)
    featured_tours = Tour.objects.filter(
        dates__start_date__gte=timezone.now()
    ).distinct().order_by('-created_at')[:6]  # Limit to 6 tours
    
    return render(request, 'core/home.html', {
        'tours': featured_tours,
    })

@login_required
def add_to_wishlist(request, tour_id):
    return redirect('home')