from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db.models import Avg, F
from apps.common.models import Language
from django.utils import timezone

User = get_user_model()

class Tour(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('challenging', 'Challenging'),
    ]

    DURATION_CHOICES = [
        ('1-3', '1-3 hours'),
        ('4-6', '4-6 hours'),
        ('7-12', '7-12 hours'),
        ('full-day', 'Full Day'),
        ('multi-day', 'Multi Day')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50, choices=DURATION_CHOICES)
    location = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    max_participants = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    included_services = models.TextField(blank=True)
    excluded_services = models.TextField(blank=True)
    meeting_point = models.TextField()
    cancellation_policy = models.TextField()
    guide = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tours')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    languages = models.ManyToManyField('common.Language', related_name='tours')
    favorited_by = models.ManyToManyField(User, related_name='favorite_tours', blank=True)

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        return self.reviews.aggregate(Avg('rating'))['rating__avg']

    def get_available_dates(self):
        return self.dates.filter(max_spots__gt=0)

    @property
    def is_available(self):
        """Check if the tour has any available dates in the future with available spots"""
        return self.dates.filter(
            start_date__gte=timezone.now().date(),
            max_spots__gt=F('booked_spots')
        ).exists()

class TourImage(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='tour_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_primary:
            TourImage.objects.filter(tour=self.tour, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

class TourDate(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='dates')
    start_date = models.DateField()
    start_time = models.TimeField()
    max_spots = models.PositiveIntegerField()
    booked_spots = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['start_date', 'start_time']

    def __str__(self):
        return f"{self.tour.title} - {self.start_date}"

    @property
    def available_spots(self):
        return self.max_spots - self.booked_spots

    @property
    def is_available(self):
        return self.start_date >= timezone.now().date() and self.available_spots > 0

class SavedSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    name = models.CharField(max_length=100)
    filters = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s search: {self.name}"

class Review(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['tour', 'user']

    def __str__(self):
        return f"{self.user.username}'s review of {self.tour.title}"
