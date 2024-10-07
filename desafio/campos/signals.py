from django.db.models.signals import post_save
from django.dispatch import receiver
from campos.models import Comentario
from campos.views import enviar_resumo_feedback 

@receiver(post_save, sender=Comentario)
def comentario_salvo(sender, instance, **kwargs):
    enviar_resumo_feedback()