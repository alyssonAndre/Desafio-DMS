from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.account.utils import send_email_confirmation
from allauth.account.signals import user_logged_in
from allauth.socialaccount.signals import social_account_added
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Cria um novo UserProfile se não existir para o usuário
        UserProfile.objects.get_or_create(user=instance)
    else:
        # Atualiza o UserProfile se existir
        if hasattr(instance, 'userprofile'):
            instance.userprofile.save()


@receiver(user_logged_in)
def handle_user_logged_in(sender, request, user, **kwargs):
    if not user.username:
        if user.email:
            username = extract_first_name_from_email(user.email)
            unique_username = username
            counter = 1
            while User.objects.filter(username=unique_username).exists():
                unique_username = f"{username}{counter}"
                counter += 1
            user.username = unique_username
            user.save()

    if user.email and not user.emailaddress_set.filter(verified=True).exists():
        print("Calling send_email_confirmation")
        if not user.is_active:
            user.is_active = True
            user.save()
        send_email_confirmation(request, user)

@receiver(social_account_added)
def handle_social_account_added(sender, request, sociallogin, **kwargs):
    if sociallogin.account.provider == 'google':
        user = sociallogin.user
        if user.email:
            user.is_active = True
            user.save()
        login(request, user)
        return redirect('/')  
    
def extract_first_name_from_email(email):
    local_part = email.split('@')[0]  # Parte local do e-mail
    first_name = local_part.split('.')[0]  # Pegando o primeiro nome antes do ponto
    return first_name
