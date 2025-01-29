from django.urls import path
from .views import UserTypeView, RegistrationView, CustomLoginView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/type/', UserTypeView.as_view(), name='select_user_type'),
    path('register/', RegistrationView.as_view(), name='register_user'),

]