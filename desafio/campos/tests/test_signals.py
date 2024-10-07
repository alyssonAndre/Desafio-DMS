from django.test import TestCase
from unittest.mock import patch
from campos.models import Comentario, Campo
from django.contrib.auth.models import User

class ComentarioSignalTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', password='password')
        self.campo = Campo.objects.create(
            nome='Campo Teste',
            cidade='Cidade Teste',
            endereco='Endereço Teste',
            descricao='Descrição Teste',
            preco_hora=100.00,
            tipo_gramado='Grama',
            iluminacao=True,
            vestiarios=True,
            latitude=0.0,
            longitude=0.0,
            locador=self.user
        )

    @patch('campos.views.enviar_resumo_feedback')
    def test_comentario_salvo_signal(self, mock_enviar_resumo_feedback):
        Comentario.objects.create(
            user=self.user,
            campo=self.campo,
            comentario='Comentário Teste',
            avaliacao=5
        )

