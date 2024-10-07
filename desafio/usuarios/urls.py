from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import (
    RegisterView, VerifyCodeView, LoginView, HomeView, LogoutView,
    PasswordResetRequestView, PasswordResetVerifyView, PasswordResetCompleteView, profile_view,CustomMFAAuthenticateView
)

urlpatterns = [
    path('registrar-se/', RegisterView.as_view(), name='register'),
    path('verificacao/', VerifyCodeView.as_view(), name='verificacao'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('trocar-senha/', PasswordResetRequestView.as_view(), name='trocar-senha'),
    path('password_reset_request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-verify/', PasswordResetVerifyView.as_view(), name='password_reset_verify'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('profile/', profile_view, name='profile'),
    path('custom-mfa-authenticate/', CustomMFAAuthenticateView.as_view(), name='custom_mfa_authenticate'),
    path('', HomeView.as_view(), name='home'),
    path('captcha/', include('captcha.urls')),
  
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


