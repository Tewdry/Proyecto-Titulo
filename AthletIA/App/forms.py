from django import forms
from App.models import (
    Perfil, TipoSangre, SaludUsuario,
    Publicacion, Comentario, Like, FavoritoPublicacion,
    SeguimientoUsuario, Notificacion, MensajePrivado,
    GrupoEntrenamiento, GrupoMiembro,
    ProgresoUsuario, HistorialMedidas,
    NutricionRegistro, SuenoUsuario,
    TipoObjetivo, ObjetivoUsuario,
    Opinion, Contacto, EstiloVidaUsuario, Tip
)


# =====================================================
# PERFIL Y SALUD
# =====================================================
class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = [
            'username', 'email', 'telefono', 'direccion',
            'fecha_nacimiento', 'genero', 'is_active', 'is_staff', 'is_superuser'
        ]
        widgets = {
            'is_active': forms.CheckboxInput(),
            'is_staff': forms.CheckboxInput(),
            'is_superuser': forms.CheckboxInput(),
        }


class PerfilEditForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = [
            'first_name', 'last_name', 'email', 'telefono',
            'direccion', 'fecha_nacimiento', 'foto'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


class TipoSangreForm(forms.ModelForm):
    class Meta:
        model = TipoSangre
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SaludUsuarioForm(forms.ModelForm):
    class Meta:
        model = SaludUsuario
        fields = [
            'frecuencia_cardiaca_reposo', 'enfermedades_preexistentes', 'lesiones_actuales',
            'alergias', 'fuma', 'bebe', 'tipo_sangre'
        ]
        widgets = {
            'frecuencia_cardiaca_reposo': forms.NumberInput(attrs={'class': 'form-control'}),
            'enfermedades_preexistentes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'lesiones_actuales': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'alergias': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'tipo_sangre': forms.Select(attrs={'class': 'form-control'}),
        }


# =====================================================
# PUBLICACIONES Y REACCIONES
# =====================================================
class PublicacionForm(forms.ModelForm):
    class Meta:
        model = Publicacion
        fields = ['perfil', 'contenido', 'media_url', 'vigente']
        widgets = {
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'media_url': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['publicacion', 'comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class LikeForm(forms.ModelForm):
    class Meta:
        model = Like
        fields = ['publicacion']


class FavoritoPublicacionForm(forms.ModelForm):
    class Meta:
        model = FavoritoPublicacion
        fields = ['publicacion']


# =====================================================
# RED SOCIAL (SEGUIMIENTOS, MENSAJES, NOTIFICACIONES)
# =====================================================
class SeguimientoUsuarioForm(forms.ModelForm):
    class Meta:
        model = SeguimientoUsuario
        fields = ['seguido']
        widgets = {'seguido': forms.Select(attrs={'class': 'form-control'})}


class NotificacionForm(forms.ModelForm):
    class Meta:
        model = Notificacion
        fields = ['perfil_destino', 'perfil_origen', 'tipo', 'mensaje', 'leida']
        widgets = {
            'tipo': forms.TextInput(attrs={'class': 'form-control'}),
            'mensaje': forms.TextInput(attrs={'class': 'form-control'}),
            'leida': forms.CheckboxInput(),
        }


class MensajePrivadoForm(forms.ModelForm):
    class Meta:
        model = MensajePrivado
        fields = ['receptor', 'contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# =====================================================
# GRUPOS Y COMUNIDADES
# =====================================================
class GrupoEntrenamientoForm(forms.ModelForm):
    class Meta:
        model = GrupoEntrenamiento
        fields = ['nombre', 'descripcion', 'vigente']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class GrupoMiembroForm(forms.ModelForm):
    class Meta:
        model = GrupoMiembro
        fields = ['grupo_entrenamiento', 'perfil', 'rol', 'activo']
        widgets = {
            'rol': forms.TextInput(attrs={'class': 'form-control'}),
            'grupo_entrenamiento': forms.Select(attrs={'class': 'form-control'}),
            'perfil': forms.Select(attrs={'class': 'form-control'}),
        }


# =====================================================
# PROGRESO, HISTORIAL Y NUTRICIÓN
# =====================================================
class ProgresoUsuarioForm(forms.ModelForm):
    class Meta:
        model = ProgresoUsuario
        fields = ['peso_kg', 'altura_cm', 'comentario']
        widgets = {
            'peso_kg': forms.NumberInput(attrs={'class': 'form-control'}),
            'altura_cm': forms.NumberInput(attrs={'class': 'form-control'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class HistorialMedidasForm(forms.ModelForm):
    class Meta:
        model = HistorialMedidas
        fields = ['grasa_corporal', 'masa_muscular', 'cintura_cm', 'cadera_cm']
        widgets = {
            'grasa_corporal': forms.NumberInput(attrs={'class': 'form-control'}),
            'masa_muscular': forms.NumberInput(attrs={'class': 'form-control'}),
            'cintura_cm': forms.NumberInput(attrs={'class': 'form-control'}),
            'cadera_cm': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class NutricionRegistroForm(forms.ModelForm):
    class Meta:
        model = NutricionRegistro
        fields = ['fecha', 'comida', 'calorias', 'proteinas', 'carbohidratos', 'grasas', 'descripcion']
        widgets = {
            'fecha': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'comida': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class SuenoUsuarioForm(forms.ModelForm):
    class Meta:
        model = SuenoUsuario
        fields = ['fecha', 'horas_dormidas', 'calidad_sueno', 'despertares_nocturnos']
        widgets = {
            'fecha': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'horas_dormidas': forms.NumberInput(attrs={'class': 'form-control'}),
            'calidad_sueno': forms.TextInput(attrs={'class': 'form-control'}),
            'despertares_nocturnos': forms.NumberInput(attrs={'class': 'form-control'}),
        }


# =====================================================
# OBJETIVOS
# =====================================================
class TipoObjetivoForm(forms.ModelForm):
    class Meta:
        model = TipoObjetivo
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ObjetivoUsuarioForm(forms.ModelForm):
    class Meta:
        model = ObjetivoUsuario
        fields = [
            'tipo_objetivo', 'meta_peso_kg', 'meta_grasa_corporal',
            'fecha_inicio', 'fecha_meta', 'estado', 'activo'
        ]
        widgets = {
            'tipo_objetivo': forms.Select(attrs={'class': 'form-control'}),
            'meta_peso_kg': forms.NumberInput(attrs={'class': 'form-control'}),
            'meta_grasa_corporal': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_meta': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
        }


# =====================================================
# OPINIÓN Y CONTACTO
# =====================================================
class OpinionForm(forms.ModelForm):
    class Meta:
        model = Opinion
        fields = ['contenido']
        labels = {'contenido': 'Deja tu opinión'}
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escribe tu opinión aquí...',
                'style': 'resize:none;',
            }),
        }


class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        fields = ['nombre', 'correo', 'asunto', 'mensaje']
        labels = {
            'nombre': 'Nombre completo',
            'correo': 'Correo electrónico',
            'asunto': 'Asunto',
            'mensaje': 'Mensaje',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre completo'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'}),
            'asunto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Motivo del mensaje'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Escribe tu mensaje aquí...'}),
        }


class EstiloVidaUsuarioForm(forms.ModelForm):
    class Meta:
        model = EstiloVidaUsuario
        fields = [
            'nivel_estres',
            'horas_sueno',
            'calidad_sueno',
            'alimentacion',
            'actividad_laboral',
            'entorno_entrenamiento',
            'frecuencia_entrenamiento',
        ]

        widgets = {
            'nivel_estres': forms.Select(choices=[
                ('', 'Seleccionar...'),
                ('Bajo', 'Bajo'),
                ('Moderado', 'Moderado'),
                ('Alto', 'Alto'),
            ], attrs={'class': 'form-control'}),

            'horas_sueno': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.1', 
                'placeholder': 'Ej: 7'
            }),

            'calidad_sueno': forms.Select(choices=[
                ('', 'Seleccionar...'),
                ('Buena', 'Buena'),
                ('Regular', 'Regular'),
                ('Mala', 'Mala'),
            ], attrs={'class': 'form-control'}),

            'alimentacion': forms.Select(choices=[
                ('', 'Seleccionar...'),
                ('Equilibrada', 'Equilibrada'),
                ('Alta en proteínas', 'Alta en proteínas'),
                ('Alta en carbohidratos', 'Alta en carbohidratos'),
                ('Desordenada', 'Desordenada'),
            ], attrs={'class': 'form-control'}),

            'actividad_laboral': forms.Select(choices=[
                ('', 'Seleccionar...'),
                ('Sedentaria', 'Sedentaria'),
                ('Moderadamente activa', 'Moderadamente activa'),
                ('Muy activa', 'Muy activa'),
            ], attrs={'class': 'form-control'}),

            'entorno_entrenamiento': forms.Select(choices=[
                ('', 'Seleccionar...'),
                ('Gimnasio', 'Gimnasio'),
                ('Casa', 'Casa'),
                ('Aire libre', 'Aire libre'),
            ], attrs={'class': 'form-control'}),

            'frecuencia_entrenamiento': forms.Select(choices=[
                ('', 'Seleccionar...'),
                ('1-2 veces por semana', '1-2 veces por semana'),
                ('3-4 veces por semana', '3-4 veces por semana'),
                ('5-6 veces por semana', '5-6 veces por semana'),
                ('Diario', 'Diario'),
            ], attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Validar que no queden campos vacíos importantes
        for field in self.fields:
            if not cleaned_data.get(field):
                self.add_error(field, "Este campo es requerido.")
        return cleaned_data
    
# =====================================================
# TIPS
# =====================================================

class TipForm(forms.ModelForm):
    class Meta:
        model = Tip
        fields = ['titulo', 'contenido', 'vigente']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vigente': forms.CheckboxInput(),
        }