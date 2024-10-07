from django.contrib import admin
from .models import Campo, CampoFoto, Reserva,DiaBloqueado,Comentario,ReservaCancelada
from reportlab.pdfgen import canvas
from django.http import HttpResponse
import csv

class CampoFotoInline(admin.TabularInline):
    model = CampoFoto
    extra = 1

class CampoAdmin(admin.ModelAdmin):
    inlines = [CampoFotoInline]

class ReservaAdmin(admin.ModelAdmin):
    list_display = ('campo', 'usuario', 'data_reserva', 'hora_inicio', 'hora_fim', 'valor_total', 'bloqueado', 'criado_em')
    list_filter = ('campo', 'usuario', 'data_reserva', 'bloqueado') 
    search_fields = ('campo__nome', 'usuario__username', 'data_reserva')
    actions = ['bloquear_horario', 'desbloquear_horario', 'exportar_para_pdf', 'exportar_para_csv']


    def bloquear_horario(self, request, queryset):
        queryset.update(bloqueado=True)
        self.message_user(request, "Horários selecionados foram bloqueados com sucesso.")

    def desbloquear_horario(self, request, queryset):
        queryset.update(bloqueado=False)
        self.message_user(request, "Horários selecionados foram desbloqueados com sucesso.")

    bloquear_horario.short_description = "Bloquear horário(s) selecionado(s)"
    desbloquear_horario.short_description = "Desbloquear horário(s) selecionado(s)"

    def exportar_para_pdf(self,request,queryset):
        dono_campo = request.user 
        queryset = Reserva.objects.filter(campo__locador=dono_campo)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reservas.pdf"'


        p = canvas.Canvas(response)
        y = 800
        x = 100
        p.setFont('Helvetica', 12)

        for reserva in queryset:
            p.drawString(x, y, f"Campo: {reserva.campo.nome}")
            y -= 20
            p.drawString(x, y, f"Usuário: {reserva.usuario.username}")
            y -= 20
            p.drawString(x, y, f"Data da Reserva: {reserva.data_reserva}")
            y -= 20
            p.drawString(x, y, f"Hora de Início: {reserva.hora_inicio}")
            y -= 20
            p.drawString(x, y, f"Hora de Fim: {reserva.hora_fim}")
            y -= 20
            p.drawString(x, y, f"Valor Total: R$ {reserva.valor_total}")
            y -= 40

            if y < 50:
                p.showPage()
                y = 800

        p.save()
        return response

    exportar_para_pdf.short_description = 'Exportar Selecionados para PDF'
    
    def exportar_para_csv(self,request,queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reservas.csv"'

        writer = csv.writer(response)
        writer.writerow(['Campo', 'Cidade', 'Usuário', 'Data', 'Hora de Início', 'Hora de Fim', 'Valor Total'])

        dono_campo = request.user 

        reservas = Reserva.objects.filter(campo__locador=dono_campo).values_list(
            'campo__nome',
            'campo__cidade',
            'usuario__username',
            'data_reserva',
            'hora_inicio',
            'hora_fim',
            'valor_total'
        )

        if not reservas:
            print("Nenhuma reserva encontrada para os campos do dono:", dono_campo.username)

        for reserva in reservas:
            writer.writerow(reserva)

        return response


    exportar_para_csv.short_description = "Exportar Selecionados para CSV"

class DiaBloqueadoAdmin(admin.ModelAdmin):
    list_display = ('campo', 'data')
    list_filter = ('campo', 'data')
    search_fields = ('campo__nome', 'data')


class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'campo', 'avaliacao', 'data_criacao')
    list_filter = ('campo', 'avaliacao', 'data_criacao')
    search_fields = ('user__username', 'campo__nome', 'comentario')
    readonly_fields = ('data_criacao',)
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class ReservaCanceladaAdmin(admin.ModelAdmin):
    list_display = ('campo','usuario','data_reserva','hora_inicio','hora_fim','motivo_cancelamento','comentario','criado_em')
    search_fields = ('campo__nome', 'usuario__username', 'motivo_cancelamento')
    list_filter = ('campo', 'data_reserva', 'motivo_cancelamento', 'criado_em')

admin.site.register(Campo, CampoAdmin)
admin.site.register(CampoFoto)
admin.site.register(Reserva, ReservaAdmin)
admin.site.register(DiaBloqueado, DiaBloqueadoAdmin)
admin.site.register(Comentario, ComentarioAdmin)
admin.site.register(ReservaCancelada, ReservaCanceladaAdmin)
