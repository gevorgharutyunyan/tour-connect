from django import forms
from.models import Booking, Payment

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['tour_date', 'number_of_participants', 'special_requests']

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'transaction_id']  # Add more fields as needed
