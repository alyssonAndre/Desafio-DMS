from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from usuarios.decorators import locador_required

class DecoratorsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_locador = User.objects.create_user(username='locador', password='testpass')
        self.user_nao_locador = User.objects.create_user(username='nao_locador', password='testpass')
        self.user_locador.userprofile.is_locador = True
        self.user_locador.userprofile.save()

    def test_access_by_locador(self):
        self.client.login(username='locador', password='testpass')
        response = self.client.get(reverse('profile'))  
        self.assertEqual(response.status_code, 200)

    def test_access_by_non_locador(self):
        self.client.login(username='nao_locador', password='testpass')
        response = self.client.get(reverse('campo_list'))  
        self.assertEqual(response.status_code, 403) 

    def test_access_without_login(self):
        response = self.client.get(reverse('profile'))  
        self.assertEqual(response.status_code, 302)  
        self.assertTrue('/login/' in response.url)  