# apps/accounts/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm

from .models import User


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Email address",  # Change the displayed label
        # widget=forms.EmailInput(attrs={'autofocus': True})  # Change input type to email
    )


class UserTypeForm(forms.Form):
    USER_TYPES = (('tourist', 'I am a Tourist'), ('guide', 'I am a Guide'),)
    user_type = forms.ChoiceField(choices=USER_TYPES, widget=forms.RadioSelect,
        label="What type of account would you like to create?")


class TouristRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'tourist'
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class GuideRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField(required=True)
    guide_license_number = forms.CharField(required=True)
    years_of_experience = forms.IntegerField(required=True)
    verification_documents = forms.FileField(required=True)

    class Meta:
        model = User
        fields = (
        'email', 'username', 'first_name', 'last_name', 'phone_number', 'guide_license_number', 'years_of_experience',
        'verification_documents', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'guide'
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
