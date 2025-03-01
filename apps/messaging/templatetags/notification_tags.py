from django import template
from apps.messaging.models import Notification

register = template.Library()

@register.simple_tag
def unread_notifications_count(user):
    """Return the count of unread notifications for a user"""
    return Notification.objects.filter(recipient=user, is_read=False).count() 