from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django.core.exceptions import ValidationError


class User(AbstractUser):
    USER_TYPES = (
        ('tourist', 'Tourist'),
        ('guide', 'Guide'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    email = models.EmailField(_('email address'), unique=True)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class Profile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    country = CountryField(blank=True)
    languages = models.ManyToManyField('common.Language', blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Guide-specific fields
    is_verified = models.BooleanField(default=False)
    verification_documents = models.FileField(
        upload_to='verification_docs/',
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'jpg', 'jpeg', 'png']
            )
        ]
    )
    guide_license_number = models.CharField(max_length=50, blank=True)
    years_of_experience = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

    def clean(self):
        # Validate guide-specific fields
        """
         if self.user.user_type == 'guide':
             if not self.guide_license_number:
                 raise ValidationError({guide_license_number': 'Guide license number is required for guides'})
        """
        # Validate tourist-specific fields
        if self.user.user_type == 'tourist':
            if self.guide_license_number:
                raise ValidationError({
                    'guide_license_number': 'Tourists cannot have a guide license number'
                })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)