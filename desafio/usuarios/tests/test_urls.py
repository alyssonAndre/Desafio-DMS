from django.test import SimpleTestCase
from django.urls import reverse, resolve
from usuarios.views import (
    PasswordResetRequestView,
    PasswordResetVerifyView,
    PasswordResetCompleteView,
    RegisterView,
    VerifyCodeView,
    LoginView,
    LogoutView,
    profile_view
)
from home.views import home_view

class UrlTests(SimpleTestCase):
    def assertViewClass(self, url_name, expected_view_class):
        url = reverse(url_name)
        resolved = resolve(url)
        view_func = resolved.func
        
        print(f"Testing URL: {url}")
        print(f"Resolved view function: {view_func}")

        self.assertIsNotNone(view_func, f"URL '{url_name}' resolved to None. Check your URL patterns.")
        
        if hasattr(view_func, 'view_class'):
            self.assertEqual(view_func.view_class, expected_view_class,
                             f"URL '{url_name}' does not resolve to the expected view class. Expected '{expected_view_class}', got '{view_func.view_class}'.")
        else:
            self.assertEqual(view_func, expected_view_class,
                             f"URL '{url_name}' does not resolve to the expected view function. Expected '{expected_view_class}', got '{view_func}'.")


#urls

    def test_register_url(self):
        self.assertViewClass('register', RegisterView)

    def test_verificacao_url(self):
        self.assertViewClass('verificacao', VerifyCodeView)

    def test_login_url(self):
        self.assertViewClass('login', LoginView)

    def test_logout_url(self):
        self.assertViewClass('logout', LogoutView)

    def test_trocar_senha_url(self):
        self.assertViewClass('trocar-senha', PasswordResetRequestView)

    def test_password_reset_verify_url(self):
        self.assertViewClass('password_reset_verify', PasswordResetVerifyView)

    def test_password_reset_complete_url(self):
        self.assertViewClass('password_reset_complete', PasswordResetCompleteView)

    def test_profile_url(self):
        self.assertViewClass('profile', profile_view)

    def test_home_url(self):
        url = reverse('home')
        view_func = resolve(url).func
        
        print(f"Testing URL: {url}")
        print(f"Resolved view function: {view_func}")
        
        self.assertIsNotNone(view_func, "URL 'home' resolved to None. Check your URL patterns.")
        self.assertEqual(view_func, home_view,
                         "URL 'home' does not resolve to the expected view function. Expected 'home_view', got '{}'.".format(view_func))
