import stripe
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from .models import Transaction, PaymentMethod, PlatformFee, PayoutAccount
import uuid

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:
    @staticmethod
    def create_payment_intent(booking):
        """Create a payment intent for a booking"""
        # Get active platform fee
        platform_fee = PlatformFee.objects.filter(is_active=True).first()
        if not platform_fee:
            platform_fee = PlatformFee.objects.create(
                percentage=15.0,
                description="Standard platform fee"
            )

        # Get payment method (assuming Stripe for now)
        payment_method = PaymentMethod.objects.get_or_create(
            name="Credit Card",
            defaults={'processing_fee_percentage': 2.9}
        )[0]

        # Calculate fees
        amount = booking.total_price
        platform_fee_amount = (amount * Decimal(platform_fee.percentage) / 100)
        processing_fee_amount = (amount * Decimal(payment_method.processing_fee_percentage) / 100)
        guide_payout_amount = amount - platform_fee_amount - processing_fee_amount

        # Create transaction record
        transaction = Transaction.objects.create(
            booking=booking,
            payment_method=payment_method,
            amount=amount,
            platform_fee_percentage=platform_fee.percentage,
            platform_fee_amount=platform_fee_amount,
            processing_fee_percentage=payment_method.processing_fee_percentage,
            processing_fee_amount=processing_fee_amount,
            guide_payout_amount=guide_payout_amount,
            transaction_id=str(uuid.uuid4())
        )

        try:
            # Create Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency='usd',
                metadata={
                    'booking_id': booking.id,
                    'transaction_id': transaction.transaction_id,
                    'guide_id': booking.tour_date.tour.guide.id
                }
            )
            
            return {
                'client_secret': intent.client_secret,
                'transaction_id': transaction.transaction_id
            }
            
        except stripe.error.StripeError as e:
            transaction.status = Transaction.FAILED
            transaction.save()
            raise e

    @staticmethod
    def process_payment_success(transaction_id):
        """Process successful payment"""
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        transaction.status = Transaction.COMPLETED
        transaction.save()

        # Update booking status
        booking = transaction.booking
        booking.status = 'confirmed'
        booking.save()

        return transaction

    @staticmethod
    def process_refund(transaction_id, reason):
        """Process refund for a transaction"""
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        
        try:
            # Find the payment intent
            payment_intents = stripe.PaymentIntent.list(
                metadata={'transaction_id': transaction_id}
            )
            
            if payment_intents.data:
                # Process refund through Stripe
                refund = stripe.Refund.create(
                    payment_intent=payment_intents.data[0].id
                )
                
                # Update transaction
                transaction.status = Transaction.REFUNDED
                transaction.refund_reason = reason
                transaction.refunded_at = timezone.now()
                transaction.save()
                
                # Update booking status
                transaction.booking.status = 'cancelled'
                transaction.booking.save()
                
                return transaction
            
            raise ValueError("Payment intent not found")
            
        except stripe.error.StripeError as e:
            raise e

    @staticmethod
    def process_guide_payout(transaction_id):
        """Process payout to guide"""
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        
        if transaction.status != Transaction.COMPLETED:
            raise ValueError("Cannot process payout for incomplete transaction")

        try:
            # Get guide's payout account
            payout_account = PayoutAccount.objects.get(
                guide=transaction.booking.tour_date.tour.guide,
                is_verified=True
            )

            if payout_account.payout_method == PayoutAccount.STRIPE:
                # Process Stripe payout
                payout = stripe.Transfer.create(
                    amount=int(transaction.guide_payout_amount * 100),  # Convert to cents
                    currency='usd',
                    destination=payout_account.account_details['stripe_account_id'],
                    metadata={
                        'transaction_id': transaction_id,
                        'booking_id': transaction.booking.id
                    }
                )
                return payout
            
            elif payout_account.payout_method == PayoutAccount.PAYPAL:
                # Implement PayPal payout logic
                pass
            
            elif payout_account.payout_method == PayoutAccount.BANK_TRANSFER:
                # Implement bank transfer logic
                pass

        except stripe.error.StripeError as e:
            raise e 