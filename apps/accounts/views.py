# apps/accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.views import View
from .forms import CustomLoginForm, UserTypeForm, TouristRegistrationForm, GuideRegistrationForm, TouristProfileForm, GuideProfileForm
from .models import Profile
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = CustomLoginForm
    redirect_authenticated_user = True

class UserTypeView(View):
    template_name = 'accounts/select_user_type.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = UserTypeForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserTypeForm(request.POST)
        if form.is_valid():
            user_type = form.cleaned_data['user_type']
            request.session['user_type'] = user_type
            return redirect('register_user')
        return render(request, self.template_name, {'form': form})

class RegistrationView(View):
    tourist_template = 'accounts/tourist_registration.html'
    guide_template = 'accounts/guide_registration.html'

    def get(self, request):
        user_type = request.session.get('user_type')
        if not user_type:
            return redirect('select_user_type')

        form = TouristRegistrationForm() if user_type == 'tourist' else GuideRegistrationForm()
        template = self.tourist_template if user_type == 'tourist' else self.guide_template

        return render(request, template, {'form': form})

    def post(self, request):
        user_type = request.session.get('user_type')
        if not user_type:
            return redirect('select_user_type')

        form = TouristRegistrationForm(request.POST) if user_type == 'tourist' else GuideRegistrationForm(request.POST)
        template = self.tourist_template if user_type == 'tourist' else self.guide_template

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome! Your {user_type} account has been created successfully.')
            return redirect('tourist_dashboard' if user_type == 'tourist' else 'guide_dashboard')

        return render(request, template, {'form': form})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import TouristProfileForm, GuideProfileForm


@login_required
def profile_view(request):
    user = request.user

    # Load the correct profile form based on user type
    if user.user_type == 'tourist':
        form_class = TouristProfileForm
        template = 'accounts/tourist_profile.html'
    else:
        form_class = GuideProfileForm
        template = 'accounts/guide_profile.html'

    # Load existing profile data
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        form = form_class(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect after saving
    else:
        form = form_class(instance=profile)

    return render(request, template, {'form': form})

