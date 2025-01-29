from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField


class User(AbstractUser):
    USER_TYPES = (
        ('tourist', 'Tourist'),
        ('guide', 'Guide'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    country = CountryField(blank=True)
    languages = models.ManyToManyField('common.Language', blank=True)

    # Guide specific fields
    is_verified = models.BooleanField(default=False)
    verification_documents = models.FileField(upload_to='verification_docs/', blank=True)
    guide_license_number = models.CharField(max_length=50, blank=True)
    years_of_experience = models.PositiveIntegerField(null=True, blank=True)

    # Tourist specific fields
    preferences = models.ManyToManyField('tours.TourCategory', blank=True)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')