from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('payment/<int:booking_id>/', views.payment_page, name='payment_page'),
    path('success/<str:transaction_id>/', views.payment_success, name='payment_success'),
    path('cancel/<str:transaction_id>/', views.payment_cancel, name='payment_cancel'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('setup-payout/', views.setup_payout_account, name='setup_payout_account'),
    path('create-stripe-account/', views.create_stripe_account, name='create_stripe_account'),
    path('transactions/', views.transaction_history, name='transaction_history'),
] 