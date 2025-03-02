from django.db import models
from django.conf import settings
from apps.bookings.models import Booking
from decimal import Decimal

class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)  # e.g., "Credit Card", "PayPal"
    is_active = models.BooleanField(default=True)
    processing_fee_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=2.9)  # e.g., 2.9%
    
    def __str__(self):
        return self.name

class PlatformFee(models.Model):
    percentage = models.DecimalField(max_digits=4, decimal_places=2, default=15.0)  # Platform fee percentage
    description = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.percentage}% - {self.description}"

class Transaction(models.Model):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
        (REFUNDED, 'Refunded'),
    ]
    
    booking = models.OneToOneField(Booking, on_delete=models.PROTECT)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    
    # Platform fee details
    platform_fee_percentage = models.DecimalField(max_digits=4, decimal_places=2)
    platform_fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment processing fee
    processing_fee_percentage = models.DecimalField(max_digits=4, decimal_places=2)
    processing_fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Guide payout amount (after fees)
    guide_payout_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Transaction details
    transaction_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Refund tracking
    refund_reason = models.TextField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only calculate fees on creation
            # Convert percentages to Decimal
            platform_fee_percentage = Decimal(str(self.platform_fee_percentage))
            processing_fee_percentage = Decimal(str(self.processing_fee_percentage))
            
            # Calculate platform fee
            self.platform_fee_amount = (self.amount * platform_fee_percentage) / Decimal('100')
            
            # Calculate processing fee
            self.processing_fee_amount = (self.amount * processing_fee_percentage) / Decimal('100')
            
            # Calculate guide payout
            self.guide_payout_amount = self.amount - self.platform_fee_amount - self.processing_fee_amount
            
        super().save(*args, **kwargs)

class PayoutAccount(models.Model):
    STRIPE = 'stripe'
    PAYPAL = 'paypal'
    BANK_TRANSFER = 'bank'
    
    PAYOUT_METHOD_CHOICES = [
        (STRIPE, 'Stripe'),
        (PAYPAL, 'PayPal'),
        (BANK_TRANSFER, 'Bank Transfer'),
    ]
    
    guide = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payout_method = models.CharField(max_length=20, choices=PAYOUT_METHOD_CHOICES)
    account_details = models.JSONField()  # Stores account details securely
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.guide.get_full_name()} - {self.get_payout_method_display()}"
