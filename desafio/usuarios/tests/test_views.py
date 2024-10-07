from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from allauth.socialaccount.models import SocialApp
from usuarios.models import UserProfile
from usuarios.forms import (CustomUserCreationForm, VerificationForm, 
                            PasswordResetRequestForm, PasswordResetVerifyForm, 
                            PasswordResetCompleteForm, UserForm, UserProfileForm,
                            CustomMFAForm)
from django.contrib.sites.models import Site
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.messages import get_messages
from django.conf import settings
from io import BytesIO
from captcha.models import CaptchaStore
import random
import os

class ViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.site, created = Site.objects.get_or_create(
            domain='example.com',
            defaults={'name': 'example'}
        )
        cls.social_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': '892864066286-7qcnopm3ponadu130u0t9ine8i6kuj6a.apps.googleusercontent.com',
                'secret': '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',
            }
        )
        if created:
            cls.social_app.sites.add(cls.site)

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user)
        self.client.login(username='testuser', password='testpassword')

    # Register

    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/registrar.html')
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)

    def test_register_view_post_valid(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        })

        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content.decode('utf-8')}")

        self.assertEqual(response.status_code, 302, msg=f"Expected 302 but got {response.status_code}")
        self.assertRedirects(response, reverse('verificacao'), msg_prefix="Redirecionamento para 'verificacao' falhou")

    # Verification

    def test_verify_code_view_get(self):
        response = self.client.get(reverse('verificacao'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/codigo_de_verificacao.html')
        self.assertIsInstance(response.context['form'], VerificationForm)

    def test_verify_code_view_post_valid(self):
        self.user_profile.verification_code = str(random.randint(100000, 999999))
        self.user_profile.save()
        response = self.client.post(reverse('verificacao'), {
            'code': self.user_profile.verification_code
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    # Login

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/login.html')
        self.assertIsInstance(response.context['form'], AuthenticationForm)


    def test_login_view_post_valid(self):
        # Criando um CAPTCHA válido
        captcha = CaptchaStore.generate_key()
        captcha_response = CaptchaStore.objects.get(hashkey=captcha).response

        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword',
            'captcha_0': captcha,  # Hashkey do CAPTCHA
            'captcha_1': captcha_response  # Resposta do CAPTCHA
        })

        self.assertEqual(response.status_code, 302)

    def test_login_view_post_valid_2fa(self):
        captcha = CaptchaStore.generate_key()
        captcha_response = CaptchaStore.objects.get(hashkey=captcha).response
        
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword',
            'captcha_0': captcha,  
            'captcha_1': captcha_response,  
            '2fa_code': '123456'  
        })
        
        self.assertEqual(response.status_code, 302)
    
        
    # MFA Authentication

    def test_custom_mfa_authenticate_get(self):
        response = self.client.get(reverse('custom_mfa_authenticate'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mfa/authenticate.html')
        self.assertIsInstance(response.context['form'], CustomMFAForm)


    def test_custom_mfa_authenticate_post_invalid_code(self):
        self.user_profile.verification_code = '123456'
        self.user_profile.is_2fa_enabled = True
        self.user_profile.save()

        response = self.client.post(reverse('custom_mfa_authenticate'), {
            'code': '000000'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mfa/authenticate.html')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Código de autenticação inválido.')

    def test_custom_mfa_authenticate_post_user_profile_not_found(self):
        UserProfile.objects.filter(user=self.user).delete()

        response = self.client.post(reverse('custom_mfa_authenticate'), {
            'code': '123456'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mfa/authenticate.html')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Perfil de usuário não encontrado.')
        
        
    # Home

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/home.html')

    # Logout

    def test_logout_view(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    # Password Reset

    def test_password_reset_request_view_get(self):
        response = self.client.get(reverse('trocar-senha'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/trocarSenha.html')
        self.assertIsInstance(response.context['form'], PasswordResetRequestForm)

    def test_password_reset_request_view_post_valid(self):
        response = self.client.post(reverse('trocar-senha'), {'email': 'testuser@example.com'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('password_reset_verify'))

    def test_password_reset_verify_view_get(self):
        response = self.client.get(reverse('password_reset_verify'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/password_reset_verify.html')
        self.assertIsInstance(response.context['form'], PasswordResetVerifyForm)

    def test_password_reset_verify_view_post_valid(self):
        self.user_profile.reset_code = str(random.randint(100000, 999999))
        self.user_profile.save()
        response = self.client.post(reverse('password_reset_verify'), {
            'code': self.user_profile.reset_code
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('password_reset_complete'))

    def test_password_reset_complete_view_get(self):
        session = self.client.session
        session['reset_user_id'] = self.user.id
        session.save()

        response = self.client.get(reverse('password_reset_complete'))

        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content.decode('utf-8')}")

        self.assertEqual(response.status_code, 200, msg=f"Expected 200 but got {response.status_code}")


    def test_password_reset_complete_view_post_valid(self):
        new_password = 'newpassword123'

        session = self.client.session
        session['reset_user_id'] = self.user.id
        session.save()

        form_data = {
            'new_password1': new_password,
            'new_password2': new_password
        }

        response = self.client.post(reverse('password_reset_complete'), form_data)

        # Atualiza o objeto usuário após o reset de senha
        self.user.refresh_from_db()

        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content.decode('utf-8')}")
        print(f"User password: {self.user.password}")

        self.assertEqual(response.status_code, 302, msg=f"Expected 302 but got {response.status_code}")
        self.assertRedirects(response, reverse('login'), msg_prefix="Redirecionamento para 'login' falhou")

        captcha = CaptchaStore.generate_key()
        captcha_response = CaptchaStore.objects.get(hashkey=captcha).response

        login_data = {
            'username': self.user.username,
            'password': new_password,
            'captcha_0': captcha,  
            'captcha_1': captcha_response 
        }

        login_response = self.client.post(reverse('login'), login_data)

        print(f"Login response status code: {login_response.status_code}")
        print(f"Login response content: {login_response.content.decode('utf-8')}")

        self.assertEqual(login_response.status_code, 302, msg=f"Login falhou com status {login_response.status_code}")
        self.assertRedirects(login_response, reverse('home'), msg_prefix="Redirecionamento para 'home' falhou")

        user = authenticate(username=self.user.username, password=new_password)
        self.assertIsNotNone(user, msg="Autenticação com nova senha falhou")

    # Profile

    def test_profile_view_get(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/profile.html')
        self.assertIsInstance(response.context['user_form'], UserForm)
        self.assertIsInstance(response.context['profile_form'], UserProfileForm)

    def test_profile_view_post_valid(self):
        image_path = os.path.join(settings.BASE_DIR, 'usuarios/tests/test2_image.jpg')

        if not os.path.isfile(image_path):
            self.fail(f"Arquivo de imagem não encontrado em {image_path}")

        with open(image_path, 'rb') as image_file:
            image = InMemoryUploadedFile(
                file=BytesIO(image_file.read()), 
                field_name='profile_picture', 
                name='test2_image.jpg', 
                content_type='image/jpeg', 
                size=os.path.getsize(image_path), 
                charset=None
            )

        form_data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updateduser@example.com',
            'profile_picture': image,
            'phone_number': '1234567890'
        }

        response = self.client.post(reverse('profile'), data=form_data, follow=True, format='multipart')

        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content.decode('utf-8')}")

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, 'Updated', msg=f"First name was '{self.user.first_name}'")
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.email, 'updateduser@example.com')

        user_profile = UserProfile.objects.get(user=self.user)

        profile_picture_name = os.path.basename(user_profile.profile_picture.name)
        self.assertTrue(
            profile_picture_name.startswith('test2_image'),
            msg=f"Profile picture name was '{profile_picture_name}'"
        )
        self.assertEqual(user_profile.phone_number, '1234567890', msg=f"Phone number was '{user_profile.phone_number}'")
