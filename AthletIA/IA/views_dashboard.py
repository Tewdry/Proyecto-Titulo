from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import date, timedelta
from django.utils.timezone import now
from App.models import (
    ProgresoUsuario,
    ObjetivoUsuario, SuenoUsuario, SaludUsuario, NutricionRegistro
)
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.serializers.json import DjangoJSONEncoder
from api_ejercicio.models import CalendarioRutina, ProgresoEjercicio


@login_required
def dashboard_view(request):
    perfil = request.user

    # Último estado de salud
    salud = SaludUsuario.objects.filter(perfil=perfil).order_by("-fecha_actualizacion").first()

    # Objetivo activo
    objetivo = ObjetivoUsuario.objects.filter(
        perfil=perfil, activo=True
    ).select_related("tipo_objetivo").first()

    # Historial de peso para el gráfico (mantiene orden cronológico)
    historial_peso = list(
        ProgresoUsuario.objects.filter(perfil=perfil, peso_kg__isnull=False)
        .order_by("fecha")
        .values("fecha", "peso_kg", "comentario")
    )
    historial_peso_json = json.dumps(historial_peso, cls=DjangoJSONEncoder)

    return render(request, "IA/dashboard.html", {
        "salud": salud,
        "objetivo": objetivo,
        "historial_peso_json": historial_peso_json,
    })

# ==========================================================
# KPI PRINCIPALES DEL USUARIO
# ==========================================================
@login_required
def obtener_kpi_dashboard(request):
    perfil = request.user
    hoy = date.today()

    # RUTINAS SEMANA ACTUAL ░░
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)

    rutinas_semana = CalendarioRutina.objects.filter(
        perfil=perfil,
        fecha__range=(inicio_semana, fin_semana),
        completada=True
    ).count()

    # Objetivo semanal (por defecto 3)
    objetivo_semana = 3
    cumplimiento = round((rutinas_semana / objetivo_semana) * 100) if objetivo_semana > 0 else 0

    if cumplimiento < 30:
        texto_cumplimiento = "Vas lento hoy, pero puedes remontar."
    elif cumplimiento < 70:
        texto_cumplimiento = "Buen ritmo."
    else:
        texto_cumplimiento = "🔥 Estás rompiéndola esta semana."

    # RACHA DE ENTRENAMIENTO (DÍAS SEGUIDOS)
    racha = 0
    dias_retroceso = 0
    fecha_iterada = hoy

    while dias_retroceso < 30:  
        completada = CalendarioRutina.objects.filter(
            perfil=perfil,
            fecha=fecha_iterada,
            completada=True
        ).exists()

        if completada:
            racha += 1
        else:
            break

        fecha_iterada -= timedelta(days=1)
        dias_retroceso += 1

    # MINUTOS ENTRENADOS (ÚLTIMOS 7 DÍAS)
    hace_7 = hoy - timedelta(days=6)

    progreso = ProgresoEjercicio.objects.filter(
        perfil=perfil,
        fecha__range=(hace_7, hoy)
    ).values_list("duracion_minutos", flat=True)

    minutos_7dias = sum([m for m in progreso if m])

    # LOGROS DESBLOQUEADOS
    logros = []
    if rutinas_semana >= objetivo_semana:
        logros.append("Objetivo semanal cumplido")
    if racha >= 5:
        logros.append("🔥 Racha de 5+ días")
    if minutos_7dias >= 150:
        logros.append("150 minutos esta semana")

    # PRÓXIMAS 3 RUTINAS
    proximas = CalendarioRutina.objects.filter(
        perfil=perfil,
        fecha__gte=hoy
    ).order_by("fecha")[:3]

    proximas_rutinas = [{
        "nombre": r.rutina.nombre,
        "fecha": r.fecha.strftime("%d/%m"),
        "hora": r.hora.strftime("%H:%M") if r.hora else None
    } for r in proximas]

    return JsonResponse({
        "rutinas_semana": rutinas_semana,
        "objetivo_semana": objetivo_semana,
        "cumplimiento": cumplimiento,
        "cumplimiento_texto": texto_cumplimiento,
        "racha": racha,
        "minutos_7dias": minutos_7dias,
        "logros": logros,
        "proximas_rutinas": proximas_rutinas
    })
    

# ==========================================================
# DATOS PARA GRÁFICOS DEL DASHBOARD PRO
# ==========================================================
@login_required
def datos_graficos_dashboard(request):
    perfil = request.user
    hoy = date.today()

    # GRAFICO 14 DÍAS
    fechas_14 = [(hoy - timedelta(days=i)) for i in range(13, -1, -1)]
    labels_14 = [f.strftime("%d/%m") for f in fechas_14]

    valores_14 = []
    for f in fechas_14:
        count = CalendarioRutina.objects.filter(
            perfil=perfil,
            fecha=f,
            completada=True
        ).count()
        valores_14.append(count)

    # GRAFICO DE MINUTOS - 8 SEMANAS
    semanas_labels = []
    semanas_valores = []

    for i in range(7, -1, -1):
        inicio = hoy - timedelta(days=i*7)
        fin = inicio + timedelta(days=6)

        semanas_labels.append(f"S{i+1}")
        minutos = ProgresoEjercicio.objects.filter(
            perfil=perfil,
            fecha__range=(inicio, fin)
        ).values_list("duracion_minutos", flat=True)

        semanas_valores.append(sum([m for m in minutos if m]))

    # MÚSCULOS MÁS ENTRENADOS
    progresos = ProgresoEjercicio.objects.filter(perfil=perfil).select_related("ejercicio")

    musculo_contador = {}

    for p in progresos:
        mus = p.ejercicio.musculo.nombre
        musculo_contador[mus] = musculo_contador.get(mus, 0) + 1

    musculos_labels = list(musculo_contador.keys())
    musculos_valores = list(musculo_contador.values())

    return JsonResponse({
        "rutinas_14d": {
            "fechas": labels_14,
            "valores": valores_14
        },
        "minutos_8s": {
            "semanas": semanas_labels,
            "valores": semanas_valores
        },
        "musculos": {
            "labels": musculos_labels,
            "valores": musculos_valores
        }
    })