from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from api_ejercicio.models import (
    Rutina,
    RutinaEjercicio,
    Ejercicio,
    RutinaGuardada,
    CalendarioRutina,
)
import json
import traceback


@login_required
def ver_rutina_detalle(request, rutina_id):
    rutina = get_object_or_404(Rutina, id=rutina_id)

    ejercicios_qs = (
        RutinaEjercicio.objects
        .filter(rutina=rutina)
        .select_related("ejercicio")
        .values(
            "ejercicio__id",
            "ejercicio__nombre",
            "ejercicio__descripcion",
            "ejercicio__musculo__nombre",
            "ejercicio__nivel_dificultad__nombre"
        )
    )

    ejercicios = []
    for e in ejercicios_qs:
        # Manejo seguro de None
        musculo = e.get("ejercicio__musculo__nombre") or "General"
        nivel = e.get("ejercicio__nivel_dificultad__nombre") or "Básico"
        
        ejercicios.append({
            "id": e["ejercicio__id"],
            "nombre": e["ejercicio__nombre"],
            "descripcion": e["ejercicio__descripcion"] or "",
            "musculo": musculo,
            "nivel": nivel,
        })

    return JsonResponse({
        "success": True,
        "rutina": {
            "id": rutina.id,
            "nombre": rutina.nombre,
            "descripcion": rutina.descripcion,
            "nivel": rutina.nivel_dificultad.nombre if rutina.nivel_dificultad else "",
            "fecha_creacion": rutina.fecha_creacion.strftime("%d/%m/%Y"),
            "total_ejercicios": len(ejercicios),
            "ejercicios": ejercicios,
        }
    })


@csrf_exempt
@login_required
@require_POST
def editar_rutina(request):
    try:
        data = json.loads(request.body.decode("utf-8"))

        rutina_id = data.get("rutina_id")
        nuevo_nombre = (data.get("nombre") or "").strip()
        nueva_desc = (data.get("descripcion") or "").strip()
        nuevos_ejercicios = data.get("ejercicios", [])

        if not rutina_id:
            return JsonResponse({"success": False, "error": "ID de rutina no proporcionado."}, status=400)

        if not nuevo_nombre:
            return JsonResponse({"success": False, "error": "El nombre de la rutina no puede estar vacío."}, status=400)

        # Verificar propiedad
        rutina = Rutina.objects.get(id=rutina_id, perfil=request.user)

        # Actualizar nombre y descripción
        rutina.nombre = nuevo_nombre
        rutina.descripcion = nueva_desc or rutina.descripcion
        rutina.save()

        # Resetear ejercicios (Borrar y crear)
        RutinaEjercicio.objects.filter(rutina=rutina).delete()

        # Insertar nuevos ejercicios
        for e in nuevos_ejercicios:
            ej_id = e.get("id")
            if ej_id:
                try:
                    ej = Ejercicio.objects.get(id=ej_id)
                    RutinaEjercicio.objects.create(rutina=rutina, ejercicio=ej)
                except Ejercicio.DoesNotExist:
                    continue 

        return JsonResponse({
            "success": True,
            "message": "Rutina actualizada correctamente."
        })

    except Rutina.DoesNotExist:
        return JsonResponse({"success": False, "error": "La rutina no existe o no es tuya."}, status=404)
    except Exception as e:
        print("🔥 ERROR editar_rutina:", traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@login_required
@require_POST
def duplicar_rutina(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        rutina_id = data.get("rutina_id")

        if not rutina_id:
            return JsonResponse({"success": False, "error": "ID de rutina no proporcionado."}, status=400)

        rutina = Rutina.objects.get(id=rutina_id)

        if not rutina.vigente:
            return JsonResponse({"success": False, "error": "No se puede duplicar una rutina desactivada."}, status=400)

        # Crear copia
        nueva_rutina = Rutina.objects.create(
            nombre=f"{rutina.nombre} (Copia)",
            descripcion=rutina.descripcion,
            perfil=request.user,
            nivel_dificultad=rutina.nivel_dificultad,
            vigente=True,
        )

        # Copiar ejercicios
        ejercicios = RutinaEjercicio.objects.filter(rutina=rutina)
        for e in ejercicios:
            RutinaEjercicio.objects.create(
                rutina=nueva_rutina,
                ejercicio=e.ejercicio,
                repeticiones=e.repeticiones,
                orden=e.orden,
            )

        return JsonResponse({
            "success": True,
            "message": "Rutina duplicada correctamente.",
            "nueva_rutina_id": nueva_rutina.id,
            "nueva_rutina_nombre": nueva_rutina.nombre,
        })

    except Rutina.DoesNotExist:
        return JsonResponse({"success": False, "error": "Rutina no encontrada."}, status=404)
    except Exception as e:
        print("🔥 ERROR duplicar_rutina:", traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@login_required
@require_POST
def eliminar_rutina(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        rutina_id = data.get("rutina_id")

        if not rutina_id:
            return JsonResponse({"success": False, "error": "ID de rutina no proporcionado."}, status=400)

        rutina = Rutina.objects.get(id=rutina_id)

        if rutina.perfil != request.user:
            return JsonResponse({
                "success": False,
                "error": "No tienes permiso para eliminar esta rutina."
            }, status=403)

        rutina.vigente = False
        rutina.save()

        RutinaGuardada.objects.filter(rutina=rutina).delete()

        return JsonResponse({
            "success": True,
            "message": "Rutina desactivada correctamente."
        })

    except Rutina.DoesNotExist:
        return JsonResponse({"success": False, "error": "La rutina no existe."}, status=404)

    except Exception as e:
        print("🔥 ERROR eliminar_rutina:", traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@login_required
@require_POST
def toggle_rutina(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        rutina_id = data.get("rutina_id")

        if not rutina_id:
            return JsonResponse({"success": False, "error": "ID de rutina no proporcionado."}, status=400)

        rutina = Rutina.objects.get(id=rutina_id)

        if rutina.perfil != request.user:
            return JsonResponse({
                "success": False,
                "error": "No tienes permiso para modificar esta rutina."
            }, status=403)

        rutina.vigente = not rutina.vigente
        rutina.save()

        estado = "activada" if rutina.vigente else "desactivada"
        return JsonResponse({
            "success": True,
            "estado": estado,
            "nuevo_estado": rutina.vigente,
            "message": f"Rutina '{rutina.nombre}' {estado} correctamente."
        })

    except Rutina.DoesNotExist:
        return JsonResponse({"success": False, "error": "La rutina no existe."}, status=404)
    except Exception as e:
        print("🔥 ERROR toggle_rutina:", traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def obtener_mis_rutinas(request):
    try:
        rutinas = (
            Rutina.objects
            .filter(perfil=request.user)
            .select_related("nivel_dificultad")
            .order_by("-fecha_creacion")
        )

        data = []
        for r in rutinas:
            ejercicios_count = RutinaEjercicio.objects.filter(rutina=r).count()

            data.append({
                "id": r.id,
                "nombre": r.nombre,
                "descripcion": r.descripcion or "",
                "nivel": r.nivel_dificultad.nombre if r.nivel_dificultad else "Sin nivel",
                "vigente": r.vigente,
                "total_ejercicios": ejercicios_count,
                "fecha": r.fecha_creacion.strftime("%d/%m/%Y"),
            })

        return JsonResponse(data, safe=False)

    except Exception as e:
        print("🔥 ERROR obtener_mis_rutinas:", traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)