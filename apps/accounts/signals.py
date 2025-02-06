from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import User, Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a profile for new users"""
    if created:
        with transaction.atomic():
            Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Ensure profile is saved when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()