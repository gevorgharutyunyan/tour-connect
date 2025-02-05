# apps/accounts/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User, Profile

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label="Email address")

class UserTypeForm(forms.Form):
    USER_TYPES = (('tourist', 'I am a Tourist'), ('guide', 'I am a Guide'))
    user_type = forms.ChoiceField(choices=USER_TYPES, widget=forms.RadioSelect, label="What type of account would you like to create?")

class TouristRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'tourist'
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.create(user=user)  # Create profile after saving user
        return user

class GuideRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'guide'
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.create(user=user)  # Create profile after saving user
        return user

class TouristProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number']  # Add more fields if needed

class GuideProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'guide_license_number', 'years_of_experience', 'verification_documents']