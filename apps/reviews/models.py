from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

class Review(models.Model):
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    photos = models.ManyToManyField('ReviewPhoto', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)

class ReviewPhoto(models.Model):
    image = models.ImageField(upload_to='review_photos/')
    caption = models.CharField(max_length=200, blank=True)

class Wishlist(models.Model):
    tourist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tour = models.ForeignKey('tours.Tour', on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)