import json
import requests
import traceback
from datetime import date, datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Count, Q, OuterRef, Exists
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db import transaction
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST, require_GET
from django.dispatch import receiver
from django.db.models.signals import post_save
import re
from urllib.parse import urlparse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

# --- IMPORTACIÓN DE MODELOS ---
from App.models import *
from api_ejercicio.models import *
from IA.models import RecomendacionIA

# --- IMPORTACIÓN DE FORMULARIOS ---
from App.forms import (
    PerfilForm, PerfilEditForm, PublicacionForm, ComentarioForm, 
    ContactoForm, OpinionForm, TipForm, EstiloVidaUsuarioForm, 
    TipoSangreForm, ObjetivoUsuarioForm, SaludUsuarioForm,
    NutricionRegistroForm, SuenoUsuarioForm, GrupoEntrenamientoForm,
    HistorialMedidasForm
)
from api_ejercicio.forms import (
    MusculoForm, EjercicioForm, RutinaForm, 
    NivelDificultadForm, TipoEjercicioForm
)

# ==============================================================
# HELPERS DEL ADMIN (FUNCIONES AUXILIARES)
# ==============================================================

@staff_member_required
def listar_generico(request, model, title, title_singular, columns, attributes, crear_url, editar_url_name, eliminar_url_name):
    """Vista genérica para listar objetos en el panel premium."""
    object_list = model.objects.all()
    
    # Ordenar si es posible
    if hasattr(model, 'fecha_creacion'):
        object_list = object_list.order_by('-fecha_creacion')
    elif hasattr(model, 'id'):
        object_list = object_list.order_by('-id')

    context = {
        'title': title,
        'title_singular': title_singular,
        'columns': columns,
        'attributes': attributes,
        'object_list': object_list,
        'crear_url_name': crear_url,
        'editar_url_name': editar_url_name,
        'eliminar_url_name': eliminar_url_name,
    }
    return render(request, "admin/admin_listar_base.html", context)

@staff_member_required
def crear_objeto_admin(request, form_class, title, back_url_name):
    """Vista genérica para crear objetos."""
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            if hasattr(obj, 'perfil') and not getattr(obj, 'perfil', None):
                obj.perfil = request.user
            obj.save()
            
            messages.success(request, f"✅ {title} creado correctamente.")
            return redirect(back_url_name)
        else:
            messages.error(request, "❌ Error en el formulario. Revisa los campos.")
    else:
        form = form_class()
    
    return render(request, 'admin/admin_form_base.html', {
        'form': form,
        'title': f"Crear {title}",
        'back_url': reverse(back_url_name)
    })

@staff_member_required
def editar_objeto_admin(request, form_class, title, back_url_name, pk, model_class):
    """Vista genérica para editar objetos."""
    obj = get_object_or_404(model_class, pk=pk)
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ {title} actualizado correctamente.")
            return redirect(back_url_name)
        else:
            messages.error(request, "❌ Error al actualizar.")
    else:
        form = form_class(instance=obj)
    
    return render(request, 'admin/admin_form_base.html', {
        'form': form,
        'title': f"Editar {title}",
        'back_url': reverse(back_url_name)
    })

@staff_member_required
def eliminar_objeto_admin(request, model_class, title_singular, redirect_url_name, pk):
    """Vista genérica para eliminar objetos."""
    obj = get_object_or_404(model_class, pk=pk)
    if request.method == "POST":
        try:
            obj.delete()
            messages.success(request, f"🗑️ {title_singular} eliminado.")
        except Exception as e:
            messages.error(request, f"Error al eliminar: {e}")
    return redirect(redirect_url_name)


# ==============================================================
# DASHBOARD (PANEL PRINCIPAL)
# ==============================================================

@staff_member_required
def panel_admin(request):
    hoy = date.today()
    
    # --- KPIs ---
    total_usuarios = Perfil.objects.count()
    nuevos_usuarios_mes = Perfil.objects.filter(date_joined__month=hoy.month, date_joined__year=hoy.year).count()
    
    # Rutinas IA hoy (Si el modelo existe y tiene datos)
    try:
        rutinas_ia_hoy = RecomendacionIA.objects.filter(fecha_recomendacion__date=hoy).count()
    except:
        rutinas_ia_hoy = 0
        
    # Usuarios activos (aprox 15 min)
    activos_ahora = Perfil.objects.filter(last_login__gte=datetime.now() - timedelta(minutes=15)).count()
    nuevos_posts = Publicacion.objects.filter(fecha_creacion__date=hoy).count()

    # --- CHART: Crecimiento Usuarios (6 meses) ---
    seis_meses_atras = hoy - timedelta(days=180)
    usuarios_por_mes = (
        Perfil.objects
        .filter(date_joined__gte=seis_meses_atras)
        .annotate(mes=TruncMonth('date_joined'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    labels_crecimiento = [x['mes'].strftime("%b") for x in usuarios_por_mes]
    data_crecimiento = [x['total'] for x in usuarios_por_mes]

    # --- CHART: Músculos Populares (Top 5) ---
    musculos_populares = (
        Ejercicio.objects
        .values('musculo__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )
    labels_musculos = [x['musculo__nombre'] for x in musculos_populares]
    data_musculos = [x['total'] for x in musculos_populares]

    context = {
        'kpi': {
            'total_usuarios': total_usuarios,
            'nuevos_mes': nuevos_usuarios_mes,
            'rutinas_ia': rutinas_ia_hoy,
            'activos': activos_ahora,
            'posts_hoy': nuevos_posts
        },
        'charts': {
            'crecimiento_labels': json.dumps(labels_crecimiento),
            'crecimiento_data': json.dumps(data_crecimiento),
            'musculos_labels': json.dumps(labels_musculos),
            'musculos_data': json.dumps(data_musculos),
        }
    }
    return render(request, "admin/admin_base.html", context)

@staff_member_required
def panel_analisis_rutinas(request):

    # === 1. DISTRIBUCIÓN DE DIFICULTADES ===
    rutinas_por_dificultad = (
        Rutina.objects
        .values('nivel_dificultad__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    labels_dificultad = [
        r['nivel_dificultad__nombre'] or 'Sin Nivel'
        for r in rutinas_por_dificultad
    ]
    data_dificultad = [r['total'] for r in rutinas_por_dificultad]

    # === 2. TOP 5 CREADORES ===
    top_creadores = (
        Rutina.objects
        .values('perfil__username')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )

    # === 3. RUTINA MÁS GUARDADA ===
    rutina_popular = (
        RutinaGuardada.objects
        .values("rutina__id", "rutina__nombre", "rutina__nivel_dificultad__nombre")
        .annotate(total_guardados=Count("id"))
        .order_by("-total_guardados")
        .first()
    )

    # Si no hay registros aún
    if not rutina_popular:
        rutina_popular = {
            "rutina__nombre": "Sin registros",
            "rutina__nivel_dificultad__nombre": "-",
            "total_guardados": 0,
        }

    # === 4. REPORTES ===
    try:
        reportes_activos = ComentarioReporte.objects.filter(
            fecha__gte=date.today() - timedelta(days=30)
        ).count()
        reportes_total = ComentarioReporte.objects.count()
    except:
        reportes_activos = 0
        reportes_total = 0

    # === CONTEXTO ===
    context = {
        'charts': {
            'dificultad_labels': json.dumps(labels_dificultad),
            'dificultad_data': json.dumps(data_dificultad),
        },
        'top_creadores': top_creadores,
        'rutina_popular': rutina_popular,
        'reportes_activos': reportes_activos,
        'reportes_total': reportes_total,
    }

    return render(request, "admin/admin_data_analysis.html", context)


@staff_member_required
def listar_reportes_comentarios(request):
    return listar_generico(
        request,
        model=ComentarioReporte,
        title="Reportes de Comentarios",
        title_singular="Reporte",
        columns=["Motivo", "Comentario", "Reportado Por", "Fecha"],
        attributes=["motivo", "comentario__comentario", "perfil__username", "fecha"],
        crear_url=None,
        editar_url_name=None,
        eliminar_url_name='eliminar_reporte_comentario'
    )

@staff_member_required
def eliminar_reporte_comentario(request, pk):
    return eliminar_objeto_admin(request, ComentarioReporte, "Reporte", 'listar_reportes_comentarios', pk)

@staff_member_required
def eliminar_comentario_admin(request, pk):
    return eliminar_objeto_admin(request, Comentario, "Comentario", 'listar_reportes_comentarios', pk)

@staff_member_required
def eliminar_publicacion_admin(request, pk):
    return eliminar_objeto_admin(request, Publicacion, "Publicación", 'listar_publicaciones', pk)


# ==============================================================
# VISTAS CRUD ADMIN (IMPLEMENTACIÓN COMPLETA)
# ==============================================================

# --- GIMNASIO ---
@staff_member_required
def listar_musculos(request):
    return listar_generico(
        request,
        Musculo,
        "Músculos",
        "Músculo",
        ["Nombre"],
        ["nombre"],
        'crear_musculo',
        'editar_musculo',
        'eliminar_musculo'
    )

@staff_member_required
def crear_musculo(request):
    return crear_objeto_admin(request, MusculoForm, "Músculo", "listar_musculos")

@staff_member_required
def editar_musculo(request, pk):
    return editar_objeto_admin(request, MusculoForm, "Músculo", "listar_musculos", pk, Musculo)

@staff_member_required
def eliminar_musculo(request, pk):
    return eliminar_objeto_admin(request, Musculo, "Músculo", "listar_musculos", pk)


@staff_member_required
def listar_tipos(request):
    return listar_generico(request, TipoEjercicio, "Tipos de Ejercicio", "Tipo", ["ID", "Nombre"], ["id", "nombre"], 'crear_tipo_ejercicio', 'editar_tipo_ejercicio', 'eliminar_tipo_ejercicio')

@staff_member_required
def crear_tipo_ejercicio(request):
    return crear_objeto_admin(request, TipoEjercicioForm, "Tipo Ejercicio", "listar_tipos")

@staff_member_required
def editar_tipo_ejercicio(request, pk):
    return editar_objeto_admin(request, TipoEjercicioForm, "Tipo Ejercicio", "listar_tipos", pk, TipoEjercicio)

@staff_member_required
def eliminar_tipo_ejercicio(request, pk):
    return eliminar_objeto_admin(request, TipoEjercicio, "Tipo Ejercicio", 'listar_tipos', pk)

@staff_member_required
def listar_niveles(request):
    return listar_generico(request, NivelDificultad, "Niveles Dificultad", "Nivel", ["ID", "Nombre"], ["dificultad_id", "nombre"], 'crear_nivel', 'editar_nivel', 'eliminar_nivel')

@staff_member_required
def crear_nivel(request):
    return crear_objeto_admin(request, NivelDificultadForm, "Nivel", "listar_niveles")

@staff_member_required
def editar_nivel(request, pk):
    return editar_objeto_admin(request, NivelDificultadForm, "Nivel", "listar_niveles", pk, NivelDificultad)

@staff_member_required
def eliminar_nivel(request, pk):
    return eliminar_objeto_admin(request, NivelDificultad, "Nivel", 'listar_niveles', pk)

@staff_member_required
def listar_ejercicios(request):
    return listar_generico(request, Ejercicio, "Ejercicios", "Ejercicio", ["Nombre", "Músculo", "Dificultad"], ["nombre", "musculo", "nivel_dificultad"], 'crear_ejercicio', 'editar_ejercicio', 'eliminar_ejercicio')

@staff_member_required
def crear_ejercicio(request):
    return crear_objeto_admin(request, EjercicioForm, "Ejercicio", "listar_ejercicios")

@staff_member_required
def editar_ejercicio(request, pk):
    return editar_objeto_admin(request, EjercicioForm, "Ejercicio", "listar_ejercicios", pk, Ejercicio)

@staff_member_required
def eliminar_ejercicio(request, pk):
    return eliminar_objeto_admin(request, Ejercicio, "Ejercicio", 'listar_ejercicios', pk)

@staff_member_required
def listar_rutinas(request):
    # Obtener todas las rutinas
    rutinas = Rutina.objects.select_related("perfil", "nivel_dificultad").all()

    # Preparar filtros dinámicos
    filtros = {
        "Creador": list(rutinas.values_list("perfil__username", flat=True).distinct()),
        "Dificultad": list(rutinas.values_list("nivel_dificultad__nombre", flat=True).distinct()),
    }

    context = {
        "title": "Rutinas",
        "title_singular": "Rutina",
        "object_list": rutinas,
        "columns": ["Nombre", "Creador", "Dificultad"],
        "attributes": ["nombre", "perfil", "nivel_dificultad"],

        "crear_url_name": None,
        "editar_url_name": None,

        "eliminar_url_name": "eliminar_rutina",

        "filters": filtros,
    }

    return render(request, "admin/admin_listar_base.html", context)



@staff_member_required
def crear_rutina(request):
    return crear_objeto_admin(request, RutinaForm, "Rutina", "listar_rutinas")

@staff_member_required
def eliminar_rutina(request, pk):
    return eliminar_objeto_admin(request, Rutina, "Rutina", 'listar_rutinas', pk)


# --- USUARIOS ---
@staff_member_required
def toggle_staff(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para modificar estados de Staff.")
        return redirect('listar_usuarios')

    user = Perfil.objects.get(pk=pk)

    if user == request.user:
        messages.error(request, "No puedes modificar tu propio estado de Staff.")
        return redirect('listar_usuarios')

    # Cambiar estado
    user.is_staff = not user.is_staff
    user.save()

    estado = "activado" if user.is_staff else "desactivado"
    messages.success(request, f"Estado Staff de {user.username} fue {estado}.")
    return redirect('listar_usuarios')



@staff_member_required
def listar_usuarios(request):
    return listar_generico(
        request,
        Perfil,
        "Usuarios",
        "Usuario",
        ["User", "Email", "Staff", "Fecha Reg."],
        ["username", "email", "is_staff", "date_joined"],
        None,
        'editar_usuario',
        'eliminar_usuario'
    )


@staff_member_required
def crear_usuario(request):
    if not request.user.is_superuser:
        messages.error(request, "Solo un superusuario puede crear nuevos usuarios.")
        return redirect("listar_usuarios")

    return crear_objeto_admin(request, PerfilForm, "Usuario", "listar_usuarios")


@staff_member_required
def editar_usuario(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para editar usuarios.")
        return redirect("listar_usuarios")

    return editar_objeto_admin(request, PerfilForm, "Usuario", "listar_usuarios", pk, Perfil)


@staff_member_required
def eliminar_usuario(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para eliminar usuarios.")
        return redirect("listar_usuarios")

    return eliminar_objeto_admin(request, Perfil, "Usuario", 'listar_usuarios', pk)


# --- CONTENIDO (Posts, Comentarios, Tips) ---
@staff_member_required
def listar_publicaciones(request):
    return listar_generico(
        request,
        Publicacion,
        "Publicaciones",
        "Post",
        ["Autor", "Contenido", "Fecha"],
        ["perfil", "contenido", "fecha_creacion"],
        None,                
        None,               
        'eliminar_publicacion'   
    )


@staff_member_required
def crear_publicacion(request):
    return crear_objeto_admin(request, PublicacionForm, "Post", "listar_publicaciones")

@staff_member_required
def editar_publicacion(request, pk):
    return editar_objeto_admin(request, PublicacionForm, "Post", "listar_publicaciones", pk, Publicacion)

@staff_member_required
def eliminar_publicacion(request, pk):
    return eliminar_objeto_admin(request, Publicacion, "Post", 'listar_publicaciones', pk)

@staff_member_required
def listar_comentarios(request):
    return listar_generico(request, Comentario, "Comentarios", "Comentario", ["Usuario", "Post", "Texto"], ["perfil", "publicacion_id", "comentario"], None, None, 'eliminar_comentario')

@staff_member_required
def eliminar_comentario(request, pk):
    return eliminar_objeto_admin(request, Comentario, "Comentario", 'listar_comentarios', pk)

@staff_member_required
def listar_tips(request):
    return listar_generico(request, Tip, "Tips", "Tip", ["Título", "Contenido"], ["titulo", "contenido"], 'crear_tip', 'editar_tip', 'eliminar_tip')

@staff_member_required
def crear_tip(request):
    return crear_objeto_admin(request, TipForm, "Tip", "listar_tips")

@staff_member_required
def editar_tip(request, pk):
    return editar_objeto_admin(request, TipForm, "Tip", "listar_tips", pk, Tip)

@staff_member_required
def eliminar_tip(request, pk):
    return eliminar_objeto_admin(request, Tip, "Tip", 'listar_tips', pk)

# --- SALUD Y OTROS ---
@staff_member_required
def listar_salud_usuarios(request):
    return listar_generico(request, SaludUsuario, "Salud", "Ficha", ["ID", "Tipo Sangre", "Fuma"], ["id", "tipo_sangre", "fuma"], None, None, None)

@staff_member_required
def listar_tipos_sangre(request):
    return listar_generico(request, TipoSangre, "Tipos Sangre", "Tipo", ["Nombre"], ["nombre"], 'crear_tipo_sangre', 'editar_tipo_sangre', 'eliminar_tipo_sangre')

@staff_member_required
def crear_tipo_sangre(request):
    return crear_objeto_admin(request, TipoSangreForm, "Tipo Sangre", "listar_tipos_sangre")

@staff_member_required
def editar_tipo_sangre(request, pk):
    return editar_objeto_admin(request, TipoSangreForm, "Tipo Sangre", "listar_tipos_sangre", pk, TipoSangre)

@staff_member_required
def eliminar_tipo_sangre(request, pk):
    return eliminar_objeto_admin(request, TipoSangre, "Tipo Sangre", 'listar_tipos_sangre', pk)

@staff_member_required
def listar_objetivos(request):
    return listar_generico(request, ObjetivoUsuario, "Objetivos", "Objetivo", ["Usuario", "Meta", "Estado"], ["perfil", "tipo_objetivo", "estado"], None, 'editar_objetivo', 'eliminar_objetivo')

@staff_member_required
def editar_objetivo(request, pk):
    return editar_objeto_admin(request, ObjetivoUsuarioForm, "Objetivo", "listar_objetivos", pk, ObjetivoUsuario)

@staff_member_required
def eliminar_objetivo(request, pk):
    return eliminar_objeto_admin(request, ObjetivoUsuario, "Objetivo", 'listar_objetivos', pk)

@staff_member_required
def listar_contactos(request):
    return listar_generico(request, Contacto, "Mensajes", "Mensaje", ["Nombre", "Email", "Asunto"], ["nombre", "correo", "asunto"], None, None, 'eliminar_contacto')

@staff_member_required
def eliminar_contacto(request, pk):
    return eliminar_objeto_admin(request, Contacto, "Mensaje", 'listar_contactos', pk)

@staff_member_required
def listar_estilos_vida(request):
    return listar_generico(request, EstiloVidaUsuario, "Estilos Vida", "Estilo", ["Usuario", "Actividad", "Dieta"], ["perfil", "actividad_laboral", "alimentacion"], None, None, None)

@staff_member_required
def listar_calendario_rutinas(request):
    return listar_generico(
        request,
        CalendarioRutina,
        "Calendario",
        "Evento",
        ["Usuario", "Rutina", "Fecha"],
        ["perfil", "rutina", "fecha"],
        None,              
        None,              
        'eliminar_calendario_rutina'
    )

@staff_member_required
def eliminar_calendario_rutina(request, pk):
    return eliminar_objeto_admin(
        request,
        CalendarioRutina,
        "Evento de Calendario",
        'listar_calendario_rutinas',
        pk
    )

@staff_member_required
def listar_grupos(request):
    return listar_generico(request, GrupoEntrenamiento, "Grupos", "Grupo", ["Nombre", "Creador"], ["nombre", "perfil_creador"], None, 'editar_grupo', 'eliminar_grupo')

@staff_member_required
def editar_grupo(request, pk):
    return editar_objeto_admin(request, GrupoEntrenamientoForm, "Grupo", "listar_grupos", pk, GrupoEntrenamiento)

@staff_member_required
def eliminar_grupo(request, pk):
    return eliminar_objeto_admin(request, GrupoEntrenamiento, "Grupo", 'listar_grupos', pk)

@staff_member_required
def listar_historial_medidas(request):
    return listar_generico(request, HistorialMedidas, "Historial Medidas", "Medida", ["Usuario", "Fecha"], ["perfil", "progreso_usuario__fecha"], None, None, None)

@staff_member_required
def listar_nutricion_registros(request):
    return listar_generico(request, NutricionRegistro, "Nutrición", "Registro", ["Usuario", "Comida", "Kcal", "Fecha"], ["perfil", "comida", "calorias", "fecha"], None, None, None)

@staff_member_required
def listar_sueno_usuarios(request):
    return listar_generico(request, SuenoUsuario, "Sueño", "Registro", ["Usuario", "Horas", "Fecha"], ["perfil", "horas_dormidas", "fecha"], None, None, None)

@staff_member_required
def listar_progresos(request):
    return listar_generico(request, ProgresoEjercicio, "Progresos Ejercicio", "Progreso", ["Usuario", "Ejercicio", "Peso"], ["perfil", "ejercicio", "peso_usado"], None, None, 'eliminar_progreso')

@staff_member_required
def eliminar_progreso(request, pk):
    return eliminar_objeto_admin(request, ProgresoEjercicio, "Progreso", 'listar_progresos', pk)

# Placeholder para las vistas que faltaban
@staff_member_required
def listar_rutina_ejercicios(request):
    return listar_generico(
        request,
        RutinaEjercicio,
        "Ejercicios en Rutina",
        "Item",
        ["Rutina", "Ejercicio", "Orden"],
        ["rutina", "ejercicio", "orden"],
        crear_url_name=None,
        editar_url_name=None,
        eliminar_url_name="eliminar_rutina_ejercicio"
    )

    
@staff_member_required
def crear_rutina_ejercicio(request):
    # Requiere RutinaEjercicioForm
    return redirect('listar_rutinas') 

@staff_member_required
def eliminar_rutina_ejercicio(request, pk):
    return eliminar_objeto_admin(request, RutinaEjercicio, "Item", 'listar_rutina_ejercicios', pk)


@staff_member_required
def listar_opiniones(request):
    return listar_generico(
        request,
        model=Opinion,
        title="Opiniones de Usuarios",
        title_singular="Opinión",
        columns=["Usuario", "Contenido", "Fecha"],
        attributes=["perfil", "contenido", "fecha_creacion"],
        crear_url=None,          # No creamos opiniones desde el admin
        editar_url_name=None,    # No editamos opiniones de usuarios
        eliminar_url_name='eliminar_opinion'
    )

@staff_member_required
def eliminar_opinion(request, pk):
    return eliminar_objeto_admin(request, Opinion, "Opinión", 'listar_opiniones', pk)


# ==============================================================
# VISTAS PÚBLICAS (ORIGINALES)
# ==============================================================

def base(request):
    return render(request, 'Base/base.html')

def index(request):
    opiniones = Opinion.objects.filter(vigente=True).order_by('-fecha_creacion')[:3]
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = OpinionForm(request.POST)
            if form.is_valid():
                nueva_opinion = form.save(commit=False)
                nueva_opinion.perfil = request.user
                nueva_opinion.vigente = True
                nueva_opinion.save()
                return redirect('base')
        else:
            return redirect('inicio_Sesion')
    else:
        form = OpinionForm()
    return render(request, 'Home/index.html', {'opiniones': opiniones, 'form': form})

def nosotros(request):
    return render(request, 'Home/nosotros.html')

def contactanos(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu mensaje fue enviado correctamente.")
            return redirect('contactanos')
    else:
        form = ContactoForm()
    return render(request, 'Home/contactanos.html', {'form': form})

# ==============================================================
# AUTENTICACIÓN (ORIGINAL + REGISTRO)
# ==============================================================

def inicio_Sesion(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password')
        if not Perfil.objects.filter(username=username).exists():
            messages.error(request, "El usuario no existe.")
            return render(request, 'Autenticacion/inicio_Sesion.html')
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Contraseña incorrecta.")
            return render(request, 'Autenticacion/inicio_Sesion.html')
        login(request, user)
        messages.success(request, f"¡Bienvenido, {user.username}!")
        if user.is_staff:
            return redirect('panel_admin')
        return redirect('base')
    return render(request, 'Autenticacion/inicio_Sesion.html')

@login_required
def cerrar_Sesion(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('base')

def registro(request):
    objetivos = TipoObjetivo.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        print("\n🔵 [DEBUG] INICIO PROCESO DE REGISTRO")
        
        try:
            # Recolección de datos
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip().lower()
            password1_pass = request.POST.get('password1')
            fecha_nacimiento = request.POST.get('fecha_nacimiento')

            # ---- VALIDAR USERNAME ----
            parsed = urlparse(username)
            if parsed.scheme or parsed.netloc or "www." in username.lower():
                messages.error(request, "El nombre de usuario no puede ser una URL.")
                return render(request, 'Autenticacion/registro.html', {'objetivos': objetivos})

            if not re.match(r'^[a-zA-Z0-9_-]{3,20}$', username):
                messages.error(request, "Username inválido. Solo letras, números y guiones (3-20 caracteres).")
                return render(request, 'Autenticacion/registro.html', {'objetivos': objetivos})


            # ---- VALIDAR CONTRASEÑA ----
            if not password1_pass or len(password1_pass) < 8:
                messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
                return render(request, 'Autenticacion/registro.html', {'objetivos': objetivos})

            if not re.search(r"[A-Z]", password1_pass) or not re.search(r"[0-9]", password1_pass):
                messages.error(request, "La contraseña debe contener al menos una mayúscula y un número.")
                return render(request, 'Autenticacion/registro.html', {'objetivos': objetivos})


            # ---- VALIDAR EMAIL SEGURO ----
            try:
                validate_email(email)

                if re.search(r"(c:|file:|/etc/|boot.ini|system32|windows/)", email, re.IGNORECASE):
                    raise ValidationError("Email peligroso")

            except ValidationError:
                messages.error(request, "Correo electrónico inválido o inseguro.")
                return render(request, 'Autenticacion/registro.html', {'objetivos': objetivos})
            
            print(f"📝 [DEBUG] Usuario: {username}, Email: {email}, Fecha Nac: {fecha_nacimiento}")

            # Validaciones básicas
            if Perfil.objects.filter(username=username).exists():
                print("🔴 [ERROR] Usuario ya existe")
                messages.error(request, 'Usuario ya registrado.')
                return render(request, 'Autenticacion/registro.html', {'objetivos': objetivos})

            # INICIO TRANSACCIÓN
            with transaction.atomic():
                print("🟢 [DEBUG] Creando perfil base...")
                perfil = Perfil.objects.create_user(username=username, password=password1_pass, email=email)
                perfil.telefono = request.POST.get('telefono')
                perfil.direccion = request.POST.get('direccion')
                perfil.fecha_nacimiento = parse_date(fecha_nacimiento) if fecha_nacimiento else None
                perfil.save()
                print(f"✅ [DEBUG] Perfil creado. ID: {perfil.id}")

                # SALUD
                print("🟢 [DEBUG] Guardando datos de salud...")
                tipo_sangre_nombre = request.POST.get('tipo_sangre')
                ts = None
                if tipo_sangre_nombre:
                    ts, _ = TipoSangre.objects.get_or_create(nombre=tipo_sangre_nombre)
                
                # Frecuencia Cardíaca (Manejo seguro de enteros)
                fc_str = request.POST.get('frecuencia_cardiaca', '')
                # Extraer solo números si viene texto como "60 bpm"
                fc_val = ''.join(filter(str.isdigit, fc_str)) 
                fc = int(fc_val) if fc_val else None

                salud = SaludUsuario.objects.create(
                    tipo_sangre=ts,
                    frecuencia_cardiaca_reposo=fc,
                    enfermedades_preexistentes=request.POST.get('enfermedades'),
                    lesiones_actuales=request.POST.get('lesiones'),
                    alergias=request.POST.get('alergias'),
                    fuma=request.POST.get('fuma') == 'on', # Checkbox envía 'on' si está marcado
                    bebe=request.POST.get('bebe') == 'on'
                )
                perfil.salud_usuario = salud
                perfil.save()
                print("✅ [DEBUG] Salud guardada.")

                # PROGRESO
                print("🟢 [DEBUG] Guardando progreso inicial...")
                altura = request.POST.get('altura_cm')
                peso = request.POST.get('peso_kg')
                
                progreso = ProgresoUsuario.objects.create(
                    perfil=perfil,
                    altura_cm=float(altura) if altura else None,
                    peso_kg=float(peso) if peso else None,
                    comentario="Registro inicial"
                )
                
                # Historial Medidas
                grasa = request.POST.get('grasa_corporal')
                masa = request.POST.get('masa_muscular')
                cintura = request.POST.get('cintura_cm')
                cadera = request.POST.get('cadera_cm')

                if any([grasa, masa, cintura, cadera]):
                    HistorialMedidas.objects.create(
                        progreso_usuario=progreso, perfil=perfil,
                        grasa_corporal=float(grasa) if grasa else None,
                        masa_muscular=float(masa) if masa else None,
                        cintura_cm=float(cintura) if cintura else None,
                        cadera_cm=float(cadera) if cadera else None
                    )
                print("✅ [DEBUG] Progreso guardado.")

                # OBJETIVOS
                print("🟢 [DEBUG] Guardando objetivos...")
                obj_nombre = request.POST.get('tipo_objetivo')
                tipo_obj = None
                if obj_nombre:
                    tipo_obj, _ = TipoObjetivo.objects.get_or_create(nombre=obj_nombre)
                
                ObjetivoUsuario.objects.create(
                    perfil=perfil, 
                    tipo_objetivo=tipo_obj,
                    fecha_inicio=parse_date(request.POST.get('fecha_inicio') or '') or date.today(),
                    fecha_meta=parse_date(request.POST.get('fecha_meta') or ''),
                    estado=request.POST.get('estado', 'En progreso'),
                    activo=True
                )
                print("✅ [DEBUG] Objetivos guardados.")

            # FIN TRANSACCIÓN
            print("✨ [EXITO] Todo guardado correctamente. Redirigiendo...")
            messages.success(request, '¡Registro exitoso!')
            return redirect('inicio_Sesion')

        except Exception as e:
            print(f"🔥 [EXCEPCIÓN FATAL] {str(e)}")
            traceback.print_exc()
            messages.error(request, f'Error interno: {str(e)}')
            return render(request, 'Autenticacion/registro.html', {'objetivos': objetivos})

    return render(request, 'Autenticacion/registro.html', {'objetivos': objetivos})

# ==============================================================
# PERFIL Y SOCIAL (ORIGINALES)
# ==============================================================

@login_required
def perfil(request):
    perfil = request.user
    progresos = ProgresoUsuario.objects.filter(perfil=perfil).order_by('-fecha')

    if request.method == 'POST':
        if 'guardar_progreso' in request.POST:
            peso = request.POST.get('peso_kg')
            altura = request.POST.get('altura_cm')
            comentario = request.POST.get('comentario', '')
            if peso and altura:
                ProgresoUsuario.objects.create(perfil=perfil, peso_kg=peso, altura_cm=altura, comentario=comentario)
                messages.success(request, "✅ Progreso registrado.")
                return redirect('perfil')
            else:
                messages.error(request, "❌ Faltan datos.")
        else:
            form = PerfilEditForm(request.POST, request.FILES, instance=perfil)
            if form.is_valid():
                form.save()
                messages.success(request, "✅ Perfil actualizado.")
                return redirect('perfil')
    else:
        form = PerfilEditForm(instance=perfil)

    return render(request, 'Perfil/perfil.html', {'form': form, 'perfil': perfil, 'progresos': progresos})

@login_required
def detalle_perfil(request, pk):
    perfil = get_object_or_404(Perfil, pk=pk)

    # -------------------------------------------------------
    # OBTENER EL ÚLTIMO PESO REAL (ProgresoUsuario)
    # -------------------------------------------------------
    # Ordenamos por ID descendente (-id) para obtener el último registro creado
    ultimo_progreso = ProgresoUsuario.objects.filter(perfil=perfil).order_by('-id').first()

    peso_actual = 0
    altura_actual = 0
    imc = 0

    if ultimo_progreso:
        peso_actual = ultimo_progreso.peso_kg or 0
        altura_actual = ultimo_progreso.altura_cm or 0
        
        # Calculamos IMC si hay datos
        if peso_actual and altura_actual:
            estatura_m = altura_actual / 100
            imc = round(peso_actual / (estatura_m ** 2), 1)

    # -------------------------
    # PROGRESOS (Gráfico histórico)
    # -------------------------
    progresos = ProgresoUsuario.objects.filter(perfil=perfil).order_by("fecha")

    # -------------------------
    # PUBLICACIONES DEL PERFIL
    # -------------------------
    publicaciones = (
        Publicacion.objects
        .filter(perfil=perfil)
        .select_related("perfil")
        .annotate(
            num_likes=Count("like", distinct=True),
            num_comentarios=Count("comentario", distinct=True),
            num_favoritos=Count("favoritopublicacion", distinct=True),
            es_liked=Exists(
                Like.objects.filter(publicacion=OuterRef("pk"), perfil=request.user)
            ),
            es_favorited=Exists(
                FavoritoPublicacion.objects.filter(publicacion=OuterRef("pk"), perfil=request.user)
            )
        )
        .order_by("-fecha_creacion")
    )

    # ------------------------------------------------
    # PUBLICACIONES GUARDADAS
    # ------------------------------------------------
    publicaciones_guardadas = []
    if perfil == request.user:
        favoritos = (
            FavoritoPublicacion.objects
            .filter(perfil=request.user)
            .select_related("publicacion", "publicacion__perfil")
            .order_by("-id")
        )
        publicaciones_guardadas = [f.publicacion for f in favoritos]

    # -------------------------
    # SEGUIR / SIGUIENDO
    # -------------------------
    yo_sigo_ids = set(
        SeguimientoUsuario.objects.filter(
            seguidor=request.user, vigente=True
        ).values_list("seguido_id", flat=True)
    ) if request.user.is_authenticated else set()

    siguiendo = perfil.id in yo_sigo_ids

    # Contadores
    seguidores_count = SeguimientoUsuario.objects.filter(seguido=perfil, vigente=True).count()
    siguiendo_count = SeguimientoUsuario.objects.filter(seguidor=perfil, vigente=True).count()

    # -------------------------
    # CREAR PUBLICACIÓN
    # -------------------------
    if request.method == "POST" and perfil == request.user:
        contenido = request.POST.get("contenido")
        media = request.FILES.get("media_url")

        if contenido or media:
            Publicacion.objects.create(
                perfil=request.user,
                contenido=contenido,
                media_url=media
            )
            return redirect("detalle_perfil", pk=perfil.pk)

    return render(request, "Perfil/detalle_perfil.html", {
        "perfil": perfil,
        "peso_actual": peso_actual,     # <--- DATO CORREGIDO
        "altura_actual": altura_actual, # <--- DATO CORREGIDO
        "imc": imc,                     # <--- IMC ACTUALIZADO
        "progresos": progresos,
        "publicaciones": publicaciones,
        "publicaciones_guardadas": publicaciones_guardadas,
        "es_mi_perfil": perfil == request.user,
        "siguiendo": siguiendo,
        "seguidores_count": seguidores_count,
        "siguiendo_count": siguiendo_count
    })

@login_required
def editar_estilo_vida(request):
    perfil = request.user
    estilo_vida, _ = EstiloVidaUsuario.objects.get_or_create(perfil=perfil)
    if request.method == 'POST':
        form = EstiloVidaUsuarioForm(request.POST, instance=estilo_vida)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Estilo de vida actualizado.')
            return redirect('perfil')
    else:
        form = EstiloVidaUsuarioForm(instance=estilo_vida)
    return render(request, 'Perfil/editar_estilo_vida.html', {'form': form})

def obtener_seguidores(request, perfil_id):
    seguidores = SeguimientoUsuario.objects.filter(seguido_id=perfil_id, vigente=True).select_related("seguidor")
    yo_sigo_ids = set(SeguimientoUsuario.objects.filter(seguidor=request.user, vigente=True).values_list("seguido_id", flat=True))
    data = [{"id": s.seguidor.id, "username": s.seguidor.username, "foto": s.seguidor.foto.url if s.seguidor.foto else "/media/avatar.png", "lo_sigo": s.seguidor.id in yo_sigo_ids} for s in seguidores]
    return JsonResponse({"usuarios": data})

def obtener_siguiendo(request, perfil_id):
    seguidos = SeguimientoUsuario.objects.filter(seguidor_id=perfil_id, vigente=True).select_related("seguido")
    yo_sigo_ids = set(SeguimientoUsuario.objects.filter(seguidor=request.user, vigente=True).values_list("seguido_id", flat=True))
    data = [{"id": s.seguido.id, "username": s.seguido.username, "foto": s.seguido.foto.url if s.seguido.foto else "/media/avatar.png", "lo_sigo": s.seguido.id in yo_sigo_ids} for s in seguidos]
    return JsonResponse({"usuarios": data})


# ==============================================================
# MENSAJERÍA Y NOTIFICACIONES (ORIGINALES)
# ==============================================================

@login_required
def mensajes_inbox(request):
    user = request.user
    mensajes = MensajePrivado.objects.filter(Q(emisor=user) | Q(receptor=user)).select_related("emisor", "receptor").order_by("-fecha_envio")
    conversaciones = {}
    for m in mensajes:
        partner = m.receptor if m.emisor == user else m.emisor
        if partner.id not in conversaciones:
            conversaciones[partner.id] = {"perfil": partner, "last_message": m, "unread": 0}
        if m.receptor == user and not m.leido:
            conversaciones[partner.id]["unread"] += 1
    return render(request, "Red/mensajes_inbox.html", {"conversaciones": sorted(conversaciones.values(), key=lambda x: x["last_message"].fecha_envio, reverse=True)})

@login_required
def mensajes_conversacion(request, perfil_id):
    user = request.user
    other = get_object_or_404(Perfil, pk=perfil_id)
    msgs = MensajePrivado.objects.filter((Q(emisor=user) & Q(receptor=other)) | (Q(emisor=other) & Q(receptor=user))).order_by("fecha_envio")
    paginator = Paginator(msgs, 20)
    page_obj = paginator.get_page(request.GET.get("page") or paginator.num_pages)
    
    # Marcar leídos
    MensajePrivado.objects.filter(id__in=[m.id for m in page_obj.object_list], receptor=user, leido=False).update(leido=True)
    
    return render(request, "Red/mensajes_conversacion.html", {"other": other, "user": user, "mensajes": page_obj.object_list, "page_obj": page_obj})

@login_required
def cargar_mensajes(request, perfil_id):
    user = request.user
    other = get_object_or_404(Perfil, pk=perfil_id)
    msgs = MensajePrivado.objects.filter((Q(emisor=user) & Q(receptor=other)) | (Q(emisor=other) & Q(receptor=user))).order_by("fecha_envio")
    page_obj = Paginator(msgs, 20).get_page(request.GET.get("page", 1))
    
    data = [{
        "id": m.id, "emisor_id": m.emisor.id, "emisor": m.emisor.username, "contenido": m.contenido,
        "foto": m.emisor.foto.url if m.emisor.foto else "/media/avatar.png",
        "fecha_envio": m.fecha_envio.strftime("%d/%m/%Y %H:%M")
    } for m in page_obj.object_list]
    
    return JsonResponse({"messages": data, "has_next": page_obj.has_next()})

@login_required
def enviar_mensaje(request):
    if request.method != "POST": return JsonResponse({"error": "POST required"}, status=405)
    receptor_id = request.POST.get("receptor_id")
    contenido = request.POST.get("contenido", "").strip()
    if not receptor_id or not contenido: return JsonResponse({"error": "Datos faltantes"}, status=400)
    
    receptor = get_object_or_404(Perfil, pk=receptor_id)
        
    msg = MensajePrivado.objects.create(emisor=request.user, receptor=receptor, contenido=contenido)

    return JsonResponse({
        "success": True, 
        "emisor": request.user.first_name or request.user.username, # <--- IMPORTANTE
        "contenido": msg.contenido, 
        "fecha_envio": msg.fecha_envio.strftime("%d/%m/%Y %H:%M")
    })

@login_required
def obtener_nuevos_mensajes(request, perfil_id):
    user = request.user
    other = get_object_or_404(Perfil, pk=perfil_id)
    
    ultimo_id = request.GET.get("ultimo_id", 0) 
    
    try:
        ultimo_id = int(ultimo_id)
    except ValueError:
        ultimo_id = 0
    nuevos = MensajePrivado.objects.filter(
        (Q(emisor=user) & Q(receptor=other)) | (Q(emisor=other) & Q(receptor=user)), 
        id__gt=ultimo_id
    ).order_by("fecha_envio")
    
    # Marcar como leídos los que recibo
    MensajePrivado.objects.filter(id__in=[m.id for m in nuevos if m.receptor == user]).update(leido=True)
    
    data = [{
        "id": m.id, 
        "emisor_id": m.emisor.id, 
        "emisor": m.emisor.first_name or m.emisor.username,
        "contenido": m.contenido, 
        "fecha_envio": m.fecha_envio.strftime("%d/%m/%Y %H:%M"),
        "foto": m.emisor.foto.url if m.emisor.foto else "/media/avatar.png"
    } for m in nuevos]
    
    return JsonResponse({"messages": data})

@login_required
def mensajes_quick(request):
    user = request.user
    mensajes = MensajePrivado.objects.filter(Q(emisor=user) | Q(receptor=user)).order_by('-fecha_envio')
    conversaciones = {}
    for m in mensajes:
        other = m.receptor if m.emisor == user else m.emisor
        if other.id not in conversaciones:
            conversaciones[other.id] = {
                "id": other.id, "usuario": other.username, "foto": other.foto.url if other.foto else "/media/avatar.png",
                "ultimo": m.contenido[:40], "hora": m.fecha_envio.strftime("%H:%M"), "unread": 0
            }
        if m.receptor == user and not m.leido: conversaciones[other.id]["unread"] += 1
    return JsonResponse(list(conversaciones.values()), safe=False)

# Notificaciones AJAX
@login_required
@require_GET
def notifications_list(request):
    qs = Notificacion.objects.filter(perfil_destino=request.user).order_by('-fecha')[:20]
    data = [{'id': n.id, 'tipo': n.tipo, 'mensaje': n.mensaje, 'leida': n.leida, 'fecha': n.fecha.strftime('%Y-%m-%d %H:%M')} for n in qs]
    return JsonResponse({'notifications': data})

@login_required
@require_GET
def notifications_unread_count(request):
    return JsonResponse({'unread_count': Notificacion.objects.filter(perfil_destino=request.user, leida=False).count()})

@login_required
@require_POST
def notification_mark_read(request, pk):
    Notificacion.objects.filter(pk=pk, perfil_destino=request.user).update(leida=True)
    return JsonResponse({'success': True})

@login_required
@require_POST
def notifications_mark_all_read(request):
    Notificacion.objects.filter(perfil_destino=request.user, leida=False).update(leida=True)
    return JsonResponse({'success': True})


# ==============================================================
# UTILIDADES API EXTERNAS
# ==============================================================

@login_required
def g_Dieta(request):
    datos_api = None
    error = None
    recetas_api = []
    recetas_error = None
    query = request.GET.get('query')
    
    # Variable para pasar los datos limpios a JS
    base_data_json = None 
    # Contexto para el gráfico
    chart_data = None 

    if query:
        # 1. CalorieNinjas (Nutrición)
        url = f"https://api.calorieninjas.com/v1/nutrition?query={query}"
        try:
            # Tu API Key real
            response = requests.get(url, headers={'X-Api-Key': 'EF5l3OdGqCzyoN5vul8PfQ==Qve6OpEs17pZal3b'}) 
            
            if response.status_code == 200: 
                items = response.json().get('items', [])
                if items:
                    datos_api = items[0] # Tomamos el primer resultado
                    
                    base_data_json = json.dumps({
                        'name': datos_api['name'],
                        'grams': datos_api['serving_size_g'],
                        'cal': datos_api['calories'],
                        'prot': datos_api['protein_g'],
                        'carb': datos_api['carbohydrates_total_g'],
                        'fat': datos_api['fat_total_g']
                    })

                    # Datos solo para chart si los usabas aparte
                    chart_data = json.dumps({
                        'prot': datos_api['protein_g'],
                        'carb': datos_api['carbohydrates_total_g'],
                        'fat': datos_api['fat_total_g']
                    })
            else: 
                error = f"Error CalorieNinjas: {response.status_code}"
        except Exception as e: 
            error = str(e)
        
        # 2. Spoonacular (Recetas)
        # Tu API Key real
        receta_url = f"https://api.spoonacular.com/recipes/complexSearch?query={query}&apiKey=dc4aa01ef6814468a7fb1ef61e9d3826&addRecipeInformation=true&number=3"
        try:
            rr = requests.get(receta_url)
            if rr.status_code == 200:
                recetas_api = rr.json().get('results', [])
            else: 
                recetas_error = f"Error Spoonacular: {rr.status_code}"
        except Exception as e: 
            recetas_error = str(e)

    return render(request, 'Social/g_Dieta.html', {
        'datos_api': datos_api, 
        'base_data_json': base_data_json, # Pasamos el JSON seguro a la plantilla
        'chart_data': chart_data,
        'error': error, 
        'query': query, 
        'recetas_api': recetas_api, 
        'recetas_error': recetas_error
    })

# ==========================================
# GUARDAR EN DB (AJAX)
# ==========================================
@login_required
@csrf_exempt
def guardar_alimento_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # Obtener el perfil del usuario actual
            # Dado que Perfil hereda de AbstractUser, request.user es una instancia de Perfil
            perfil = request.user 

            nuevo_registro = NutricionRegistro.objects.create(
                perfil=perfil,
                fecha=date.today(),
                comida=data.get('nombre'),
                calorias=data.get('calorias'),
                proteinas=data.get('proteinas'),
                carbohidratos=data.get('carbos'),
                grasas=data.get('grasas'),
                descripcion=f"Registrado desde Lab Nutricional ({data.get('gramos')}g)"
            )
            return JsonResponse({'status': 'success', 'msg': 'Alimento registrado correctamente'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)})
            
    return JsonResponse({'status': 'error', 'msg': 'Método no permitido'})

def g_Ejercicio(request):
    return render(request, 'Social/g_Ejercicio.html')


# ==============================================================
# SIGNALS (NOTIFICACIONES AUTOMÁTICAS)
# ==============================================================

@receiver(post_save, sender=SeguimientoUsuario)
def create_follow_notification(sender, instance, created, **kwargs):
    if created and instance.seguidor != instance.seguido:
        Notificacion.objects.create(perfil_destino=instance.seguido, perfil_origen=instance.seguidor, tipo='follow', mensaje=f'{instance.seguidor.username} te siguió.')

@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    if created and instance.perfil != instance.publicacion.perfil:
        Notificacion.objects.create(perfil_destino=instance.publicacion.perfil, perfil_origen=instance.perfil, tipo='like', mensaje=f'{instance.perfil.username} le dio like a tu post.')

@receiver(post_save, sender=Comentario)
def create_comment_notification(sender, instance, created, **kwargs):
    if created and instance.perfil != instance.publicacion.perfil:
        Notificacion.objects.create(perfil_destino=instance.publicacion.perfil, perfil_origen=instance.perfil, tipo='comment', mensaje=f'{instance.perfil.username} comentó tu post.')

@login_required
def notifications_list_view(request):
    # Obtener todas las notificaciones del usuario, las más nuevas primero
    notifs_list = Notificacion.objects.filter(perfil_destino=request.user).order_by('-fecha')
    
    # Paginación: Mostrar 15 por página
    paginator = Paginator(notifs_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'Social/notifications_list.html', {'page_obj': page_obj})