from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from allauth.mfa.adapter import DefaultMFAAdapter
from usuarios.models import UserProfile

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.is_active = True
        user.save()
        return user



class CustomMFAAdapter(DefaultMFAAdapter):
    def _update_2fa_status(self, user, is_enabled):
        print(f"Updating 2FA status for {user.username} to {is_enabled}")
        # Verifica se o UserProfile existe para o usuário
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.is_2fa_enabled = is_enabled
        profile.save()

    def mfa_enable(self, request, user):
        super().mfa_enable(request, user)
        self._update_2fa_status(user, True)

    def mfa_disable(self, request, user):
        super().mfa_disable(request, user)
        self._update_2fa_status(user, False)