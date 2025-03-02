from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .services import PaymentService
from .models import Transaction, PayoutAccount, PaymentMethod
from apps.bookings.models import Booking
from decimal import Decimal
import stripe
import json
import time

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def payment_page(request, booking_id):
    """Display payment page for a booking"""
    booking = get_object_or_404(Booking, id=booking_id, tourist=request.user)
    
    # Get payment method from session or default to first available
    payment_method_id = request.session.get('payment_method_id')
    if payment_method_id:
        payment_method = get_object_or_404(PaymentMethod, id=payment_method_id)
    else:
        payment_method = PaymentMethod.objects.filter(is_active=True).first()
    
    # Create or get transaction
    transaction, created = Transaction.objects.get_or_create(
        booking=booking,
        defaults={
            'payment_method': payment_method,
            'amount': booking.total_price,
            'platform_fee_percentage': Decimal('15.0'),  # Convert to Decimal
            'processing_fee_percentage': payment_method.processing_fee_percentage,
            'transaction_id': f"TR{booking.id}-{int(time.time())}"  # Generate unique transaction ID
        }
    )
    
    context = {
        'booking': booking,
        'transaction': transaction,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'payment_method': payment_method
    }
    
    return render(request, 'payments/payment.html', context)

@login_required
def payment_success(request, transaction_id):
    """Handle successful payment"""
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
    
    try:
        PaymentService.process_payment_success(transaction_id)
        return render(request, 'payments/success.html', {'transaction': transaction})
        
    except Exception as e:
        return render(request, 'payments/error.html', {'error': str(e)})

@login_required
def payment_cancel(request, transaction_id):
    """Handle cancelled payment"""
    return render(request, 'payments/cancel.html')

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        # Handle successful payment
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            transaction_id = payment_intent.metadata.get('transaction_id')
            if transaction_id:
                PaymentService.process_payment_success(transaction_id)
        
        # Handle failed payment
        elif event.type == 'payment_intent.payment_failed':
            payment_intent = event.data.object
            transaction_id = payment_intent.metadata.get('transaction_id')
            if transaction_id:
                transaction = Transaction.objects.get(transaction_id=transaction_id)
                transaction.status = Transaction.FAILED
                transaction.save()
        
        return HttpResponse(status=200)
        
    except Exception as e:
        return HttpResponse(status=400)

@login_required
def setup_payout_account(request):
    """Setup payout account for guides"""
    if request.user.user_type != 'guide':
        return redirect('home')
    
    if request.method == 'POST':
        data = json.loads(request.body)
        payout_method = data.get('payout_method')
        account_details = data.get('account_details')
        
        # Create or update payout account
        PayoutAccount.objects.update_or_create(
            guide=request.user,
            defaults={
                'payout_method': payout_method,
                'account_details': account_details,
                'is_verified': False  # Require verification process
            }
        )
        
        return JsonResponse({'status': 'success'})
    
    payout_account = PayoutAccount.objects.filter(guide=request.user).first()
    return render(request, 'payments/setup_payout.html', {'payout_account': payout_account})

@login_required
def transaction_history(request):
    """View transaction history"""
    if request.user.user_type == 'guide':
        transactions = Transaction.objects.filter(
            booking__tour_date__tour__guide=request.user
        ).select_related('booking', 'payment_method')
    else:
        transactions = Transaction.objects.filter(
            booking__tourist=request.user
        ).select_related('booking', 'payment_method')
    
    return render(request, 'payments/transaction_history.html', {'transactions': transactions})

@login_required
def create_stripe_account(request):
    """Create a Stripe Connect account for guides"""
    if request.user.user_type != 'guide':
        return JsonResponse({'error': 'Only guides can create Stripe accounts'}, status=403)
    
    try:
        # Create a Stripe Connect account
        account = stripe.Account.create(
            type='express',
            country='US',
            email=request.user.email,
            capabilities={
                'card_payments': {'requested': True},
                'transfers': {'requested': True},
            },
            business_type='individual',
        )
        
        # Create an account link for onboarding
        account_link = stripe.AccountLink.create(
            account=account.id,
            refresh_url=request.build_absolute_uri('/payments/setup-payout/'),
            return_url=request.build_absolute_uri('/payments/setup-payout/'),
            type='account_onboarding',
        )
        
        # Save the Stripe account ID
        PayoutAccount.objects.update_or_create(
            guide=request.user,
            defaults={
                'payout_method': PayoutAccount.STRIPE,
                'account_details': {'stripe_account_id': account.id},
                'is_verified': False
            }
        )
        
        return JsonResponse({'url': account_link.url})
        
    except stripe.error.StripeError as e:
        return JsonResponse({'error': str(e)}, status=400)
