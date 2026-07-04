from django import forms
from .models import Materie, Nota, Absenta, StudyCheckin, WeeklyReflection


class MaterieForm(forms.ModelForm):
    class Meta:
        model = Materie
        fields = ['nume', 'profesor']
        widgets = {
            'nume': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: Matematică'}),
            'profesor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: Prof. Ionescu'}),
        }
        labels = {'nume': 'Materie', 'profesor': 'Profesor (opțional)'}


class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['materie', 'valoare', 'descriere', 'data']
        widgets = {
            'materie': forms.Select(attrs={'class': 'form-select'}),
            'valoare': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10, 'step': 0.5}),
            'descriere': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: Teză semestrul I'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {'valoare': 'Notă (1-10)', 'descriere': 'Descriere', 'data': 'Data'}

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['materie'].queryset = Materie.objects.filter(user=user)


class AbsentaForm(forms.ModelForm):
    class Meta:
        model = Absenta
        fields = ['materie', 'tip', 'data', 'motiv']
        widgets = {
            'materie': forms.Select(attrs={'class': 'form-select'}),
            'tip': forms.Select(attrs={'class': 'form-select'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'motiv': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Motivul absenței'}),
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['materie'].queryset = Materie.objects.filter(user=user)


class StudyCheckinForm(forms.ModelForm):
    class Meta:
        model = StudyCheckin
        fields = ['ore_studiu', 'productivitate', 'intelegere', 'stres']
        widgets = {
            'ore_studiu': forms.Select(attrs={'class': 'form-select'}),
            'productivitate': forms.Select(attrs={'class': 'form-select'}),
            'intelegere': forms.Select(attrs={'class': 'form-select'}),
            'stres': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'ore_studiu': 'Cât ai studiat astăzi?',
            'productivitate': 'Productivitate (1-5)',
            'intelegere': 'Ai înțeles materia? (1-5)',
            'stres': 'Nivel de stres (1-5)',
        }


class WeeklyReflectionForm(forms.ModelForm):
    class Meta:
        model = WeeklyReflection
        fields = ['ce_a_mers', 'ce_a_fost_dificil', 'obiectiv']
        widgets = {
            'ce_a_mers': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ce a funcționat bine săptămâna aceasta?'}),
            'ce_a_fost_dificil': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ce a fost dificil sau provocator?'}),
            'obiectiv': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Obiectivul tău pentru săptămâna viitoare'}),
        }
        labels = {
            'ce_a_mers': 'Ce a mers bine?',
            'ce_a_fost_dificil': 'Ce a fost dificil?',
            'obiectiv': 'Obiectiv pentru săptămâna viitoare',
        }
