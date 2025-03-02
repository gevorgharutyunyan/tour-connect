from django import forms
from .models import PaymentMethod

class PaymentForm(forms.Form):
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label=None,
        required=True
    ) 