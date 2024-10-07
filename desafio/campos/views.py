import csv
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponseNotAllowed
from .models import Campo, CampoFoto, Reserva, DiaBloqueado,Comentario,ReservaCancelada
from .forms import CampoForm, CampoFotoFormSet, BuscaCampoForm, ReservaForm, DiaBloqueadoForm,ComentarioForm,FeedBackCancelamentoForm
from usuarios.decorators import locador_required
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from usuarios.tasks import send_mail_task
from collections import defaultdict



@login_required
@locador_required
def campo_list(request):
    campos = Campo.objects.filter(locador=request.user)
    return render(request, 'campos/campos_list.html', {'campos': campos})



@login_required
@locador_required
def campo_create(request):
    if request.method == 'POST':
        campo_form = CampoForm(request.POST, request.FILES)
        formset = CampoFotoFormSet(request.POST, request.FILES)

        if campo_form.is_valid() and formset.is_valid():
            campo = campo_form.save(commit=False)

            if campo.tipo_gramado == '':
                campo.tipo_gramado = None

            campo.locador = request.user
            campo.save()

            for form in formset:
                if form.cleaned_data.get('DELETE'):
                    if form.instance.pk:
                        form.instance.delete()
                elif form.cleaned_data.get('imagem'):
                    imagem = form.cleaned_data.get('imagem')
                    if not CampoFoto.objects.filter(campo=campo, imagem=imagem).exists():
                        CampoFoto.objects.create(campo=campo, imagem=imagem)

            return redirect('campo_list')
        else:
            print("Form errors:", campo_form.errors)
            print("Formset errors:", formset.errors)
    else:
        campo_form = CampoForm()
        formset = CampoFotoFormSet(queryset=CampoFoto.objects.none())

    return render(request, 'campos/campos_form.html', {
        'campo_form': campo_form,
        'formset': formset,
    })



@login_required
@locador_required
def campo_update(request, pk):
    campo = get_object_or_404(Campo, pk=pk, locador=request.user)

    if request.method == 'POST':
        campo_form = CampoForm(request.POST, request.FILES, instance=campo)
        formset = CampoFotoFormSet(
            request.POST, request.FILES, queryset=CampoFoto.objects.filter(campo=campo))

        if campo_form.is_valid() and formset.is_valid():
            campo = campo_form.save(commit=False)

            # Verifica se o tipo_gramado é uma string vazia
            if campo.tipo_gramado == '':
                campo.tipo_gramado = None

            campo.save()

            for form in formset:
                if form.cleaned_data.get('DELETE'):
                    if form.instance.pk:
                        form.instance.delete()
                elif form.cleaned_data.get('imagem'):
                    imagem = form.cleaned_data.get('imagem')
                    if not CampoFoto.objects.filter(campo=campo, imagem=imagem).exists():
                        CampoFoto.objects.create(
                            campo=campo, imagem=imagem)

            return redirect('campo_list')
        else:
            print("Form errors:", campo_form.errors)
            print("Formset errors:", formset.errors)
    else:
        campo_form = CampoForm(instance=campo)
        formset = CampoFotoFormSet(queryset=CampoFoto.objects.filter(
            campo=campo))

    return render(request, 'campos/campos_form.html', {'campo_form': campo_form, 'formset': formset})


@login_required
@locador_required
def campo_delete(request, pk):
    campo = get_object_or_404(Campo, pk=pk, locador=request.user)

    if request.method == 'POST':
        campo.delete()
        return redirect('campo_list')

    elif request.method == 'GET':
        return render(request, 'campos/campos_confirm_delete.html', {'campo': campo})

    return HttpResponseNotAllowed(['GET', 'POST'])

@login_required
def busca_campos(request):
    query = request.GET.get('q', '')
    tipo_gramado = request.GET.get('tipo_gramado', '')
    iluminacao = request.GET.get('iluminacao', False)
    vestiarios = request.GET.get('vestiarios', False)
    cidade = request.GET.get('cidade', '')

    campos = Campo.objects.all()

    if query:
        campos = campos.filter(
            Q(nome__icontains=query) |
            Q(endereco__icontains=query) |
            Q(descricao__icontains=query) |
            Q(cidade__icontains=query) 
            
        )

    if tipo_gramado:
        campos = campos.filter(tipo_gramado=tipo_gramado)

    if iluminacao:
        campos = campos.filter(iluminacao=True)

    if vestiarios:
        campos = campos.filter(vestiarios=True)

    if cidade:
        campos = campos.filter(cidade__icontains=cidade)

    campos = campos.order_by('nome')
    

    context = {
        'campos': campos,
        'query': query,
        'tipo_gramado': tipo_gramado,
        'iluminacao': iluminacao,
        'vestiarios': vestiarios,
        'cidade': cidade,
    }

    return render(request, 'campos/buscar_campos.html', context)

@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    campo = reserva.campo  
    
    if request.method == 'POST':
        feedback_form = FeedBackCancelamentoForm(request.POST)
        
        if feedback_form.is_valid():
            ReservaCancelada.objects.create(
                campo=reserva.campo,
                usuario=reserva.usuario,
                data_reserva=reserva.data_reserva,
                hora_inicio= reserva.hora_inicio,
                hora_fim=reserva.hora_fim,
                valor_total=reserva.valor_total,
                motivo_cancelamento=feedback_form.cleaned_data['motivos'],
                comentario= feedback_form.cleaned_data['comentario']
            )
            
            reserva.delete()
            
            send_mail_task.delay(
                'Feedback sobre Cancelamento de Reserva',
                f'O usuário {request.user.username} cancelou a reserva e deixou o seguinte feedback:\n\n'
                f'Motivo: {feedback_form.cleaned_data["motivos"]}\n'
                f'Comentário: {feedback_form.cleaned_data["comentario"]}',
                [campo.locador.email]  
            )
            
            send_mail_task.delay(
                'Obrigado pelo seu Feedback',
                'Sua reserva foi cancelada e agradecemos seu feedback.',
                [request.user.email]
            )
            
            messages.success(request, 'Reserva cancelada com sucesso!')
            return redirect('minhas_reservas')
    else:
        feedback_form = FeedBackCancelamentoForm()

    return render(request, 'campos/cancelar_reserva.html', {
        'reserva': reserva,
        'feedback_form': feedback_form
    })

@login_required
def reservar_campo(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id)

    if request.method == 'POST':
        reserva_form = ReservaForm(request.POST)
        if reserva_form.is_valid():
            data_reserva = reserva_form.cleaned_data['data_reserva']
            hora_inicio = reserva_form.cleaned_data['hora_inicio']
            hora_fim = reserva_form.cleaned_data['hora_fim']
            usuario = request.user

            # Verifica se o dia está bloqueado
            if DiaBloqueado.objects.filter(campo=campo, data=data_reserva).exists():
                messages.error(request, 'Este dia está bloqueado para reservas.')
                return _render_reserva_form(request, campo, reserva_form)

            # Verifica se o horário está bloqueado
            if Reserva.objects.filter(campo=campo, data_reserva=data_reserva, hora_inicio=hora_inicio, bloqueado=True).exists():
                messages.error(request, 'Esse horário está bloqueado.')
                return _render_reserva_form(request, campo, reserva_form)

            # Lógica de cancelamento: impede nova reserva do mesmo campo 1 hora após um cancelamento
            uma_hora_atras = timezone.now() - timedelta(hours=1)
            reservas_canceladas = ReservaCancelada.objects.filter(
                usuario=usuario,
                campo=campo,
                criado_em__gte=uma_hora_atras  # Verifica se foi cancelada na última hora
            )
            
            if reservas_canceladas.exists():
                messages.error(request, 'Você só pode fazer uma nova reserva 1 hora após o cancelamento anterior deste campo.')
                return _render_reserva_form(request, campo, reserva_form)

            # Tenta encontrar uma reserva existente
            reserva_existente = Reserva.objects.filter(
                campo=campo, 
                data_reserva=data_reserva, 
                hora_inicio=hora_inicio, 
                hora_fim=hora_fim, 
                cancelada=False
            ).first()

            if reserva_existente:
                # Atualiza o usuário da reserva existente
                reserva_existente.usuario = usuario
                reserva_existente.save()
                messages.success(request, 'Reserva atualizada com sucesso.')
            else:
                # Cria a nova reserva
                reserva = reserva_form.save(commit=False)
                reserva.campo = campo
                reserva.usuario = usuario
                reserva.valor_total = reserva.calcular_valor_total()
                reserva.save()
                
                enviar_email_reserva(reserva)
                messages.success(request, 'Reserva realizada com sucesso.')
                
            return redirect('busca_campos')

    else:
        reserva_form = ReservaForm()

    return _render_reserva_form(request, campo, reserva_form)


def _render_reserva_form(request, campo, form=None):
    """
    Helper function to render the reservation form.
    """
    if form is None:
        form = ReservaForm()
    return render(request, 'campos/reservar_campo.html', {
        'campo': campo,
        'preco_hora': campo.preco_hora,
        'form': form,
    })


@login_required
@locador_required
def bloquear_dia(request):
    if request.method == 'POST':
        form = DiaBloqueadoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dia bloqueado com sucesso.')
            return redirect('busca_campos')
    else:
        form = DiaBloqueadoForm()

    return render(request, 'campos/bloquear_dia.html', {'form': form})


@login_required
def minhas_reservas(request):
    reservas = Reserva.objects.filter(usuario=request.user, cancelada=False).order_by('-data_reserva', '-hora_inicio')
    return render(request, 'campos/minhas_reservas.html', {'reservas': reservas})



@login_required
def comentar_campo(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id)
    
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.user = request.user
            comentario.campo = campo
            comentario.save()
            return redirect('busca_campos')
    else:
        form = ComentarioForm()
    
    comentarios = Comentario.objects.filter(campo=campo)
    
    return render(request, 'campos/comentar_campo.html', {
        'form': form,
        'campo': campo,
        'comentarios': comentarios
    })    
    

def enviar_resumo_feedback():
    data_limite = datetime.now() - timedelta(days=1)
    comentarios = Comentario.objects.filter(data_criacao__gte=data_limite)

    feedback_resumo = defaultdict(list)  
    for comentario in comentarios:
        dono_campo = comentario.campo.locador
        email = dono_campo.email

        # Ignora e-mails de teste
        if email == 'aaa@gmail.com':
            continue

        feedback_resumo[email].append(f'Campo: {comentario.campo.nome}\nComentário: {comentario.comentario}')

    for email, comentarios in feedback_resumo.items():
        subject = 'Resumo de Feedback'
        message = f'Você recebeu os seguintes comentários:\n\n' + '\n\n'.join(comentarios)
        send_mail_task.delay(subject, message, [email])  
        
def enviar_email_reserva(reserva):
    email_dono = reserva.campo.locador.email
    assunto_dono = 'Nova Reserva Confirmada'
    mensagem_dono = (f'O campo {reserva.campo.nome} foi reservado para {reserva.data_reserva} '
                     f'das {reserva.hora_inicio} às {reserva.hora_fim} por {reserva.usuario.username}')
    
    send_mail_task.delay(assunto_dono, mensagem_dono, [email_dono])  
    
    email_usuario = reserva.usuario.email
    assunto_usuario = 'Reserva Confirmada'
    mensagem_usuario = (f'Sua reserva do campo {reserva.campo.nome} para {reserva.data_reserva} '
                        f'das {reserva.hora_inicio} às {reserva.hora_fim} foi confirmada.')
    
    send_mail_task.delay(assunto_usuario, mensagem_usuario, [email_usuario])  

    
def deletar_comentario(request,comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id)
    
    
    if comentario.campo.locador != request.user:
        messages.error(request, 'Você não tem permissão para deletar este comentário.')
        return redirect('busca_campos')
    
    comentario.delete()
    messages.success(request, 'Comentário deletado com sucesso')
    return redirect('busca_campos')

@login_required
@locador_required
def export_reservas_csv(request):
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


@login_required
@locador_required
def exportar_para_pdf(request):
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


@login_required
@locador_required
def exportar_para_pdf_cancelamentos(request):
    dono_campo = request.user 
    queryset = ReservaCancelada.objects.filter(campo__locador=dono_campo)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ReservasCanceladas.pdf"'
    

    p = canvas.Canvas(response)
    y = 800
    x = 100
    p.setFont('Helvetica', 12)

    prejuizo_total = sum(reserva.valor_total for reserva in queryset)


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
        p.drawString(x, y, f"Motivo do Cancelamento: {reserva.motivo_cancelamento}")  
        y -= 20
        p.drawString(x, y, f"Comentário: {reserva.comentario}")  
        y -= 40

        
        if y < 50:
            p.showPage()
            y = 800
    
    p.setFont('Helvetica-Bold', 14)
    p.drawString(x, y, f"Prejuízo Total: R$ {prejuizo_total:.2f}")
    

    p.save()
    return response