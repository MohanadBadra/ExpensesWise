from django.urls import path
from .views import RegistrationView, UsernameValidationView,EmailValidationView, VerificationView, LoginView, LogoutView, RequestPassword, ResetPassword
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('register', RegistrationView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()), name='validate-username'),
    path('validate-email', csrf_exempt(EmailValidationView.as_view()), name='validate-email'),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name='activate'),
    path('request-password', RequestPassword.as_view(), name='request-password'),
    path('reset-password/<uidb64>/<token>', ResetPassword.as_view(), name='reset-password'),
]
