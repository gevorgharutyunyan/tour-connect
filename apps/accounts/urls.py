from django.urls import path
from .views import UserTypeView, RegistrationView, CustomLoginView, profile_view, guide_dashboard
from django.contrib.auth.views import LogoutView

app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('register/type/', UserTypeView.as_view(), name='select_user_type'),
    path('register/', RegistrationView.as_view(), name='register_user'),
    path('profile/', profile_view, name='profile'),
    path('guide_dashboard/', guide_dashboard, name='guide_dashboard'),
]