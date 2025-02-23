from django import forms
from.models import Booking, Payment
from apps.tours.models import TourDate

class BookingForm(forms.ModelForm):
    """
    tour_date = forms.ModelChoiceField(
        queryset=TourDate.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select a Tour Date",
        required=True
    )
    """

    class Meta:
        model = Booking
        fields = [ 'number_of_participants', 'special_requests'] #'tour_date', # FIXME think about this again(add for tourist or not)

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method']  # Add more fields as needed
