from django import forms
from .models import Booking

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
        fields = ['number_of_participants', 'special_requests']
        widgets = {
            'number_of_participants': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10'
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requirements or requests?'
            })
        }
