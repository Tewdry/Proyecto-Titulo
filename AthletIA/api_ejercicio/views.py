from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.urls import reverse
from django.contrib import messages

from App.models import ObjetivoUsuario, Perfil, ProgresoUsuario
from api_ejercicio.forms import *
from api_ejercicio.models import *

@login_required
def generar_rutina(request):
    perfil = Perfil.objects.get(id=request.user.id)
    progreso = ProgresoUsuario.objects.filter(perfil=perfil).first()
    objetivo = ObjetivoUsuario.objects.filter(perfil=perfil, activo=True).first()
    salud = getattr(perfil, 'salud_usuario', None)

    if progreso and objetivo and salud and progreso.peso_kg and progreso.altura_cm:
        return redirect('recomendador_view')

    return render(request, 'IA/stepper_rutina.html', {"perfil": perfil})

@login_required
def mapa_corporal(request):
    return render(request, 'api_ejercicio/mapa_corporal.html')


def musculo_detalle(request, nombre):
    # nombre viene como slug: "cuerpo-completo" -> "cuerpo completo"
    nombre_limpio = nombre.replace('-', ' ')
    musculo = get_object_or_404(Musculo, nombre__iexact=nombre_limpio)

    ejercicios = (
        Ejercicio.objects
        .filter(musculo=musculo, vigente=True)
        .select_related("tipo_ejercicio", "nivel_dificultad")
        .order_by("nombre")
    )

    # IDs de tipos y niveles que realmente se usan en estos ejercicios
    tipos_ids = ejercicios.values_list("tipo_ejercicio_id", flat=True).distinct()

    niveles_ids = (
        ejercicios
        .filter(nivel_dificultad__isnull=False)
        .values_list("nivel_dificultad__pk", flat=True)
        .distinct()
    )

    tipos = TipoEjercicio.objects.filter(id__in=tipos_ids)
    niveles = NivelDificultad.objects.filter(pk__in=niveles_ids)

    return render(request, "api_ejercicio/musculo_detalle.html", {
        "musculo": musculo,
        "ejercicios": ejercicios,
        "tipos": tipos,
        "niveles": niveles,
    })