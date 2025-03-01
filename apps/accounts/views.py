# apps/accounts/views.py
from django.contrib.auth import login, get_user_model
from django.urls import reverse_lazy
from django.views import View
from .forms import CustomLoginForm, UserTypeForm, TouristRegistrationForm, GuideRegistrationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import TouristProfileForm, GuideProfileForm
from apps.tours.models import Tour
from apps.messaging.models import Message
from apps.bookings.models import Booking
from apps.reviews.models import Review
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .forms import PasswordResetRequestForm, SetPasswordForm
from apps.reviews.models import Wishlist

User = get_user_model()

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = CustomLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user  # Get the logged-in user
        if not user.user_type:
            return reverse_lazy('accounts:google_select_user_type')
        if user.user_type == 'tourist':
            return reverse_lazy('home') # Redirect to tourist dashboard
        elif user.user_type == 'guide':
            return reverse_lazy('accounts:guide_dashboard')  # Redirect to guide dashboard
        else:
            return reverse_lazy('home')



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
            return redirect('accounts:profile')

    else:
        form = form_class(instance=profile)

    context = {'form': form, 'profile': profile, 'user_type': user.get_user_type_display()}
    return render(request, template, context)


@login_required
def tourist_dashboard(request):
    if request.user.user_type != 'tourist':
        return redirect('home')
        
    # Get recent bookings (excluding completed ones)
    recent_bookings = Booking.objects.filter(
        tourist=request.user,
        status__in=['pending', 'confirmed', 'cancelled']
    ).select_related(
        'tour_date__tour',
        'tour_date__tour__guide'
    ).order_by('-booking_date')[:5]

    # Get completed bookings
    completed_bookings = Booking.objects.filter(
        tourist=request.user,
        status='completed'
    ).select_related(
        'tour_date__tour',
        'tour_date__tour__guide',
        'review'
    ).order_by('-tour_date__start_date')

    # Calculate pending reviews count
    pending_reviews_count = completed_bookings.filter(review__isnull=True).count()

    # Get wishlist items
    wishlist_items = Wishlist.objects.filter(
        tourist=request.user
    ).select_related(
        'tour', 'tour__guide'
    ).order_by('-added_date')

    context = {
        'recent_bookings': recent_bookings,
        'completed_bookings': completed_bookings,
        'wishlist_items': wishlist_items,
        'pending_reviews_count': pending_reviews_count,
    }
    
    return render(request, 'accounts/tourist_dashboard.html', context)


@login_required
def guide_dashboard(request):
    tours = Tour.objects.filter(guide=request.user)
    booking_requests = Booking.objects.filter(tour_date__tour__guide=request.user)  # Filter bookings
    unread_messages_count = Message.objects.filter(conversation__participants=request.user, is_read=False).count() #Unread messages
    reviews = Review.objects.filter(booking__tour_date__tour__guide=request.user)

    context = {
        'tours': tours,
        'booking_requests': booking_requests,
        'unread_messages_count': unread_messages_count,
        'reviews': reviews,
    }
    return render(request, 'accounts/guide_dashboard.html', context)


@login_required
def google_select_user_type(request):
    user_id = request.session.get('user_id')  # Get user ID from session
    if not user_id:
        return redirect('/')

    user = request.user

    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        user.user_type = user_type
        user.save()
        return redirect('/')

    return render(request, 'accounts/google_select_user_type.html')


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                # Generate token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # Build reset URL
                reset_url = request.build_absolute_uri(
                    reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )

                # Email content
                context = {
                    'user': user,
                    'reset_url': reset_url,
                }
                email_html = render_to_string('accounts/password_reset_email.html', context)

                # Send email
                send_mail(
                    'Password Reset Request',
                    'Please click the link to reset your password',
                    'noreply@yourdomain.com',
                    [email],
                    html_message=email_html,
                    fail_silently=False,
                )

                messages.success(request, 'Password reset link has been sent to your email.')
                return redirect('accounts:login')
            except User.DoesNotExist:
                messages.error(request, 'No user found with this email address.')
    else:
        form = PasswordResetRequestForm()

    return render(request, 'accounts/password_reset_request.html', {'form': form})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                messages.success(request, 'Your password has been reset successfully.')
                return redirect('accounts:login')
        else:
            form = SetPasswordForm()
        return render(request, 'accounts/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'Password reset link is invalid or has expired.')
        return redirect('accounts:login')