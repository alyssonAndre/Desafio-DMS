# usuarios/tests/test_signals.py
from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from allauth.account.signals import user_logged_in
from allauth.socialaccount.signals import social_account_added
from usuarios.models import UserProfile

User = get_user_model()

class SignalsTest(TestCase):
    def setUp(self):
        # Configuração do ambiente antes de cada teste
        self.user = User.objects.create_user(username='existinguser', password='testpass')
        # Cria um UserProfile para o usuário
        UserProfile.objects.get_or_create(user=self.user)

    def test_create_user_profile_on_user_creation(self):
        # Cria um novo usuário
        user = User.objects.create_user(username='newuser', password='newpass')
        
        # Verifica se um UserProfile foi criado para o novo usuário
        user_profile_exists = UserProfile.objects.filter(user=user).exists()
        self.assertTrue(user_profile_exists)

    def test_update_user_profile_on_user_update(self):
        # Atualiza o usuário
        self.user.username = 'updateduser'
        self.user.save()
        
        # Verifica se o UserProfile foi salvo e atualizado
        user_profile = UserProfile.objects.get(user=self.user)
        self.assertIsNotNone(user_profile)

    def tearDown(self):
        # Limpeza do ambiente após cada teste
        UserProfile.objects.all().delete()
        User.objects.all().delete()

class UserLoggedInSignalTest(TestCase):
    @patch('usuarios.signals.send_email_confirmation')
    @patch('django.contrib.auth.get_user_model')
    def test_handle_user_logged_in(self, MockUser, mock_send_email_confirmation):
        # Preparar o mock do User
        mock_user = MagicMock()
        mock_user.email = 'test@example.com'
        mock_user.is_active = False
        mock_user.username = None  # Simular que o username está vazio
        mock_user.emailaddress_set.filter.return_value.exists.return_value = False  # Simular que o email não está verificado

        # Configurar o retorno do mock para get_user_model
        MockUser.objects.create.return_value = mock_user

        # Simular o sinal de login
        user_logged_in.send(sender=None, request=None, user=mock_user)

        # Verificar se o e-mail de confirmação foi enviado
        mock_send_email_confirmation.assert_called_once_with(None, mock_user)

class SocialAccountAddedSignalTest(TestCase):
    @patch('usuarios.signals.login')
    @patch('usuarios.signals.redirect')
    def test_handle_social_account_added(self, mock_redirect, mock_login):
        # Preparar o mock para o SocialLogin
        mock_sociallogin = MagicMock()
        mock_sociallogin.account.provider = 'google'
        mock_sociallogin.user = MagicMock()
        mock_sociallogin.user.email = 'test@example.com'
        
        # Simular o sinal de conta social adicionada
        response = social_account_added.send(sender=None, request=None, sociallogin=mock_sociallogin)
        
        # Verificar se o usuário foi ativado e o login foi realizado
        mock_sociallogin.user.is_active = True
        mock_sociallogin.user.save.assert_called_once()
        mock_login.assert_called_once_with(None, mock_sociallogin.user)
        mock_redirect.assert_called_once_with('/')

