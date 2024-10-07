# test_email.py

from django.test import TestCase
from django.core.mail import send_mail
from django.core import mail
from django.conf import settings
import random

class EmailTestCase(TestCase):
    def setUp(self):
        # Configuração de e-mail para testes usando o backend de e-mail de memória
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

    def test_send_verification_email(self):
        subject = 'Código de Verificação'
        message = f'Seu código de verificação é {str(random.randint(100000, 999999))}'
        recipient_list = ['teste@exemplo.com']
        
        # Enviar o e-mail
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)

        # Verifique se o e-mail foi enviado
        email_sent = mail.outbox[0]  # Acessa o primeiro e-mail na caixa de saída

        # Verifique o assunto e a mensagem do e-mail enviado
        self.assertEqual(email_sent.subject, subject)
        self.assertEqual(email_sent.body, message)
        self.assertEqual(email_sent.to, recipient_list)

    def test_no_email_sent(self):
        """Testa se não há e-mails na caixa de saída quando nenhum e-mail é enviado."""
        self.assertEqual(len(mail.outbox), 0)
