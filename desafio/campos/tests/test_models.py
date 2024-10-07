from django.test import TestCase
from django.contrib.auth.models import User
from campos.models import Campo, CampoFoto, Reserva, DiaBloqueado,Comentario
from decimal import Decimal
from django.utils import timezone
from datetime import date, time, timedelta


class CampoModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.campo = Campo.objects.create(
            nome='Campo Teste',
            cidade='Cidade Teste',
            endereco='Endereço Teste',
            descricao='Descrição do Campo Teste',
            preco_hora=Decimal('100.00'),
            locador=self.user,
            tipo_gramado='natural',
            iluminacao=True,
            vestiarios=True,
            latitude=Decimal('12.345678'),
            longitude=Decimal('98.765432')
        )

    def test_campo_creation(self):
        campo = Campo.objects.get(nome='Campo Teste')
        self.assertEqual(campo.nome, 'Campo Teste')
        self.assertEqual(campo.cidade, 'Cidade Teste')
        self.assertEqual(campo.endereco, 'Endereço Teste')
        self.assertEqual(campo.descricao, 'Descrição do Campo Teste')
        self.assertEqual(campo.preco_hora, Decimal('100.00'))
        self.assertEqual(campo.locador, self.user)
        self.assertEqual(campo.tipo_gramado, 'natural')
        self.assertTrue(campo.iluminacao)
        self.assertTrue(campo.vestiarios)
        self.assertEqual(campo.latitude, Decimal('12.345678'))
        self.assertEqual(campo.longitude, Decimal('98.765432'))

    def test_campo_str(self):
        self.assertEqual(str(self.campo), 'Campo Teste')
    
    def test_campo_creation_with_default_tipo_gramado(self):
        campo = Campo.objects.create(
            nome='Campo Teste Default Tipo',
            cidade='Cidade Teste',
            endereco='Endereço Teste',
            descricao='Descrição do Campo Teste',
            preco_hora=Decimal('100.00'),
            locador=self.user
        )
        self.assertEqual(campo.tipo_gramado, 'natural')

    def test_campo_creation_with_blank_tipo_gramado(self):
        campo = Campo.objects.create(
            nome='Campo Teste Blank Tipo',
            cidade='Cidade Teste',
            endereco='Endereço Teste',
            descricao='Descrição do Campo Teste',
            preco_hora=Decimal('100.00'),
            locador=self.user,
            tipo_gramado=''
        )
        self.assertEqual(campo.tipo_gramado, '')

class CampoFotoModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.campo = Campo.objects.create(
            nome='Campo Teste',
            cidade='Cidade Teste',
            endereco='Endereço Teste',
            descricao='Descrição do Campo Teste',
            preco_hora=Decimal('100.00'),
            locador=self.user
        )
        self.campo_foto = CampoFoto.objects.create(
            campo=self.campo,
            imagem='campo_pictures/path/to/image.jpg'
        )

    def test_campo_foto_creation(self):
        campo_foto = CampoFoto.objects.get(campo=self.campo)
        self.assertEqual(campo_foto.campo, self.campo)
        self.assertEqual(campo_foto.imagem, 'campo_pictures/path/to/image.jpg')

    def test_campo_foto_str(self):
        self.assertEqual(str(self.campo_foto), 'Foto de Campo Teste')

class ReservaModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.campo = Campo.objects.create(
            nome='Campo Teste',
            cidade='Cidade Teste',
            endereco='Endereço Teste',
            descricao='Descrição do Campo Teste',
            preco_hora=Decimal('100.00'),
            locador=self.user
        )
        self.reserva = Reserva.objects.create(
            campo=self.campo,
            usuario=self.user,
            data_reserva=date(2024, 8, 15),
            hora_inicio=time(10, 0),
            hora_fim=time(12, 0)
        )
        self.reserva.valor_total = self.reserva.calcular_valor_total()
        self.reserva.save()

    def test_reserva_creation(self):
        reserva = Reserva.objects.get(campo=self.campo)
        self.assertEqual(reserva.campo, self.campo)
        self.assertEqual(reserva.usuario, self.user)
        self.assertEqual(reserva.data_reserva, date(2024, 8, 15))
        self.assertEqual(reserva.hora_inicio, time(10, 0))
        self.assertEqual(reserva.hora_fim, time(12, 0))
        self.assertEqual(reserva.valor_total, Decimal('200.00'))
        self.assertFalse(reserva.cancelada)
    
    def test_reserva_cancelada(self):
        self.reserva.cancelada = True
        self.reserva.save()
        reserva = Reserva.objects.get(pk=self.reserva.pk)
        self.assertTrue(reserva.cancelada) 
    
    def test_calcular_valor_total(self):
        self.assertEqual(self.reserva.calcular_valor_total(), Decimal('200.00'))

    def test_calcular_valor_total_invalid_time(self):
        reserva = Reserva(campo=self.campo, usuario=self.user, data_reserva=date(2024, 8, 15), hora_inicio=time(12, 0), hora_fim=time(10, 0))
        with self.assertRaises(ValueError):
            reserva.calcular_valor_total()

    def test_reserva_str(self):
        self.assertEqual(str(self.reserva), 'Reserva de Campo Teste por testuser em 2024-08-15')

class DiaBloqueadoModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.campo = Campo.objects.create(
            nome='Campo Teste',
            cidade='Cidade Teste',
            endereco='Endereço Teste',
            descricao='Descrição do Campo Teste',
            preco_hora=Decimal('100.00'),
            locador=self.user
        )
        self.dia_bloqueado = DiaBloqueado.objects.create(
            campo=self.campo,
            data=date(2024, 8, 15)
        )

    def test_dia_bloqueado_creation(self):
        dia_bloqueado = DiaBloqueado.objects.get(campo=self.campo)
        self.assertEqual(dia_bloqueado.campo, self.campo)
        self.assertEqual(dia_bloqueado.data, date(2024, 8, 15))

    def test_dia_bloqueado_str(self):
        self.assertEqual(str(self.dia_bloqueado), 'Dia bloqueado em 2024-08-15 para Campo Teste')


class ComentarioModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.campo = Campo.objects.create(
            nome='Campo Teste',
            cidade='Cidade Teste',
            endereco='Endereço Teste',
            descricao='Descrição do Campo Teste',
            preco_hora=100.00,
            locador=self.user,
            tipo_gramado='natural',
            iluminacao=True,
            vestiarios=True,
            latitude=Decimal('12.345678'),
            longitude=Decimal('98.765432')
        )
        self.comentario = Comentario.objects.create(
            user=self.user,
            campo=self.campo,
            comentario='Comentário de Teste',
            avaliacao=4,
            data_criacao=timezone.now() 
        )

    def test_comentario_creation(self):
        self.assertEqual(self.comentario.user, self.user)
        self.assertEqual(self.comentario.campo, self.campo)
        self.assertEqual(self.comentario.comentario, 'Comentário de Teste')
        self.assertEqual(self.comentario.avaliacao, 4)
        self.assertTrue(self.comentario.data_criacao.tzinfo is not False)

    def test_comentario_str(self):
        expected_str = f'{self.user.username} - {self.campo.nome} ({self.comentario.avaliacao})'
        self.assertEqual(str(self.comentario), expected_str)

    def test_comentario_data_criacao(self):
        now = timezone.now()
        delta = timedelta(seconds=10)
        self.assertTrue(self.comentario.data_criacao <= now)
        self.assertTrue(self.comentario.data_criacao >= now - delta)