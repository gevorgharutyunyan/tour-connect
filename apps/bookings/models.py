from django.conf import settings
from django.db import models
from django.utils import timezone


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    tourist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tour_date = models.ForeignKey('tours.TourDate', on_delete=models.PROTECT)
    number_of_participants = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    special_requests = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Booking {self.id} - {self.tour_date.tour.title}"

    def can_be_cancelled(self):
        """Check if the booking can be cancelled"""
        # Can't cancel if already cancelled or completed
        if self.status in ['cancelled', 'completed']:
            return False
        
        # Can't cancel if less than 24 hours before tour start
        if timezone.now() + timezone.timedelta(hours=24) > self.tour_date.start_date:
            return False
        
        return True

    @property
    def is_cancellable(self):
        # Add cancellation policy logic here
        return True