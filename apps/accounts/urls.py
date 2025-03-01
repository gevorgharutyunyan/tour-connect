from django.urls import path
from .views import (UserTypeView, RegistrationView, CustomLoginView, profile_view, guide_dashboard,
                    google_select_user_type,password_reset_confirm,password_reset_request,
                    tourist_dashboard)

from django.contrib.auth.views import LogoutView

app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('register/type/', UserTypeView.as_view(), name='select_user_type'),
    path('register/', RegistrationView.as_view(), name='register_user'),
    path('profile/', profile_view, name='profile'),
    path('guide_dashboard/', guide_dashboard, name='guide_dashboard'),
    path('google-select-user-type/', google_select_user_type, name='google_select_user_type'),
    path('password-reset/', password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/<str:uidb64>/<str:token>/', password_reset_confirm,
         name='password_reset_confirm'),
    path('tourist/dashboard/', tourist_dashboard, name='tourist_dashboard'),
]