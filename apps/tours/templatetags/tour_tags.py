from django import template
from apps.bookings.models import Booking

register = template.Library()

@register.filter
def has_booked(user, tour):
    """Check if a user has booked a specific tour"""
    if not user.is_authenticated or user.user_type != 'tourist':
        return False
    return Booking.objects.filter(
        tourist=user,
        tour_date__tour=tour,
        status__in=['pending', 'confirmed', 'completed']
    ).exists() 