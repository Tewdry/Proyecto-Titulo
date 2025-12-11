import os
import json
import joblib
import traceback
import numpy as np
import pandas as pd
import tensorflow as tf
import random
from datetime import date, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from App.models import Perfil, ProgresoUsuario, SaludUsuario, TipoObjetivo, ObjetivoUsuario, SuenoUsuario, EstiloVidaUsuario, NutricionRegistro, HistorialMedidas
from api_ejercicio.models import Ejercicio, Rutina, RutinaEjercicio, NivelDificultad
from .models import RecomendacionIA
from django.views.decorators.http import require_GET


# ==========================================================
# CARGA DEL MODELO IA (AthletIA)
# ==========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "modelos")

model = tf.keras.models.load_model(os.path.join(MODEL_DIR, "athletia_recomendador.keras"), compile=False)
preprocessor = joblib.load(os.path.join(MODEL_DIR, "preprocessor_athletia.pkl"))
label_encoder = joblib.load(os.path.join(MODEL_DIR, "label_encoder_athletia.pkl"))

# ==========================================================
# Vista principal: Generar Rutina
# ==========================================================
@login_required
def generar_rutina_view(request):
    objetivos = TipoObjetivo.objects.all().order_by("nombre")
    return render(request, "IA/generar_rutina.html", {"objetivos": objetivos})


# ==========================================================
# Vista del Recomendador IA (formulario clásico)
# ==========================================================
@login_required
def recomendador_view(request):
    perfil = request.user
    try:
        progreso = ProgresoUsuario.objects.filter(perfil=perfil).order_by("-fecha").first()
        objetivo = ObjetivoUsuario.objects.filter(perfil=perfil, activo=True).first()

        bmi = ""
        if progreso and progreso.altura_cm and progreso.peso_kg:
            altura_m = progreso.altura_cm / 100
            bmi = round(progreso.peso_kg / (altura_m ** 2), 1)

        datos = {
            "age": (date.today().year - perfil.fecha_nacimiento.year) if perfil.fecha_nacimiento else "",
            "bmi": bmi,
            "hr": perfil.salud_usuario.frecuencia_cardiaca_reposo if perfil.salud_usuario else 140,
            "duration": 40,
            "calories": 250,
            "goal": objetivo.tipo_objetivo.nombre if objetivo else "Mantener peso actual",
        }

    except Exception:
        datos = {"age": "", "bmi": "", "hr": "", "duration": "", "calories": "", "goal": "Mantener peso actual"}

    objetivos = TipoObjetivo.objects.all()
    return render(request, "IA/recomendador.html", {"datos": datos, "objetivos": objetivos})


# ==========================================================
# Vista Wizard (flujo paso a paso)
# ==========================================================
@login_required
def recomendador_wizard_view(request):
    objetivos = TipoObjetivo.objects.all().order_by("nombre")
    return render(request, "IA/recomendador_wizard.html", {"objetivos": objetivos})


# ==========================================================
# Chat IA
# ==========================================================
@login_required
def chat_view(request):
    return render(request, "IA/chat.html")


# ==========================================================
# Recomendador IA (AthletIA)
# ==========================================================
@csrf_exempt
@require_POST
@login_required
def recomendar_rutina(request):
    try:
        import traceback, random
        from datetime import date
        import numpy as np
        import pandas as pd

        body = json.loads(request.body.decode("utf-8"))
        perfil = request.user

        # ======================================================
        # 1. Recolectar datos del perfil y registros
        # ======================================================
        progreso = ProgresoUsuario.objects.filter(perfil=perfil).order_by("-fecha").first()
        objetivo = ObjetivoUsuario.objects.filter(perfil=perfil, activo=True).first()
        salud = getattr(perfil, "salud_usuario", None)
        sueno = SuenoUsuario.objects.filter(perfil=perfil).order_by("-fecha").first()
        nutricion = NutricionRegistro.objects.filter(perfil=perfil).order_by("-fecha").first()
        medidas = HistorialMedidas.objects.filter(perfil=perfil).order_by("-id").first()

        # Edad e IMC
        edad = float(body.get("edad") or (date.today().year - perfil.fecha_nacimiento.year if perfil.fecha_nacimiento else 28))
        altura_cm = float(progreso.altura_cm) if progreso and progreso.altura_cm else 170
        peso_kg = float(progreso.peso_kg) if progreso and progreso.peso_kg else 70
        imc = peso_kg / ((altura_cm / 100) ** 2)

        # ======================================================
        # 2. Datos de ritmo y entrenamiento
        # ======================================================
        ritmo = float(body.get("ritmo_cardiaco") or (salud.frecuencia_cardiaca_reposo if salud and salud.frecuencia_cardiaca_reposo else 75))
        
        duracion = float(body.get("duracion_min", 45))
        calorias = float(body.get("calorias_quemadas", 300))
        objetivo_nombre = str(body.get("objetivo") or (objetivo.tipo_objetivo.nombre if objetivo else "Mantener peso actual"))
        nivel = str(body.get("nivel_experiencia", "Intermedio"))

        # ======================================================
        # 3. Salud y hábitos
        # ======================================================
        fuma = body.get("fuma") or ("Sí" if salud and salud.fuma else "No")
        bebe = body.get("bebe") or ("Sí" if salud and salud.bebe else "No")
        lesiones_actuales = body.get("lesiones_actuales") or (salud.lesiones_actuales if salud and salud.lesiones_actuales else "No tengo lesiones")
        enfermedades_preexistentes = body.get("enfermedades_preexistentes") or (salud.enfermedades_preexistentes if salud and salud.enfermedades_preexistentes else "No poseo")

        # ======================================================
        # 4. Sueño y nutrición
        # ======================================================
        horas_sueno = body.get("horas_dormidas") or (sueno.horas_dormidas if sueno else "7 a 8 horas (óptimo)")
        calidad_sueno = body.get("calidad_sueno") or (sueno.calidad_sueno if sueno else "Buena")
        despertares = body.get("despertares_nocturnos") or (sueno.despertares_nocturnos if sueno else "1 vez")

        tipo_comida = body.get("tipo_comida_principal") or (nutricion.comida if nutricion else "Balanceada")
        calorias_diarias = body.get("calorias_diarias_aprox") or (f"{int(nutricion.calorias)} kcal" if nutricion and nutricion.calorias else "2000 - 2500 kcal")
        consumo_prot = body.get("consumo_proteinas") or (
            "Moderado" if not nutricion or not nutricion.proteinas else
            "Alto (según objetivos)" if nutricion.proteinas >= 100 else
            "Bajo"
        )

        meta_peso = body.get("meta_peso_corporal") or "Mantener peso actual"
        meta_grasa = body.get("meta_grasa_corporal") or "Entre 10% y 15%"

        # ======================================================
        # 5. Ajuste de dificultad inteligente
        # ======================================================
        peso_dificultad = 0
        if "avan" in nivel.lower(): peso_dificultad += 2
        elif "inter" in nivel.lower(): peso_dificultad += 1

        if duracion >= 100: peso_dificultad += 2
        elif duracion >= 60: peso_dificultad += 1
        elif duracion < 30: peso_dificultad -= 1

        if any(x in objetivo_nombre.lower() for x in ["fuerza", "muscul", "intenso", "rendimiento"]): peso_dificultad += 1
        elif any(x in objetivo_nombre.lower() for x in ["mantener", "salud", "bajar"]): peso_dificultad -= 1

        nivel_ajustado = "Avanzado" if peso_dificultad >= 3 else "Intermedio" if peso_dificultad >= 1 else "Principiante"

        # ======================================================
        # 6. Reglas de salud antes de predicción
        # ======================================================
        riesgo_enfermedad = any(x in str(enfermedades_preexistentes).lower() for x in ["diab", "asma", "hipert", "card", "colest"])
        riesgo_lesion = any(x in str(lesiones_actuales).lower() for x in ["rodilla", "hombro", "espalda", "desgarro", "esguince"])

        if riesgo_enfermedad or riesgo_lesion:
            duracion = min(duracion, 45)
            calorias = min(calorias, 250)
            nivel_ajustado = "Principiante"

        # ======================================================
        # 7. DataFrame completo para IA
        # ======================================================
        df = pd.DataFrame([{
            "edad": edad,
            "imc": imc,
            "ritmo_cardiaco": ritmo,
            "duracion_min": duracion,
            "calorias_quemadas": calorias,
            "altura_cm": altura_cm,
            "peso_kg": peso_kg,
            "grasa_corporal": float(medidas.grasa_corporal) if medidas and medidas.grasa_corporal else random.uniform(8, 25),
            "masa_muscular": float(medidas.masa_muscular) if medidas and medidas.masa_muscular else random.uniform(25, 40),
            "cintura_cm": float(medidas.cintura_cm) if medidas and medidas.cintura_cm else random.uniform(70, 100),
            "cadera_cm": float(medidas.cadera_cm) if medidas and medidas.cadera_cm else random.uniform(85, 110),
            "fuma": fuma,
            "bebe": bebe,
            "lesiones_actuales": lesiones_actuales,
            "enfermedades_preexistentes": enfermedades_preexistentes,
            "horas_dormidas": horas_sueno,
            "calidad_sueno": calidad_sueno,
            "despertares_nocturnos": despertares,
            "tipo_comida_principal": tipo_comida,
            "calorias_diarias_aprox": calorias_diarias,
            "consumo_proteinas": consumo_prot,
            "meta_peso_corporal": meta_peso,
            "meta_grasa_corporal": meta_grasa,
            "objetivo": objetivo_nombre,
            "nivel_experiencia": nivel_ajustado,
        }])

        # ======================================================
        # 8. Predicción IA AthletIA
        # ======================================================
        X = preprocessor.transform(df)
        preds = model.predict(X)
        top3_idx = np.argsort(preds[0])[-3:][::-1]
        rutinas = label_encoder.inverse_transform(top3_idx)
        top3 = [{"rutina": r, "probabilidad": round(float(preds[0][i]) * 100, 2)} for i, r in zip(top3_idx, rutinas)]
        rutina_principal = rutinas[0]
        precision_modelo = round(float(np.max(preds[0]) * 100), 2)

        # ======================================================
        # 9. Correcciones post-predicción
        # ======================================================
        if riesgo_enfermedad or riesgo_lesion:
            rutina_principal = "Rehabilitación"
            top3 = [
                {"rutina": "Rehabilitación", "probabilidad": 85.0},
                {"rutina": "Pilates", "probabilidad": 10.0},
                {"rutina": "Yoga", "probabilidad": 5.0},
            ]

        if duracion > 120 and "fuerza" in rutina_principal.lower():
            rutina_principal = "Full Body Workout"
            precision_modelo = round(precision_modelo * 0.9, 2)

        # ======================================================
        # 10. Crear o reutilizar rutina
        # ======================================================
        rutina_db, creada = Rutina.objects.get_or_create(
            nombre=f"Rutina IA - {rutina_principal}",
            defaults={
                "descripcion": f"Rutina personalizada generada con IA ({rutina_principal})",
                "perfil": perfil,
                "nivel_dificultad": NivelDificultad.objects.filter(nombre__icontains=nivel_ajustado).first()
                or NivelDificultad.objects.first(),
                "vigente": True,
            },
        )

        ejercicios_rel = list(Ejercicio.objects.filter(
            Q(nombre__icontains=rutina_principal) |
            Q(descripcion__icontains=rutina_principal) |
            Q(tipo_ejercicio__nombre__icontains=rutina_principal),
            nivel_dificultad__nombre__icontains=nivel_ajustado
        ).distinct())

        if len(ejercicios_rel) < 8:
            ejercicios_rel.extend(list(Ejercicio.objects.order_by("?")[:8 - len(ejercicios_rel)]))

        ejercicios = [{"nombre": e.nombre, "descripcion": e.descripcion or "Sin descripción disponible."} for e in ejercicios_rel[:8]]

        # ======================================================
        # 11. Guardar registro IA
        # ======================================================
        RecomendacionIA.objects.create(
            perfil=perfil,
            rutina_recomendada=rutina_principal,
            top3_recomendaciones=top3,
            ejercicios=ejercicios,
            parametros_entrada=df.to_dict(orient="records")[0],
            precision_modelo=precision_modelo,
            modelo_version="AthletIA v13 (Full Health + Habits)",
            estado="pendiente",
        )

        # ======================================================
        # 12. Respuesta JSON
        # ======================================================
        return JsonResponse({
            "success": True,
            "recommendation": rutina_principal,
            "precision_modelo": precision_modelo,
            "top3": top3,
            "ejercicios": ejercicios,
            "nivel_experiencia": nivel_ajustado,
            "nueva_rutina": creada,
        })

    except Exception as e:
        print("🔥 ERROR IA:", traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=400)


# ==========================================================
# Guardar rutina recomendada manualmente
# ==========================================================
@csrf_exempt
@require_POST
@login_required
def guardar_rutina(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        tipo_rutina = data.get("tipo")
        ejercicios = data.get("ejercicios", [])[:8]

        perfil = Perfil.objects.get(id=request.user.id)
        nivel_default = NivelDificultad.objects.first() or NivelDificultad.objects.create(
            nombre="Intermedio",
            descripcion="Nivel asignado automáticamente."
        )

        rutina = Rutina.objects.create(
            nombre=f"Rutina IA - {tipo_rutina}",
            descripcion=f"Rutina generada automáticamente ({tipo_rutina})",
            perfil=perfil,
            nivel_dificultad=nivel_default,
            vigente=True,
        )

        for e in ejercicios:
            ejercicio = Ejercicio.objects.filter(nombre__iexact=e.get("nombre")).first()
            if ejercicio:
                RutinaEjercicio.objects.create(rutina=rutina, ejercicio=ejercicio)

        return JsonResponse({
            "success": True,
            "message": "Rutina guardada correctamente.",
            "rutina": tipo_rutina,
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@require_POST
@login_required
def guardar_rutina_manual(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        nombre = data.get("nombre", "Rutina Personalizada")
        notas = data.get("notas", "")
        ejercicios = data.get("ejercicios", [])

        perfil = Perfil.objects.get(id=request.user.id)
        nivel_default = NivelDificultad.objects.filter(nombre__icontains="Intermedio").first() \
            or NivelDificultad.objects.create(nombre="Intermedio", descripcion="Nivel asignado automáticamente.")

        rutina = Rutina.objects.create(
            nombre=nombre,
            descripcion=notas or "Rutina creada manualmente por el usuario.",
            perfil=perfil,
            nivel_dificultad=nivel_default,
            vigente=True,
        )

        for e in ejercicios[:20]:  # Limita por seguridad
            ejercicio = Ejercicio.objects.filter(nombre__iexact=e.get("nombre")).first()
            if ejercicio:
                RutinaEjercicio.objects.create(rutina=rutina, ejercicio=ejercicio)

        return JsonResponse({
            "success": True,
            "message": "Rutina guardada exitosamente.",
            "rutina_id": rutina.id,
        })

    except Exception as e:
        import traceback
        print("🔥 ERROR guardar_rutina_manual:", traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=400)


# ==========================================================
# Verificación y guardado de datos faltantes
# ==========================================================
@login_required
def verificar_datos_usuario(request):
    perfil = request.user
    faltantes = []

    if not perfil.fecha_nacimiento:
        faltantes.append("edad")

    progreso = ProgresoUsuario.objects.filter(perfil=perfil).order_by("-fecha").first()
    if not progreso or not progreso.altura_cm:
        faltantes.append("altura")
    if not progreso or not progreso.peso_kg:
        faltantes.append("peso")

    salud = getattr(perfil, "salud_usuario", None)
    if not salud or not salud.frecuencia_cardiaca_reposo:
        faltantes.append("ritmo_cardiaco")

    objetivo = ObjetivoUsuario.objects.filter(perfil=perfil, activo=True).first()
    if not objetivo or not objetivo.tipo_objetivo:
        faltantes.append("objetivo")

    return JsonResponse({"faltantes": faltantes})


@csrf_exempt
@login_required
def guardar_datos_faltantes(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        perfil = request.user

        with transaction.atomic():
            if "edad" in data and data["edad"]:
                edad = int(data["edad"])
                perfil.fecha_nacimiento = date.today() - timedelta(days=edad * 365)
                perfil.save()

            if "altura" in data or "peso" in data:
                progreso = ProgresoUsuario.objects.filter(perfil=perfil).order_by("-fecha").first()
                if not progreso:
                    progreso = ProgresoUsuario.objects.create(perfil=perfil)
                if data.get("altura"):
                    progreso.altura_cm = float(data["altura"])
                if data.get("peso"):
                    progreso.peso_kg = float(data["peso"])
                progreso.save()

            if "ritmo_cardiaco" in data:
                salud = perfil.salud_usuario or SaludUsuario.objects.create()
                salud.frecuencia_cardiaca_reposo = data["ritmo_cardiaco"]
                salud.save()
                perfil.salud_usuario = salud
                perfil.save()

            if "objetivo" in data:
                tipo = TipoObjetivo.objects.filter(id=data["objetivo"]).first()
                if tipo:
                    obj = ObjetivoUsuario.objects.filter(perfil=perfil, activo=True).first()
                    if not obj:
                        ObjetivoUsuario.objects.create(
                            perfil=perfil,
                            tipo_objetivo=tipo,
                            fecha_inicio=date.today(),
                            estado="En progreso",
                            activo=True
                        )
                    else:
                        obj.tipo_objetivo = tipo
                        obj.save()

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@login_required
def seleccionar_ejercicios_view(request):
    return render(request, "IA/seleccionar_ejercicios.html")


@csrf_exempt
@require_POST
@login_required
def guardar_rutina_manual(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        ejercicios = data.get("ejercicios", [])
        nombre_rutina = data.get("nombre", "Rutina Personalizada")
        notas = data.get("notas", "")

        perfil = Perfil.objects.get(id=request.user.id)
        nivel_default = (
            NivelDificultad.objects.filter(nombre__icontains="Intermedio").first()
            or NivelDificultad.objects.first()
        )

        rutina = Rutina.objects.create(
            nombre=nombre_rutina,
            descripcion=f"Rutina creada manualmente desde el mapa corporal por {perfil.username}",
            perfil=perfil,
            nivel_dificultad=nivel_default,
            vigente=True,
        )

        # Si vienen strings dentro de la lista → convertir a int
        ejercicios_ids = []
        for e in ejercicios:
            try:
                ejercicios_ids.append(int(e))  # e = ID
            except:
                pass

        # Asociar ejercicios por ID
        for ej_id in ejercicios_ids:
            ej = Ejercicio.objects.filter(id=ej_id).first()
            if ej:
                RutinaEjercicio.objects.create(rutina=rutina, ejercicio=ej)

        return JsonResponse({
            "success": True,
            "message": "Rutina manual creada correctamente.",
            "rutina_id": rutina.id,
            "rutina_nombre": rutina.nombre,
        })

    except Exception as e:
        import traceback
        print("🔥 ERROR guardar_rutina_manual:", traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@login_required
def listar_ejercicios(request):
    try:
        # Obtenemos solo los campos necesarios (diccionarios directos)
        ejercicios = list(Ejercicio.objects.values(
            'id', 
            'nombre', 
            'descripcion', 
            'musculo__nombre',      
            'tipo_ejercicio__nombre', 
            'nivel_dificultad__nombre' 
        ))

        data = [
            {
                "id": e['id'],
                "nombre": e['nombre'],
                "descripcion": e['descripcion'] or "",
                "musculo": e['musculo__nombre'] or "General",
                "tipo": e['tipo_ejercicio__nombre'] or "General",
                "nivel": e['nivel_dificultad__nombre'] or "Básico"
            }
            for e in ejercicios
        ]
            
        return JsonResponse({"success": True, "ejercicios": data}, safe=False)

    except Exception as e:
        print("🔥 ERROR listar_ejercicios:", str(e))
        return JsonResponse({"success": False, "error": str(e)}, status=500)