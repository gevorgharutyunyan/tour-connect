from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .forms import UserTypeForm, TouristRegistrationForm, GuideRegistrationForm

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class UserTypeView(View):
    template_name = 'accounts/select_user_type.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = UserTypeForm()
        return render(request, 'accounts/select_user_type.html', {'form': form})

    def post(self, request):
        form = UserTypeForm(request.POST)
        if form.is_valid():
            user_type = form.cleaned_data['user_type']
            request.session['user_type'] = user_type
            return redirect('register_user')
        return render(request, 'accounts/select_user_type.html', {'form': form})


class RegistrationView(View):
    tourist_template = 'accounts/tourist_registration.html'
    guide_template = 'accounts/guide_registration.html'

    def get(self, request):
        user_type = request.session.get('user_type')

        if not user_type:
            return redirect('select_user_type')

        if user_type == 'tourist':
            form = TouristRegistrationForm()
            template = self.tourist_template
        else:
            form = GuideRegistrationForm()
            template = self.guide_template

        return render(request, template, {'form': form})

    def post(self, request):
        user_type = request.session.get('user_type')

        if not user_type:
            return redirect('select_user_type')

        if user_type == 'tourist':
            form = TouristRegistrationForm(request.POST)
            template = self.tourist_template
        else:
            form = GuideRegistrationForm(request.POST, request.FILES)
            template = self.guide_template

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome! Your {user_type} account has been created successfully.')

            # Redirect to different pages based on user type
            if user_type == 'tourist':
                return redirect('tourist_dashboard')
            else:
                return redirect('guide_dashboard')

        return render(request, template, {'form': form})