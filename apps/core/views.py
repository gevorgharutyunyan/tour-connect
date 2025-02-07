from django.shortcuts import render, redirect
from apps.tours.models import Tour  # Import your Tour model
from django.contrib.auth.decorators import login_required
from django.urls import reverse

def home(request):
    tours = Tour.objects.filter(is_active=True)  # Get active tours (you might want to add ordering or filtering)
    return render(request, 'core/home.html', {'tours': tours})

@login_required  # Example wishlist view
def add_to_wishlist(request, tour_id):
    # Add logic here to add tour_id to user's wishlist
    # Example: request.user.wishlist.add(Tour.objects.get(pk=tour_id))
    return redirect('home')  # Redirect back to the home page