import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views import View
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import (CustomUserCreationForm, VerificationForm, PasswordResetRequestForm,
                    PasswordResetVerifyForm, PasswordResetCompleteForm, UserForm, UserProfileForm, CustomMFAForm,CustomLoginForm)
from .models import UserProfile
from .tasks import send_mail_task
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'usuarios/activation_invalid.html')


class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'usuarios/registrar.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()

            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.verification_code = str(random.randint(100000, 999999))
            user_profile.save()

            subject = 'Código de Verificação'
            message = f'Seu código de verificação é {user_profile.verification_code}'
            user_email = form.cleaned_data.get('email')

            # Chamar a task do Celery
            send_mail_task.delay(subject, message, [user_email])

            return redirect('verificacao')
        return render(request, 'usuarios/registrar.html', {'form': form})



class VerifyCodeView(View):
    def get(self, request):
        form = VerificationForm()
        return render(request, 'usuarios/codigo_de_verificacao.html', {'form': form})

    def post(self, request):
        form = VerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            try:
                user_profile = UserProfile.objects.get(verification_code=code)
                user_profile.is_verified = True
                user_profile.user.is_active = True
                user_profile.user.save()
                user_profile.save()
                messages.success(request, 'Conta verificada com sucesso!')
                return redirect('login')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Código de verificação inválido.')
        return render(request, 'usuarios/codigo_de_verificacao.html', {'form': form})

class LoginView(View):
    def get(self, request):
        form = CustomLoginForm()  
        return render(request, 'usuarios/login.html', {'form': form})

    def post(self, request):
        if 'reload_captcha' in request.POST:
            # Cria um novo captcha
            form = CustomLoginForm()
            return render(request, 'usuarios/login.html', {'form': form})

        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                try:
                    user_profile = UserProfile.objects.get(user=user)
                    if user_profile.is_2fa_enabled:
                        return redirect('custom_mfa_authenticate')
                    else:
                        return redirect('home')
                except UserProfile.DoesNotExist:
                    messages.error(request, 'Perfil de usuário não encontrado.')
                    return render(request, 'usuarios/login.html', {'form': form})
            else:
                messages.error(request, 'Credenciais inválidas.')

        messages.error(request, 'Captcha ou credenciais incorretos.')
        return render(request, 'usuarios/login.html', {'form': form})


class HomeView(View):
    def get(self, request):
        return render(request, 'home/home.html')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')


class PasswordResetRequestView(View):
    def get(self, request):
        form = PasswordResetRequestForm()
        return render(request, 'usuarios/trocarSenha.html', {'form': form})

    def post(self, request):
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                user = User.objects.get(email=email)
                user_profile, created = UserProfile.objects.get_or_create(user=user)

                user_profile.reset_code = str(random.randint(100000, 999999))
                user_profile.save()

                subject = 'Código de Redefinição de Senha'
                message = f'Seu código de redefinição de senha é {user_profile.reset_code}'
                
                # Chamar a task do Celery
                send_mail_task.delay(subject, message, [email])

                return redirect('password_reset_verify')
            except User.DoesNotExist:
                messages.error(request, 'Email não encontrado.')
        return render(request, 'usuarios/trocarSenha.html', {'form': form})



class PasswordResetVerifyView(View):
    def get(self, request):
        form = PasswordResetVerifyForm()
        return render(request, 'usuarios/password_reset_verify.html', {'form': form})

    def post(self, request):
        form = PasswordResetVerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            try:
                user_profile = UserProfile.objects.get(reset_code=code)
                request.session['reset_user_id'] = user_profile.user.id
                return redirect('password_reset_complete')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Código de redefinição inválido.')
        return render(request, 'usuarios/password_reset_verify.html', {'form': form})


class PasswordResetCompleteView(View):
    def get(self, request):
        user_id = request.session.get('reset_user_id')
        if not user_id:
            return redirect('login')
        user = get_object_or_404(User, id=user_id)
        form = PasswordResetCompleteForm(user=user)
        return render(request, 'usuarios/password_reset_complete.html', {'form': form})

    def post(self, request):
        user_id = request.session.get('reset_user_id')
        if not user_id:
            return redirect('login')

        user = get_object_or_404(User, id=user_id)
        form = PasswordResetCompleteForm(user=user, data=request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Senha redefinida com sucesso!')
            del request.session['reset_user_id']
            return redirect('login')

        return render(request, 'usuarios/password_reset_complete.html', {'form': form})


@login_required
def profile_view(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if 'remove_picture' in request.POST:
            if user_profile.profile_picture:
                user_profile.profile_picture.delete(save=False)
                user_profile.profile_picture = None
                user_profile.save()
                messages.success(request, 'Sua foto de perfil foi removida com sucesso.')
            return redirect('profile')

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso.')
            return redirect('profile')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')

    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=user_profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_profile': user_profile,
        'is_editable': request.user.is_authenticated,
    }
    return render(request, 'usuarios/profile.html', context)

class CustomMFAAuthenticateView(View):
    def get(self, request):
        form = CustomMFAForm()
        return render(request, 'mfa/authenticate.html', {'form': form})

    def post(self, request):
        form = CustomMFAForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                if code == user_profile.verification_code:
                    user_profile.is_verified = True
                    user_profile.is_2fa_enabled = True
                    user_profile.save()

                    user = User.objects.get(id=request.session['pre_2fa_user_id'])
                    request.user = user
                    login(request, user)
                    del request.session['pre_2fa_user_id']

                    return redirect('home')
                else:
                    messages.error(request, 'Código de autenticação inválido.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Perfil de usuário não encontrado.')
        return render(request, 'mfa/authenticate.html', {'form': form})
