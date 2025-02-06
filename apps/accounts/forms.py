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
          # Create profile after saving user
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
        return user


class BaseProfileForm(forms.ModelForm):
    """Base form for shared profile fields"""

    class Meta:
        model = Profile
        fields = [
            'phone_number',
            'bio',
            'profile_picture',
            'date_of_birth',
            'country',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Remove any non-digit characters
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) < 10:
                raise forms.ValidationError("Phone number must be at least 10 digits")
        return phone


class TouristProfileForm(BaseProfileForm):
    class Meta(BaseProfileForm.Meta):
        fields = BaseProfileForm.Meta.fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class GuideProfileForm(BaseProfileForm):
    class Meta(BaseProfileForm.Meta):
        fields = BaseProfileForm.Meta.fields + [
            'guide_license_number',
            'years_of_experience',
            'verification_documents',
            'languages'
        ]

    def clean_verification_documents(self):
        docs = self.cleaned_data.get('verification_documents')
        if docs:
            if docs.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("File size must be under 5MB")
        return docs
