from django.db import models
from django.conf import settings


class TourCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='category_icons/', blank=True)

    class Meta:
        verbose_name_plural = 'Tour Categories'

    def __str__(self):
        return self.name


class Tour(models.Model):
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('challenging', 'Challenging'),
    )

    guide = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tours')
    title = models.CharField(max_length=200)
    description = models.TextField()
    categories = models.ManyToManyField(TourCategory)
    location = models.ForeignKey('common.Location', on_delete=models.CASCADE)
    duration = models.DurationField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    max_participants = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    included_services = models.TextField()
    excluded_services = models.TextField(blank=True)
    meeting_point = models.CharField(max_length=255)
    languages = models.ManyToManyField('common.Language')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    cancellation_policy = models.TextField()


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
    end_date = models.DateField()
    start_time = models.TimeField()
    available_spots = models.PositiveIntegerField()
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)
