from django.test import TestCase
from django.contrib.auth.models import User
from campos.models import Campo, CampoFoto, Reserva, DiaBloqueado,Comentario
from campos.forms import CampoForm, CampoFotoForm, BuscaCampoForm, ReservaForm, DiaBloqueadoForm,ComentarioForm,FeedBackCancelamentoForm
from decimal import Decimal
from datetime import date, time

class CampoFormTest(TestCase):

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

    def test_valid_form(self):
        form_data = {
            'nome': 'Campo Teste Novo',
            'cidade': 'Nova Cidade',
            'endereco': 'Novo Endereço',
            'descricao': 'Nova Descrição',
            'preco_hora': '150.00',
            'tipo_gramado': 'sintetico',
            'iluminacao': True,
            'vestiarios': False,
            'latitude': '12.345678',
            'longitude': '98.765432'
        }
        form = CampoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'nome': '',
            'cidade': 'Cidade Teste',
            'endereco': 'Endereço Teste',
            'descricao': 'Descrição do Campo Teste',
            'preco_hora': '100.00',
            'tipo_gramado': 'natural',
            'iluminacao': True,
            'vestiarios': False,
            'latitude': '12.345678',
            'longitude': '98.765432'
        }
        form = CampoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['nome'], ['Este campo é obrigatório.'])

    def test_unique_nome_validation(self):
        form_data = {
            'nome': 'Campo Teste',
            'cidade': 'Cidade Teste',
            'endereco': 'Endereço Teste',
            'descricao': 'Descrição do Campo Teste',
            'preco_hora': '100.00',
            'tipo_gramado': 'natural',
            'iluminacao': True,
            'vestiarios': False,
            'latitude': '12.345678',
            'longitude': '98.765432'
        }
        form = CampoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['nome'], ['Já existe um campo com este nome.'])
    
    def test_tipo_gramado_choices(self):
        form_data = {
            'nome': 'Campo Teste Novo',
            'cidade': 'Nova Cidade',
            'endereco': 'Novo Endereço',
            'descricao': 'Nova Descrição',
            'preco_hora': '150.00',
            'tipo_gramado': 'sintetico', 
            'iluminacao': True,
            'vestiarios': False,
            'latitude': '12.345678',
            'longitude': '98.765432'
        }
        form = CampoForm(data=form_data)
        self.assertTrue(form.is_valid())

class CampoFotoFormTest(TestCase):

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

    def test_valid_form(self):
        form_data = {'imagem': 'campo_pictures/path/to/image.jpg'}
        form = CampoFotoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_without_image(self):
        form = CampoFotoForm(data={})
        self.assertTrue(form.is_valid()) 

class BuscaCampoFormTest(TestCase):

    def test_valid_form(self):
        form_data = {
            'q': 'Campo Teste',
            'tipo_gramado': 'natural',
            'iluminacao': True,
            'vestiarios': False,
            'cidade': 'Cidade Teste'
        }
        form = BuscaCampoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form = BuscaCampoForm(data={})
        self.assertTrue(form.is_valid()) 

class ReservaFormTest(TestCase):

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

    def test_valid_form(self):
        form_data = {
            'data_reserva': date(2024, 8, 15),
            'hora_inicio': time(10, 0),
            'hora_fim': time(12, 0)
        }
        form = ReservaForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'data_reserva': '',
            'hora_inicio': '',
            'hora_fim': ''
        }
        form = ReservaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['data_reserva'], ['Este campo é obrigatório.'])
        self.assertEqual(form.errors['hora_inicio'], ['Este campo é obrigatório.'])
        self.assertEqual(form.errors['hora_fim'], ['Este campo é obrigatório.'])

class DiaBloqueadoFormTest(TestCase):

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

    def test_valid_form(self):
        form_data = {
            'campo': self.campo.id,
            'data': date(2024, 8, 15)
        }
        form = DiaBloqueadoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'campo': '',
            'data': ''
        }
        form = DiaBloqueadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['campo'], ['Este campo é obrigatório.'])
        self.assertEqual(form.errors['data'], ['Este campo é obrigatório.'])


class ComentarioFormTest(TestCase):

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

    def test_valid_form(self):
        form_data = {
            'campo': self.campo.id,  
            'comentario': 'Comentário Válido',
            'avaliacao': 4
        }
        form = ComentarioForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'campo': self.campo.id,  
            'comentario': '',  
            'avaliacao': ''    
        }
        form = ComentarioForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['comentario'], ['Este campo é obrigatório.'])
        self.assertEqual(form.errors['avaliacao'], ['Este campo é obrigatório.'])

    def test_avaliacao_choices(self):
        form_data = {
            'campo': self.campo.id,  
            'comentario': 'Comentário com Avaliação',
            'avaliacao': 5
        }
        form = ComentarioForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_avaliacao_invalid_choice(self):
        form_data = {
            'campo': self.campo.id,  
            'comentario': 'Comentário com Avaliação Inválida',
            'avaliacao': 10 
        }
        form = ComentarioForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['avaliacao'], ['Faça uma escolha válida. 10 não é uma das escolhas disponíveis.'])


    def test_form_without_user(self):
        form_data = {
            'campo': self.campo.id,
            'comentario': 'Comentário sem usuário',
            'avaliacao': 3
        }
        form = ComentarioForm(data=form_data)
        form.user = self.user  
        self.assertTrue(form.is_valid())
    


class FeedBackCancelamentoFormTest(TestCase):
    
    def test_valid_form(self):
        
        form_data ={
            'motivos': 'atendimento',
            'comentario': 'Atendimento foi muito ruim'
        }
        form = FeedBackCancelamentoForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_valid_form_without_comentario(self):
        form_data = {
            'motivos': 'atendimento',
            'comentario': ''
        }
        form = FeedBackCancelamentoForm(data=form_data)
        self.assertTrue(form.is_valid())

    
    def test_invalid_form_without_motivo(self):
        form_data = {
            'motivos': '',
            'comentario': 'descreva seu motivo'
        }
        form = FeedBackCancelamentoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['motivos'], ['Este campo é obrigatório.'])


    def test_invalid_choice_for_motivos(self):
        form_data = {
            'motivos': 'motivo_invalido',
            'comentario': 'Motivo inválido escolhido.'
        }
        form = FeedBackCancelamentoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['motivos'], ['Faça uma escolha válida. motivo_invalido não é uma das escolhas disponíveis.'])
    
    
    def test_placeholder_comentario(self):
        form = FeedBackCancelamentoForm()
        self.assertEqual(form.fields['comentario'].widget.attrs['placeholder'], 'Descreva seu motivo (opcional)')