from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from campos.models import Campo, Reserva, DiaBloqueado,Comentario,ReservaCancelada
from usuarios.models import UserProfile
from datetime import datetime, time,timedelta
from django.utils import timezone
from decimal import Decimal
from django.utils import timezone


class CampoViewsTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user)
        self.user_profile.is_locador = True
        self.user_profile.save()
        self.client.login(username='testuser', password='12345')
        self.campo = Campo.objects.create(
            nome='Campo Teste',
            cidade='Cidade Teste',
            endereco='Endereço Teste',
            descricao='Descrição Teste',
            preco_hora=Decimal('50.00'),
            locador=self.user,
            tipo_gramado='natural',
            iluminacao=True,
            vestiarios=True,
            latitude=Decimal('12.345678'),
            longitude=Decimal('98.765432')
        )
        self.url = reverse('campo_delete', args=[self.campo.pk]) 

    def test_campo_list_view(self):
        response = self.client.get(reverse('campo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'campos/campos_list.html')
        self.assertContains(response, 'Campo Teste')

        
    def test_campo_create_view(self):
        data = {
            'nome': 'Campo Teste',
            'cidade': 'Cidade Teste',
            'endereco': 'Endereço Teste',
            'descricao': 'Descrição Teste',
            'preco_hora': '50.00',
            'tipo_gramado': 'natural',
            'iluminacao': True,
            'vestiarios': True,
            'latitude': '12.345678',
            'longitude': '98.765432'
        }
        response = self.client.post(reverse('campo_create'), data)
        print("Response status code:", response.status_code)
        print("Form errors:", response.context['campo_form'].errors)
        print("Formset errors:", response.context['formset'].errors)
        
        try:
            campo = Campo.objects.get(nome='Campo Teste')
            print("Campo created:", campo)
        except Campo.DoesNotExist:
            print("Campo with 'Campo Teste' does not exist.")
        
        self.assertTrue(Campo.objects.filter(nome='Campo Teste').exists())



    def test_campo_delete_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'campos/campos_confirm_delete.html')
        self.assertContains(response, self.campo.nome)

    def test_campo_delete_view_post(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)  
        self.assertFalse(Campo.objects.filter(pk=self.campo.pk).exists())

    def test_campo_delete_view_invalid_method(self):
        response = self.client.put(self.url)  
        self.assertEqual(response.status_code, 405)


    def test_reservar_campo_view_invalid_data(self):
        data = {
            'data_reserva': '',
            'hora_inicio': '',
            'hora_fim': '',
        }
        response = self.client.post(reverse('reservar_campo', args=[self.campo.pk]), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Este campo é obrigatório.')

    def test_minhas_reservas_view(self):
        Reserva.objects.create(
            campo=self.campo,
            usuario=self.user,
            data_reserva=datetime.today().date(),
            hora_inicio=time(10, 0),
            hora_fim=time(12, 0),
            valor_total=Decimal('100.00')
        )
        response = self.client.get(reverse('minhas_reservas'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'campos/minhas_reservas.html')
        self.assertContains(response, 'Campo Teste')

    def test_bloquear_dia_view(self):
        data = {
            'campo': self.campo.pk,
            'data': datetime.today().date()
        }
        response = self.client.post(reverse('bloquear_dia'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(DiaBloqueado.objects.filter(campo=self.campo, data=data['data']).exists())

    def test_busca_campos_view(self):
        response = self.client.get(reverse('busca_campos') + '?q=Campo Teste')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'campos/buscar_campos.html')
        self.assertContains(response, 'Campo Teste')

    def test_busca_campos_view_with_filters(self):
        response = self.client.get(reverse('busca_campos') + '?cidade=Cidade Teste&tipo_gramado=natural&iluminacao=True&vestiarios=True')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'campos/buscar_campos.html')
        self.assertContains(response, 'Campo Teste')

    def test_campo_create_view_invalid_data(self):
        data = {
            'nome': '',
            'cidade': '',
            'endereco': '',
            'descricao': '',
            'preco_hora': '',
            'tipo_gramado': '',
            'iluminacao': False,
            'vestiarios': False,
            'latitude': '',
            'longitude': ''
        }
        response = self.client.post(reverse('campo_create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Este campo é obrigatório.')

    def test_campo_update_view_invalid_data(self):
        data = {
            'nome': '',
            'cidade': '',
            'endereco': '',
            'descricao': '',
            'preco_hora': '',
            'tipo_gramado': '',
            'iluminacao': False,
            'vestiarios': False,
            'latitude': '',
            'longitude': ''
        }
        response = self.client.post(reverse('campo_update', args=[self.campo.pk]), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Este campo é obrigatório.')

    def test_bloquear_dia_view_invalid_data(self):
        data = {
            'campo': self.campo.pk,
            'data': ''
        }
        response = self.client.post(reverse('bloquear_dia'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Este campo é obrigatório.')
        
        

    def test_comentar_campo_view_get(self):
        response = self.client.get(reverse('comentar_campo', args=[self.campo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'campos/comentar_campo.html')
        self.assertContains(response, 'Comentário')


    def test_comentar_campo_view_post_invalid(self):
        data = {
            'comentario': '',
            'avaliacao': 10
        }
        response = self.client.post(reverse('comentar_campo', args=[self.campo.id]), data)

        self.assertEqual(response.status_code, 200)

        form = response.context.get('form')
        self.assertIsNotNone(form)

        self.assertTrue(form.errors)
        self.assertIn('avaliacao', form.errors)
        self.assertEqual(form.errors['avaliacao'], ['Faça uma escolha válida. 10 não é uma das escolhas disponíveis.'])




    def test_deletar_comentario_view(self):
        comentario = Comentario.objects.create(
            user=self.user,
            campo=self.campo,
            comentario='Comentário para deletar',
            avaliacao=3,
            data_criacao=timezone.now()
        )
        response = self.client.post(reverse('deletar_comentario', args=[comentario.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comentario.objects.filter(id=comentario.id).exists())
        self.assertRedirects(response, reverse('busca_campos'))
    
    def test_deletar_comentario_view_permission(self):
        other_user = User.objects.create_user(username='otheruser', password='12345')
        comentario = Comentario.objects.create(
            user=other_user,
            campo=self.campo,
            comentario='Comentário de outro usuário',
            avaliacao=2,
            data_criacao=timezone.now()
        )
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('deletar_comentario', args=[comentario.id]))

        self.assertEqual(response.status_code, 302)

        self.assertFalse(Comentario.objects.filter(id=comentario.id).exists())


    def test_export_reservas_csv(self):
        from django.http import HttpResponse

        Reserva.objects.create(
            campo=self.campo,
            usuario=self.user,
            data_reserva=datetime.today().date(),
            hora_inicio=time(10, 0),
            hora_fim=time(12, 0),
            valor_total=Decimal('100.00')
        )

        response = self.client.get(reverse('export_reservas_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertTrue(response.content.decode('utf-8').startswith('Campo,Cidade,Usuário,Data,Hora de Início,Hora de Fim,Valor Total'))

    def test_exportar_para_pdf(self):
        from django.http import HttpResponse
        from io import BytesIO
        from reportlab.pdfgen import canvas

        Reserva.objects.create(
            campo=self.campo,
            usuario=self.user,
            data_reserva=datetime.today().date(),
            hora_inicio=time(10, 0),
            hora_fim=time(12, 0),
            valor_total=Decimal('100.00')
        )

        response = self.client.get(reverse('exportar_para_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response['Content-Disposition'].startswith('attachment; filename="reservas.pdf"'))

    def test_reserva_dia_bloqueado(self):
        DiaBloqueado.objects.create(campo=self.campo, data=datetime.today().date())

        data = {
            'data_reserva': datetime.today().date(),
            'hora_inicio': time(10, 0),
            'hora_fim': time(12, 0),
        }
        response = self.client.post(reverse('reservar_campo', args=[self.campo.pk]), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Este dia está bloqueado para reservas.')

    def test_reserva_horario_bloqueado(self):
        Reserva.objects.create(
            campo=self.campo,
            usuario=self.user,
            data_reserva=datetime.today().date(),
            hora_inicio=time(10, 0),
            hora_fim=time(12, 0),
            bloqueado=True
        )

        data = {
            'data_reserva': datetime.today().date(),
            'hora_inicio': time(10, 0),
            'hora_fim': time(12, 0),
        }
        response = self.client.post(reverse('reservar_campo', args=[self.campo.pk]), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Esse horário está bloqueado.')

    
    def test_reserva_atualizar_reserva_existente(self):
        reserva_existente = Reserva.objects.create(
            campo = self.campo,
            usuario = self.user,
            data_reserva=datetime.today().date(),
            hora_inicio = time(10, 0),
            hora_fim = time(12, 0),
            valor_total = Decimal('100.00')
        )
        
        data = {
            'data_reserva': reserva_existente.data_reserva,
            'hora_inicio': reserva_existente.hora_inicio,
            'hora_fim': reserva_existente.hora_fim,
        }
        response = self.client.post(reverse('reservar_campo', args=[self.campo.pk]), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Reserva.objects.get(pk=reserva_existente.pk).usuario, self.user)
    
    
    def test_reserva_bloqueio_apos_cancelamento(self):
        reserva_cancelada = Reserva.objects.create(
            campo=self.campo,
            usuario=self.user,
            data_reserva=datetime.today().date(),
            hora_inicio=time(10, 0),
            hora_fim=time(12, 0),
            cancelada=False  
        )

        ReservaCancelada.objects.create(
            campo=reserva_cancelada.campo,
            usuario=reserva_cancelada.usuario,
            data_reserva=reserva_cancelada.data_reserva,
            hora_inicio=reserva_cancelada.hora_inicio,
            hora_fim=reserva_cancelada.hora_fim,
            valor_total=reserva_cancelada.valor_total,
            motivo_cancelamento="Motivo do cancelamento",
            comentario="Comentário sobre o cancelamento",
            criado_em=timezone.now()  
        )

        reserva_cancelada.delete()

        data = {
            'data_reserva': datetime.today().date(),
            'hora_inicio': time(10, 0),
            'hora_fim': time(12, 0),
        }

        response = self.client.post(reverse('reservar_campo', args=[self.campo.pk]), data)
        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, 'Você só pode fazer uma nova reserva 1 hora após o cancelamento anterior deste campo')



    def test_reserva_criar_nova(self):
        data = {
            
            'data_reserva': datetime.today().date(),
            'hora_inicio': time(10, 0),
            'hora_fim': time( 12, 0),
            
        }
        
        response = self.client.post(reverse('reservar_campo', args=[self.campo.pk]),data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Reserva.objects.filter(campo=self.campo, data_reserva=data['data_reserva']).exists())