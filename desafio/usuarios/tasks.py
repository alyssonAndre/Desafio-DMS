# no seu_app/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_mail_task(subject, message, recipient_list):
    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, "EMAIL_HOST_USER", None),
        recipient_list=recipient_list,
        fail_silently=False
    )
    logger.info(f"E-mail enviado para {recipient_list} com o assunto '{subject}'")
