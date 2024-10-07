from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.busca_campos, name='busca_campos'),
    path('SeusCampos/', views.campo_list, name='campo_list'),
    path('NovoCampo/', views.campo_create, name='campo_create'),
    path('<int:pk>/editar/', views.campo_update, name='campo_update'),
    path('<int:pk>/deletar/', views.campo_delete, name='campo_delete'),
    path('campo/<int:campo_id>/reservar', views.reservar_campo, name='reservar_campo'),
    path('bloquear-dia/', views.bloquear_dia, name='bloquear_dia'),
    path('minhas-reservas/', views.minhas_reservas, name='minhas_reservas'),
    path('campo/<int:campo_id>/comentar/', views.comentar_campo, name='comentar_campo'),
    path('comentarios/<int:comentario_id>/deletar/',views.deletar_comentario, name='deletar_comentario'),
    path('export/csv/', views.export_reservas_csv, name='export_reservas_csv'),
    path('export/pdf/',views.exportar_para_pdf, name='exportar_para_pdf' ),
    path('export/pdf/cancelamentos',views.exportar_para_pdf_cancelamentos, name='exportar_para_pdf_cancelamentos' ),
    path('reservas/cancelar/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),




]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
