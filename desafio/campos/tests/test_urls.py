from django.test import SimpleTestCase
from django.urls import reverse, resolve
from campos.views import (busca_campos, campo_list, campo_create, 
                          campo_update, campo_delete, reservar_campo,  
                          bloquear_dia, minhas_reservas, export_reservas_csv,exportar_para_pdf,cancelar_reserva )

class URLTests(SimpleTestCase):
    
    def test_busca_campos_url(self):
        url = reverse('busca_campos')
        self.assertEqual(resolve(url).func, busca_campos)

    def test_campo_list_url(self):
        url = reverse('campo_list')
        self.assertEqual(resolve(url).func, campo_list)

    def test_campo_create_url(self):
        url = reverse('campo_create')
        self.assertEqual(resolve(url).func, campo_create)

    def test_campo_update_url(self):
        url = reverse('campo_update', args=[1])
        self.assertEqual(resolve(url).func, campo_update)

    def test_campo_delete_url(self):
        url = reverse('campo_delete', args=[1])
        self.assertEqual(resolve(url).func, campo_delete)

    def test_reservar_campo_url(self):
        url = reverse('reservar_campo', args=[1])
        self.assertEqual(resolve(url).func, reservar_campo)

    def test_bloquear_dia_url(self):
        url = reverse('bloquear_dia')
        self.assertEqual(resolve(url).func, bloquear_dia)

    def test_minhas_reservas_url(self):
        url = reverse('minhas_reservas')
        self.assertEqual(resolve(url).func, minhas_reservas)
        
    
    def test_export_reservas_csv(self):
        url = reverse('export_reservas_csv')
        self.assertEqual(resolve(url).func, export_reservas_csv)

    def test_exportar_para_pdf(self):
        url = reverse('exportar_para_pdf')
        self.assertEqual(resolve(url).func, exportar_para_pdf)

    def test_cancelar_reservas(self):
        url = reverse('cancelar_reserva', args=[1])
        self.assertEqual(resolve(url).func, cancelar_reserva)