from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from decimal import Decimal
from django.utils import timezone


class Campo(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    cidade = models.CharField(max_length=100, default='')
    endereco = models.CharField(max_length=255)
    descricao = models.TextField()
    preco_hora = models.DecimalField(max_digits=10, decimal_places=2)
    locador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campos')

    tipo_gramado = models.CharField(max_length=50, choices=[
        ('natural', 'Natural'),
        ('sintetico', 'Sintético'),
    ], null=True ,blank=True, default='natural',)

    iluminacao = models.BooleanField(default=False)
    vestiarios = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)


    def __str__(self):
        return self.nome

class CampoFoto(models.Model):
    campo = models.ForeignKey(Campo, on_delete=models.CASCADE, related_name='fotos')
    imagem = models.ImageField(upload_to='campo_pictures/')

    def __str__(self):
        return f"Foto de {self.campo.nome}"

class Reserva(models.Model):
    campo = models.ForeignKey(Campo, on_delete=models.CASCADE, related_name='reservas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas')
    data_reserva = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    criado_em = models.DateTimeField(auto_now_add=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bloqueado = models.BooleanField(default=False)
    cancelada = models.BooleanField(default=False)
    

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['campo', 'data_reserva', 'hora_inicio'],
                condition=models.Q(cancelada=False),
                name='unique_reserva_ativa'
            )
        ]

    def __str__(self):
        return f"Reserva de {self.campo.nome} por {self.usuario.username} em {self.data_reserva}"

    def calcular_valor_total(self):
        if not self.hora_inicio or not self.hora_fim:
            return Decimal(0)

        inicio = datetime.combine(datetime.today(), self.hora_inicio)
        fim = datetime.combine(datetime.today(), self.hora_fim)
        
        if fim <= inicio:
            raise ValueError("A hora de fim deve ser após a hora de início")

        duracao = fim - inicio
        duracao_horas = duracao.total_seconds() / 3600
        
        preco_hora_decimal = Decimal(self.campo.preco_hora)
        valor_total = preco_hora_decimal * Decimal(duracao_horas)
        return valor_total
 
 
class ReservaCancelada(models.Model):
    campo = models.ForeignKey(Campo,on_delete=models.CASCADE,related_name='reservas_canceladas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas_canceladas')
    data_reserva = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    criado_em = models.DateTimeField(auto_now_add=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    motivo_cancelamento = models.CharField(max_length=255)
    comentario = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f'Reserva cancelada de {self.campo.nome} por {self.usuario.username} em {self.data_reserva}'

   
class DiaBloqueado(models.Model):
    campo = models.ForeignKey(Campo, on_delete=models.CASCADE, related_name='dias_bloqueados')
    data = models.DateField()

    def __str__(self):
        return f"Dia bloqueado em {self.data} para {self.campo.nome}"


class Comentario(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    campo = models.ForeignKey(Campo ,related_name='comentarios',on_delete=models.CASCADE)
    comentario = models.TextField()
    avaliacao = models.IntegerField(choices=[(i,i) for i in range(1, 6)],default=5)
    data_criacao = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username} - {self.campo.nome} ({self.avaliacao})'