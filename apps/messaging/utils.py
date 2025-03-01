from .models import Notification

def create_notification(recipient, notification_type, title, message, related_object_id=None, related_object_type=None):
    """
    Create a new notification
    """
    return Notification.objects.create(
        recipient=recipient,
        type=notification_type,
        title=title,
        message=message,
        related_object_id=related_object_id,
        related_object_type=related_object_type
    )

def create_booking_notification(booking, notification_type='booking'):
    """
    Create a booking-related notification
    """
    if booking.status == 'pending':
        # Notify guide about new booking
        create_notification(
            recipient=booking.tour_date.tour.guide,
            notification_type=notification_type,
            title='New Booking Request',
            message=f'New booking request for {booking.tour_date.tour.title} from {booking.tourist.username}',
            related_object_id=booking.id,
            related_object_type='booking'
        )
    elif booking.status == 'confirmed':
        # Notify tourist about booking confirmation
        create_notification(
            recipient=booking.tourist,
            notification_type=notification_type,
            title='Booking Confirmed',
            message=f'Your booking for {booking.tour_date.tour.title} has been confirmed!',
            related_object_id=booking.id,
            related_object_type='booking'
        )
    elif booking.status == 'cancelled':
        # Notify tourist about booking cancellation
        create_notification(
            recipient=booking.tourist,
            notification_type=notification_type,
            title='Booking Cancelled',
            message=f'Your booking for {booking.tour_date.tour.title} has been cancelled.',
            related_object_id=booking.id,
            related_object_type='booking'
        )

def create_message_notification(message):
    """
    Create a message-related notification
    """
    # Get the other participant in the conversation
    recipient = message.conversation.participants.exclude(id=message.sender.id).first()
    
    create_notification(
        recipient=recipient,
        notification_type='message',
        title='New Message',
        message=f'New message from {message.sender.username}',
        related_object_id=message.conversation.id,
        related_object_type='conversation'
    )

def create_review_notification(review):
    """
    Create a review-related notification
    """
    create_notification(
        recipient=review.booking.tour_date.tour.guide,
        notification_type='review',
        title='New Review',
        message=f'New {review.rating}-star review from {review.booking.tourist.username}',
        related_object_id=review.id,
        related_object_type='review'
    ) 