from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from usuarios.models import UserProfile
from usuarios.forms import (CustomUserCreationForm, VerificationForm, 
                             PasswordResetRequestForm, PasswordResetVerifyForm, 
                             PasswordResetCompleteForm, UserProfileForm, UserForm)

class CustomUserCreationFormTests(TestCase):

    def test_valid_form(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'username': 'newuser',
            'email': 'not-an-email',
            'password1': 'newpassword123',
            'password2': 'differentpassword'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('password2', form.errors)
        self.assertEqual(form.errors['email'], ['Informe um endereço de email válido.'])
        self.assertEqual(form.errors['password2'], ['Os dois campos de senha não correspondem.'])

class VerificationFormTests(TestCase):
    def test_valid_form(self):
        form_data = {'code': '123456'}
        form = VerificationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {'code': ''}
        form = VerificationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('code', form.errors)

class PasswordResetRequestFormTests(TestCase):
    def test_valid_form(self):
        User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword')
        form_data = {'email': 'testuser@example.com'}
        form = PasswordResetRequestForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {'email': 'nonexistent@example.com'}
        form = PasswordResetRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

class PasswordResetVerifyFormTests(TestCase):
    def test_valid_form(self):
        form_data = {'code': '123456'}
        form = PasswordResetVerifyForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {'code': ''}
        form = PasswordResetVerifyForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('code', form.errors)

class PasswordResetCompleteFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='oldpassword')

    def test_valid_form(self):
        form_data = {
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123'
        }
        form = PasswordResetCompleteForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'new_password1': 'newpassword123',
            'new_password2': 'differentpassword'
        }
        form = PasswordResetCompleteForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password2', form.errors)

class UserProfileFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword')
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user)

    def test_valid_form(self):
        form_data = {'phone_number': '987654321'}
        form = UserProfileForm(instance=self.user_profile, data=form_data)
        self.assertTrue(form.is_valid())
        profile = form.save()
        self.assertEqual(profile.phone_number, '987654321')

    def test_invalid_form(self):
        form_data = {'phone_number': ''}
        form = UserProfileForm(instance=self.user_profile, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)

    def test_form_with_picture(self):
        with open('usuarios/tests/test_image.jpg', 'rb') as image_file:
            image = SimpleUploadedFile(name='test_image.jpg', content=image_file.read(), content_type='image/jpeg')

        form_data = {'phone_number': '123456789'}
        form = UserProfileForm(instance=self.user_profile, data=form_data, files={'profile_picture': image})

        self.assertTrue(form.is_valid())
        profile = form.save()
        self.assertEqual(profile.phone_number, '123456789')
        self.assertIsNotNone(profile.profile_picture)

class UserFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword')

    def test_valid_form(self):
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com'
        }
        form = UserForm(instance=self.user, data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'john.doe@example.com')

    def test_invalid_form(self):
        form_data = {'first_name': '', 'last_name': '', 'email': ''}
        form = UserForm(instance=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)
        self.assertIn('email', form.errors)
