# apps/accounts/views.py
from django.contrib.auth import login
from django.contrib import messages
from django.views import View
from .forms import CustomLoginForm, UserTypeForm, TouristRegistrationForm, GuideRegistrationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import TouristProfileForm, GuideProfileForm



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
            return redirect('accounts:register_user')
        return render(request, self.template_name, {'form': form})


class RegistrationView(View):
    tourist_template = 'accounts/tourist_registration.html'
    guide_template = 'accounts/guide_registration.html'

    def get(self, request):
        user_type = request.session.get('user_type')
        if not user_type:
            return redirect('accounts:select_user_type')

        form = TouristRegistrationForm() if user_type == 'tourist' else GuideRegistrationForm()
        template = self.tourist_template if user_type == 'tourist' else self.guide_template

        return render(request, template, {'form': form})

    def post(self, request):
        user_type = request.session.get('user_type')
        if not user_type:
            return redirect('accounts:select_user_type')

        form = TouristRegistrationForm(request.POST) if user_type == 'tourist' else GuideRegistrationForm(request.POST)
        template = self.tourist_template if user_type == 'tourist' else self.guide_template

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome! Your {user_type} account has been created successfully.')
            return redirect('tourist_dashboard' if user_type == 'tourist' else 'guide_dashboard')

        return render(request, template, {'form': form})



@login_required
def profile_view(request):
    user = request.user

    # Determine form class and template based on user type
    if user.user_type == 'tourist':
        form_class = TouristProfileForm
        template = 'accounts/tourist_profile.html'
    else:
        form_class = GuideProfileForm
        template = 'accounts/guide_profile.html'

    # Get or create profile
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')

    else:
        form = form_class(instance=profile)

    context = {'form': form, 'profile': profile, 'user_type': user.get_user_type_display()}
    return render(request, template, context)
