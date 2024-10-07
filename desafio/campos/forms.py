from django import forms
from .models import Campo, CampoFoto, Reserva, DiaBloqueado,Comentario
from django.forms import modelformset_factory


class CampoForm(forms.ModelForm):
    tipo_gramado = forms.ChoiceField(
    choices=[('', 'Escolha o tipo de gramado'), ('natural', 'Natural'), ('sintetico', 'Sintético')],
    required=False
    )
    class Meta:
        model = Campo
        fields = ['nome', 'endereco', 'descricao', 'preco_hora', 'tipo_gramado', 'iluminacao', 'vestiarios', 'cidade', 'latitude', 'longitude']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['preco_hora'].widget = forms.TextInput(attrs={
            'placeholder': 'O preço por hora deve ser no mínimo R$ 1,00.',
            'id': 'id_preco_hora'
        })
        self.fields['latitude'].widget = forms.TextInput(attrs={
            'placeholder': 'Insira a latitude do campo.',
            'id': 'id_latitude'
        })
        self.fields['longitude'].widget = forms.TextInput(attrs={
            'placeholder': 'Insira a longitude do campo.',
            'id': 'id_longitude'
        })

    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if Campo.objects.exclude(pk=self.instance.pk).filter(nome=nome).exists():
            raise forms.ValidationError("Já existe um campo com este nome.")
        return nome


class CampoFotoForm(forms.ModelForm):
    class Meta:
        model = CampoFoto
        fields = ['imagem']
    imagem = forms.ImageField(required=False)  # Permite que a imagem seja opcional

CampoFotoFormSet = modelformset_factory(
    CampoFoto, 
    form=CampoFotoForm,
    max_num=1,  # Permite apenas um formulário
    can_delete=True,  # Permite exclusão
    extra=1  # Garante que sempre haverá um formulário vazio para adicionar a foto
)

class BuscaCampoForm(forms.Form):
    q = forms.CharField(required=False, label='Buscar')
    tipo_gramado = forms.ChoiceField(
        choices=[('', 'Todos'), ('natural', 'Natural'), ('sintetico', 'Sintético')], 
        required=False
    )
    iluminacao = forms.BooleanField(required=False, label='Com Iluminação')
    vestiarios = forms.BooleanField(required=False, label='Com Vestiários')
    cidade = forms.CharField(required=False, label='Cidade') 

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['data_reserva', 'hora_inicio', 'hora_fim']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_reserva'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['hora_inicio'].widget = forms.TimeInput(attrs={'type': 'time'})
        self.fields['hora_fim'].widget = forms.TimeInput(attrs={'type': 'time'})

class DiaBloqueadoForm(forms.ModelForm):
    class Meta:
        model = DiaBloqueado
        fields = ['campo', 'data']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data'].widget = forms.DateInput(attrs={'type': 'date'})



class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['comentario','avaliacao']
        widgets = {
            'comentario': forms.Textarea(attrs={'rows':3}),
            'avaliacao': forms.Select(),
        }

        
class FeedBackCancelamentoForm(forms.Form):
    motivos = forms.ChoiceField(
        choices=[
            ('', 'Escolha um motivo'),
            ('atendimento', 'Problemas com o atendimento'),
            ('preco', 'Preço muito alto'),
            ('disponibilidade', 'Dificuldade em encontrar disponibilidade'),
            ('outra', 'Outro')
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})  

    )
    
    comentario = forms.CharField(
        
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descreva seu motivo (opcional)'}),
        required=False
    )