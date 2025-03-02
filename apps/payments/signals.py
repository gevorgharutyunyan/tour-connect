from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Transaction
from apps.messaging.models import Notification

@receiver(post_save, sender=Transaction)
def create_transaction_notifications(sender, instance, created, **kwargs):
    """Create notifications for transaction events"""
    if created:
        # Notify tourist about successful payment
        if instance.status == Transaction.COMPLETED:
            Notification.objects.create(
                user=instance.booking.tourist,
                title="Payment Successful",
                message=f"Your payment of ${instance.amount} for {instance.booking.tour_date.tour.title} has been processed successfully."
            )
            
            # Notify guide about new booking payment
            Notification.objects.create(
                user=instance.booking.tour_date.tour.guide,
                title="New Booking Payment",
                message=f"You received a new booking payment of ${instance.amount} for {instance.booking.tour_date.tour.title}."
            )
    
    # Notify about refunds
    elif instance.status == Transaction.REFUNDED:
        Notification.objects.create(
            user=instance.booking.tourist,
            title="Refund Processed",
            message=f"Your refund of ${instance.amount} for {instance.booking.tour_date.tour.title} has been processed."
        )
        
        Notification.objects.create(
            user=instance.booking.tour_date.tour.guide,
            title="Booking Refunded",
            message=f"A refund of ${instance.amount} has been processed for {instance.booking.tour_date.tour.title}."
        ) 