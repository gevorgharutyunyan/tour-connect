from django import forms
from .models import Language, Location

class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = ['name', 'code']


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'country', 'latitude', 'longitude']
