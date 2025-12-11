from django import forms
from api_ejercicio.models import (
    Musculo, TipoEjercicio, NivelDificultad,
    Ejercicio, Rutina, RutinaEjercicio, ProgresoEjercicio
)


# =====================================================
# 1️⃣ MÚSCULO Y TIPO DE EJERCICIO
# =====================================================
class MusculoForm(forms.ModelForm):
    class Meta:
        model = Musculo
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }


class TipoEjercicioForm(forms.ModelForm):
    class Meta:
        model = TipoEjercicio
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }


# =====================================================
# 2️⃣ NIVEL DE DIFICULTAD
# =====================================================
class NivelDificultadForm(forms.ModelForm):
    class Meta:
        model = NivelDificultad
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# =====================================================
# 3️⃣ EJERCICIO
# =====================================================
class EjercicioForm(forms.ModelForm):
    class Meta:
        model = Ejercicio
        fields = ['nombre', 'descripcion', 'video_url', 'vigente', 'tipo_ejercicio', 'musculo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'video_url': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/gif, video/mp4, video/webm'
            }),
            'tipo_ejercicio': forms.Select(attrs={'class': 'form-control'}),
            'musculo': forms.Select(attrs={'class': 'form-control'}),
            'vigente': forms.CheckboxInput(),
        }


# =====================================================
# 4️⃣ RUTINA
# =====================================================
class RutinaForm(forms.ModelForm):
    class Meta:
        model = Rutina
        fields = ['nombre', 'descripcion', 'vigente', 'nivel_dificultad']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nivel_dificultad': forms.Select(attrs={'class': 'form-control'}),
            'vigente': forms.CheckboxInput(),
        }


class RutinaEjercicioForm(forms.ModelForm):
    class Meta:
        model = RutinaEjercicio
        fields = ['rutina', 'ejercicio', 'repeticiones', 'orden']
        widgets = {
            'rutina': forms.Select(attrs={'class': 'form-control'}),
            'ejercicio': forms.Select(attrs={'class': 'form-control'}),
            'repeticiones': forms.NumberInput(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control'}),
        }


# =====================================================
# 5️⃣ PROGRESO DE EJERCICIOS
# =====================================================
class ProgresoEjercicioForm(forms.ModelForm):
    class Meta:
        model = ProgresoEjercicio
        fields = ['ejercicio', 'repeticiones_realizadas', 'peso_usado', 'duracion_minutos']
        widgets = {
            'ejercicio': forms.Select(attrs={'class': 'form-control'}),
            'repeticiones_realizadas': forms.NumberInput(attrs={'class': 'form-control'}),
            'peso_usado': forms.NumberInput(attrs={'class': 'form-control'}),
            'duracion_minutos': forms.NumberInput(attrs={'class': 'form-control'}),
        }

