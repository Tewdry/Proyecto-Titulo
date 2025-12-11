import ollama
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

MODELO_IA = "phi3"  

def chat_view(request):
    return render(request, "IA/chat.html")

@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        mensaje_usuario = data.get("mensaje", "").strip()

        if not mensaje_usuario:
            return JsonResponse({"respuesta": "Por favor escribe algo 😅."})

        if mensaje_usuario == "__reset__":
            request.session["chat_historial"] = []
            return JsonResponse({"respuesta": "💬 Historial reiniciado. ¿En qué puedo ayudarte ahora?"})

        historial = request.session.get("chat_historial", [])

        if len(historial) > 30:
            historial = historial[-30:]
        historial.append({"role": "user", "content": mensaje_usuario})

        try:
            respuesta = ollama.chat(
                model="phi3",
                messages=[
                    {"role": "system", "content": (
                        "Eres un entrenador general que sabe todo tipo de ejercicio. Responde en español con un máximo de una frase. Si el usuario saluda, responde solo con un saludo corto. No des explicaciones largas, ejemplos ni detalles adicionales bajo ninguna circunstancia, Solo responde en base a lo que te pregunten"
                    )}
                ] + historial
            )

            texto = respuesta["message"]["content"].strip()

            historial.append({"role": "assistant", "content": texto})
            request.session["chat_historial"] = historial

            return JsonResponse({"respuesta": texto})

        except Exception as e:
            return JsonResponse({
                "respuesta": f"⚠️ Error al conectar con la IA. Verifica que Ollama esté corriendo.\n\nDetalles: {str(e)}"
            })

    return JsonResponse({"error": "Método no permitido."}, status=405)
