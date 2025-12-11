import json
from datetime import date, timedelta, datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
import traceback
import os
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.shortcuts import redirect
from django.conf import settings
from App.models import Perfil
from api_ejercicio.models import Rutina, CalendarioRutina, RutinaEjercicio, RutinaGuardada

# ==========================================================
# Vista principal del calendario (HTML)
# ==========================================================
@login_required
def calendario_view(request):
    return render(request, "IA/calendario.html")


# ==========================================================
# Registrar rutina en calendario (Endpoint)
# ==========================================================
@csrf_exempt
@login_required
@require_http_methods(["POST"])
def registrar_rutina_calendario(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        fecha_str = data.get("fecha")
        rutina_id = data.get("rutina_id")
        notas = data.get("notas", "")
        hora = data.get("hora")

        if not fecha_str or not rutina_id:
            return JsonResponse({"success": False, "error": "Fecha y rutina son obligatorias."}, status=400)

        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"success": False, "error": "Formato de fecha inválido."}, status=400)

        perfil = Perfil.objects.get(id=request.user.id)
        rutina = Rutina.objects.get(id=rutina_id)

        if not rutina.vigente:
            return JsonResponse({"success": False, "error": "No se puede asignar una rutina desactivada."}, status=400)

        obj, created = CalendarioRutina.objects.get_or_create(
            perfil=perfil,
            rutina=rutina,
            fecha=fecha,
            defaults={"hora": hora, "notas": notas}
        )

        return JsonResponse({
            "success": True,
            "message": "Rutina registrada correctamente." if created else "Ya existía una rutina para esa fecha."
        })
    except Rutina.DoesNotExist:
        return JsonResponse({"success": False, "error": "La rutina seleccionada no existe."}, status=404)
    except Exception as e:
        print("🔥 ERROR registrar_rutina_calendario:", traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# ==========================================================
# Obtener eventos del calendario (JSON)
# ==========================================================
@login_required
def obtener_calendario(request):
    try:
        perfil = Perfil.objects.get(id=request.user.id)
        rutinas = (
            CalendarioRutina.objects
            .filter(perfil=perfil)
            .select_related("rutina", "rutina__nivel_dificultad")
            .order_by("fecha")
        )

        eventos = []
        for r in rutinas:
            ejercicios_qs = (
                RutinaEjercicio.objects
                .filter(rutina=r.rutina)
                .select_related("ejercicio")
                .values("ejercicio__nombre", "ejercicio__descripcion")
            )

            ejercicios = [
                {
                    "nombre": e["ejercicio__nombre"],
                    "descripcion": e["ejercicio__descripcion"] or "Sin descripción disponible."
                }
                for e in ejercicios_qs
            ]

            eventos.append({
                "id": r.id,
                "title": f"🏋️ {r.rutina.nombre}",
                "start": r.fecha.strftime("%Y-%m-%d"),
                "color": "#00b894" if r.completada else "#25e2d7",
                "textColor": "#003135",
                "extendedProps": {
                    "completada": r.completada,
                    "notas": r.notas or "",
                    "hora": str(r.hora) if r.hora else "",
                    "ejercicios": ejercicios,
                    "rutina_id": r.rutina.id,
                    "propietario": r.rutina.perfil.username,
                    "es_mia": (r.rutina.perfil_id == request.user.id),
                    "vigente": r.rutina.vigente,
                }
            })

        return JsonResponse(eventos, safe=False)
    except Exception as e:
        print("🔥 ERROR obtener_calendario:", traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)


# ==========================================================
# Registrar rutina MANUAL (Endpoint específico)
# ==========================================================
@csrf_exempt
@login_required
@require_http_methods(["POST"])
def registrar_rutina_calendario_manual(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        fecha_str = data.get("fecha")
        rutina_id = data.get("rutina_id")
        notas = data.get("notas", "")
        hora = data.get("hora")

        if not fecha_str or not rutina_id:
            return JsonResponse({"success": False, "error": "Fecha y rutina son obligatorias."}, status=400)

        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"success": False, "error": "Formato de fecha inválido."}, status=400)

        perfil = Perfil.objects.get(id=request.user.id)
        rutina = Rutina.objects.get(id=rutina_id)

        if not rutina.vigente:
            return JsonResponse({"success": False, "error": "No se puede asignar una rutina desactivada."}, status=400)

        existente = CalendarioRutina.objects.filter(perfil=perfil, fecha=fecha).first()
        if existente:
            existente.rutina = rutina
            existente.notas = notas
            existente.hora = hora
            existente.save()
            return JsonResponse({
                "success": True,
                "message": "Rutina manual actualizada en el calendario."
            })

        CalendarioRutina.objects.create(
            perfil=perfil,
            rutina=rutina,
            fecha=fecha,
            notas=notas,
            hora=hora
        )

        return JsonResponse({
            "success": True,
            "message": "Rutina manual registrada correctamente."
        })

    except Rutina.DoesNotExist:
        return JsonResponse({"success": False, "error": "La rutina seleccionada no existe."}, status=404)
    except Exception as e:
        print("🔥 ERROR registrar_rutina_calendario_manual:", traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# ==========================================================
# Obtener calendario MANUAL (ESTA ES LA QUE FALTABA)
# ==========================================================
@login_required
def obtener_calendario_manual(request):
    """
    Devuelve los eventos para el calendario manual.
    En la práctica es igual a obtener_calendario, pero se mantiene
    por compatibilidad con las URLs definidas.
    """
    return obtener_calendario(request)


# ==========================================================
# Actualizar estado/notas de rutina en calendario
# ==========================================================
@csrf_exempt
@login_required
@require_http_methods(["POST"])
def actualizar_rutina_calendario(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        rutina_id = data.get("id")
        notas = data.get("notas", "")
        completada = bool(data.get("completada", False))
        perfil = Perfil.objects.get(id=request.user.id)

        if not rutina_id:
            return JsonResponse({"success": False, "error": "ID de evento no proporcionado."}, status=400)

        with transaction.atomic():
            evento = CalendarioRutina.objects.get(id=rutina_id, perfil=perfil)
            evento.notas = notas
            evento.completada = completada
            evento.save()

        return JsonResponse({"success": True, "message": "Rutina actualizada correctamente."})
    except CalendarioRutina.DoesNotExist:
        return JsonResponse({"success": False, "error": "No se encontró la rutina seleccionada."}, status=404)
    except Exception as e:
        print("🔥 ERROR actualizar_rutina_calendario:", traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# ==========================================================
# KPI MENSUAL
# ==========================================================
@login_required
def obtener_kpi_mensual(request):
    try:
        perfil = Perfil.objects.get(id=request.user.id)
        hoy = date.today()

        inicio_mes = hoy.replace(day=1)
        if hoy.month == 12:
            fin_mes = hoy.replace(year=hoy.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            fin_mes = hoy.replace(month=hoy.month + 1, day=1) - timedelta(days=1)

        rutinas_mes = CalendarioRutina.objects.filter(
            perfil=perfil,
            fecha__range=[inicio_mes, fin_mes]
        )

        total = rutinas_mes.count()
        completadas = rutinas_mes.filter(completada=True).count()
        pendientes = total - completadas
        cumplimiento = round((completadas / total) * 100, 1) if total > 0 else 0

        dias_completados = {}
        for r in rutinas_mes.filter(completada=True):
            dia = r.fecha.day
            dias_completados[dia] = dias_completados.get(dia, 0) + 1

        data = {
            "mes": hoy.strftime("%B %Y").capitalize(),
            "inicio_mes": inicio_mes.strftime("%d-%m-%Y"),
            "fin_mes": fin_mes.strftime("%d-%m-%Y"),
            "total": total,
            "completadas": completadas,
            "pendientes": pendientes,
            "cumplimiento": cumplimiento,
            "dias_completados": dias_completados,
        }

        return JsonResponse(data)
    except Exception as e:
        print("🔥 ERROR obtener_kpi_mensual:", traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)


# ==========================================================
# Guardar Rutina en Perfil (FAVORITOS)
# ==========================================================
@csrf_exempt
@login_required
@require_http_methods(["POST"])
def guardar_rutina_en_perfil(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        rutina_id = data.get("rutina_id")

        if not rutina_id:
            return JsonResponse({"success": False, "error": "ID de rutina no proporcionado."}, status=400)

        rutina = Rutina.objects.get(id=rutina_id)
        perfil = request.user

        if rutina.perfil_id == perfil.id:
            return JsonResponse({
                "success": False,
                "error": "No necesitas guardar tus propias rutinas. Ya están en 'Mis Rutinas'."
            }, status=400)

        if not rutina.vigente:
            return JsonResponse({"success": False, "error": "No se puede guardar una rutina desactivada."}, status=400)

        guardada, creada = RutinaGuardada.objects.get_or_create(
            rutina=rutina,
            perfil=perfil
        )

        total_guardadas = RutinaGuardada.objects.filter(rutina=rutina).count()

        return JsonResponse({
            "success": True,
            "message": "Rutina guardada correctamente." if creada else "Ya la tenías guardada.",
            "total_guardadas": total_guardadas,
            "ya_guardada": not creada
        })
    except Rutina.DoesNotExist:
        return JsonResponse({"success": False, "error": "Rutina no encontrada."}, status=404)
    except Exception as e:
        print("🔥 ERROR guardar_rutina_en_perfil:", traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def obtener_rutinas_guardadas(request):
    try:
        guardadas = (
            RutinaGuardada.objects
            .filter(perfil=request.user, rutina__vigente=True)
            .select_related("rutina", "rutina__nivel_dificultad")
            .order_by("-fecha_guardado")
        )

        data = []
        for g in guardadas:
            ejercicios = (
                RutinaEjercicio.objects
                .filter(rutina=g.rutina)
                .select_related("ejercicio")
                .values("ejercicio__nombre", "ejercicio__descripcion")
            )
            data.append({
                "id": g.rutina.id,
                "nombre": g.rutina.nombre,
                "descripcion": g.rutina.descripcion or "",
                "nivel": g.rutina.nivel_dificultad.nombre if g.rutina.nivel_dificultad else "Sin nivel",
                "ejercicios": list(ejercicios),
                "fecha_guardado": g.fecha_guardado.strftime("%d/%m/%Y"),
            })

        return JsonResponse(data, safe=False)

    except Exception as e:
        print("⚠️ Error en obtener_rutinas_guardadas:", traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def eliminar_rutina_guardada(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        rutina_id = data.get("rutina_id")

        if not rutina_id:
            return JsonResponse({"success": False, "error": "ID de rutina no proporcionado."}, status=400)

        deleted, _ = RutinaGuardada.objects.filter(rutina_id=rutina_id, perfil=request.user).delete()

        if deleted == 0:
            return JsonResponse({
                "success": False,
                "error": "Esta rutina no estaba en tus guardadas."
            }, status=404)

        return JsonResponse({
            "success": True,
            "message": "Rutina quitada de tus guardadas."
        })

    except Exception as e:
        print("⚠️ Error en eliminar_rutina_guardada:", traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# ==========================================================
# Asignar rutina guardada a fecha
# ==========================================================
@csrf_exempt
@login_required
def asignar_rutina_guardada(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        fecha_str = data.get("fecha")
        rutina_id = data.get("rutina_id")
        reemplazar = bool(data.get("reemplazar", False))

        if not fecha_str or not rutina_id:
            return JsonResponse(
                {"success": False, "error": "Fecha y rutina son obligatorias."},
                status=400
            )

        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse(
                {"success": False, "error": "Formato de fecha inválido."},
                status=400
            )

        rutina = Rutina.objects.get(id=rutina_id)

        if not rutina.vigente:
            return JsonResponse(
                {"success": False, "error": "No se puede asignar una rutina desactivada."},
                status=400
            )

        existentes_dia = CalendarioRutina.objects.filter(
            perfil=request.user,
            fecha=fecha
        )

        if existentes_dia.filter(rutina=rutina).exists() and not reemplazar:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Ya tienes esta misma rutina asignada en esa fecha."
                },
                status=400
            )

        if existentes_dia.exists() and not reemplazar:
            return JsonResponse(
                {
                    "success": False,
                    "requires_confirm": True,
                    "message": "Ya tienes una rutina asignada ese día. ¿Deseas reemplazarla por esta?"
                },
                status=200
            )

        if existentes_dia.exists() and reemplazar:
            existentes_dia.delete()

        CalendarioRutina.objects.create(
            perfil=request.user,
            rutina=rutina,
            fecha=fecha,
            completada=False
        )

        return JsonResponse(
            {
                "success": True,
                "message": f"La rutina '{rutina.nombre}' fue asignada al {fecha}.",
                "reemplazo": reemplazar,
            }
        )

    except Rutina.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Rutina no encontrada."},
            status=404
        )
    except Exception as e:
        print("⚠️ Error en asignar_rutina_guardada:", traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# ==========================================================
# TENDENCIAS
# ==========================================================
@login_required
def obtener_tendencias(request):
    try:
        hoy = date.today()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + timedelta(days=6)

        tendencias = (
            CalendarioRutina.objects
            .filter(fecha__range=[inicio_semana, fin_semana])
            .values("rutina_id")
            .annotate(total_asignaciones=Count("rutina_id"))
            .order_by("-total_asignaciones")[:5]
        )

        resultados = []
        for t in tendencias:
            rutina = Rutina.objects.filter(id=t["rutina_id"], vigente=True).first()
            if rutina:
                resultados.append({
                    "id": rutina.id,
                    "nombre": rutina.nombre,
                    "nivel": getattr(rutina.nivel_dificultad, "nombre", "Desconocido"),
                    "descripcion": rutina.descripcion or "Sin descripción disponible",
                    "asignaciones": t["total_asignaciones"],
                })

        return JsonResponse({"success": True, "tendencias": resultados})

    except Exception as e:
        print("⚠️ ERROR en obtener_tendencias:", traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)})


# ==========================================================
# Info si una rutina está guardada
# ==========================================================
@login_required
def obtener_info_guardado(request):
    try:
        rutina_id = request.GET.get("rutina_id")
        if not rutina_id:
            return JsonResponse({"success": False, "error": "ID de rutina no proporcionado."}, status=400)

        rutina = Rutina.objects.get(id=rutina_id)
        perfil = request.user

        total_guardadas = RutinaGuardada.objects.filter(rutina=rutina).count()
        ya_guardada = RutinaGuardada.objects.filter(rutina=rutina, perfil=perfil).exists()

        return JsonResponse({
            "success": True,
            "total_guardadas": total_guardadas,
            "ya_guardada": ya_guardada
        })
    except Rutina.DoesNotExist:
        return JsonResponse({"success": False, "error": "Rutina no encontrada."}, status=404)
    except Exception as e:
        print("🔥 ERROR obtener_info_guardado:", traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
# ==========================================================
# Mover Rutina (Drag & Drop)
# ==========================================================
@csrf_exempt
@login_required
@require_http_methods(["POST"])
def mover_rutina_calendario(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        evento_id = data.get("id")
        nueva_fecha_str = data.get("nueva_fecha")

        if not evento_id or not nueva_fecha_str:
            return JsonResponse({"success": False, "error": "Datos incompletos."}, status=400)

        # Limpiar la fecha (por si FullCalendar manda formato ISO con hora 'T')
        if "T" in nueva_fecha_str:
            nueva_fecha_str = nueva_fecha_str.split("T")[0]

        try:
            nueva_fecha = datetime.strptime(nueva_fecha_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"success": False, "error": "Formato de fecha inválido."}, status=400)

        perfil = Perfil.objects.get(id=request.user.id)

        # Buscar el evento existente y actualizar su fecha
        evento = CalendarioRutina.objects.get(id=evento_id, perfil=perfil)
        evento.fecha = nueva_fecha
        evento.save()

        return JsonResponse({"success": True, "message": "Rutina movida correctamente."})

    except CalendarioRutina.DoesNotExist:
        return JsonResponse({"success": False, "error": "El evento no existe o no te pertenece."}, status=404)
    except Exception as e:
        print("🔥 ERROR mover_rutina_calendario:", traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
# ==========================================================
# INTEGRACIÓN GOOGLE CALENDAR
# ==========================================================

@login_required
def iniciar_google_auth(request):
    # Guardamos el ID del evento (CalendarioRutina) que quería sincronizar
    rutina_id = request.GET.get('rutina_id')
    if rutina_id:
        request.session['rutina_a_sincronizar'] = rutina_id

    # Usamos la configuración desde settings.py
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=settings.GOOGLE_API_SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    # Guardamos el estado para verificar CSRF
    request.session['google_auth_state'] = state
    
    return redirect(authorization_url)


@login_required
def google_callback(request):
    state = request.session.get('google_auth_state')
    
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=settings.GOOGLE_API_SCOPES,
        state=state,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )

    # Intercambiar el código por un token real
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    # Guardar credenciales en la sesión del usuario
    creds = flow.credentials
    request.session['google_creds'] = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

    # Si veníamos de intentar sincronizar una rutina específica, volvemos al calendario
    return redirect('ia:calendario_view')


@csrf_exempt
@login_required
def sincronizar_rutina_google(request):
    # Verificar si el usuario ya inició sesión con Google
    if 'google_creds' not in request.session:
        return JsonResponse({'success': False, 'auth_required': True})

    try:
        data = json.loads(request.body.decode("utf-8"))
        evento_id = data.get("id") # ID de CalendarioRutina (el evento en tu DB)
        
        # Obtener datos de la asignación en el calendario
        calendario_rutina = CalendarioRutina.objects.get(id=evento_id, perfil=request.user)
        rutina = calendario_rutina.rutina
        
        # Reconstruir credenciales desde la sesión
        creds_data = request.session['google_creds']
        creds = Credentials(
            token=creds_data['token'],
            refresh_token=creds_data.get('refresh_token'),
            token_uri=creds_data['token_uri'],
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret'],
            scopes=creds_data['scopes']
        )

        # Conectar con la API de Google
        service = build('calendar', 'v3', credentials=creds)

        # Construir descripción detallada con los ejercicios
        ejercicios = RutinaEjercicio.objects.filter(rutina=rutina)
        desc_texto = f"💪 Rutina: {rutina.nombre}\n🔥 Nivel: {rutina.nivel_dificultad}\n\n📝 Ejercicios a realizar:\n"
        
        for re in ejercicios:
            desc_texto += f"- {re.ejercicio.nombre} ({re.ejercicio.musculo})\n"
        
        if calendario_rutina.notas:
            desc_texto += f"\n📌 Notas personales: {calendario_rutina.notas}\n"
            
        desc_texto += "\n🚀 Generado por AthletIA"

        # Configurar fecha y hora del evento
        fecha_inicio = calendario_rutina.fecha.strftime("%Y-%m-%d")
        
        if calendario_rutina.hora:
            # Si el usuario definió una hora específica
            hora_str = calendario_rutina.hora.strftime("%H:%M:%S")
            start_dt = f"{fecha_inicio}T{hora_str}"
            # Calculamos 1 hora y media de duración por defecto
            end_dt = (datetime.combine(calendario_rutina.fecha, calendario_rutina.hora) + timedelta(minutes=90)).isoformat()
            
            event_body = {
                'summary': f'🏋️ AthletIA: {rutina.nombre}',
                'location': 'Gimnasio / Smart Fit',
                'description': desc_texto,
                'start': {'dateTime': start_dt, 'timeZone': 'America/Santiago'}, # Zona horaria de Chile
                'end': {'dateTime': end_dt, 'timeZone': 'America/Santiago'},
                'reminders': {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': 45}]}
            }
        else:
            # Si es evento de día completo
            event_body = {
                'summary': f'🏋️ AthletIA: {rutina.nombre}',
                'location': 'Gimnasio / Smart Fit',
                'description': desc_texto,
                'start': {'date': fecha_inicio},
                'end': {'date': fecha_inicio},
            }

        # Insertar evento en el calendario principal ("primary")
        event = service.events().insert(calendarId='primary', body=event_body).execute()

        return JsonResponse({'success': True, 'link': event.get('htmlLink')})

    except Exception as e:
        print("🔥 Error Google Calendar:", traceback.format_exc())
        # Si el token expiró o hay error de credenciales, pedimos loguear de nuevo
        if "invalid_grant" in str(e) or "Unauthorized" in str(e):
             return JsonResponse({'success': False, 'auth_required': True})
             
        return JsonResponse({'success': False, 'error': str(e)})