from datetime import timedelta
import json

from django.db.models import Count, Q, OuterRef, Exists
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.utils.formats import date_format
from django.views.decorators.http import require_POST
from django.utils.html import escape

from api_ejercicio.models import Rutina, RutinaEjercicio, RutinaGuardada
from .models import (
    Publicacion, Comentario, Like, FavoritoPublicacion,
    SeguimientoUsuario, Perfil, Tip, ComentarioReporte,
    GrupoEntrenamiento, GrupoMiembro
)

# ======================================================
# MURO DE PUBLICACIONES + GRUPOS + KPI
# ======================================================

def publicacion(request):
    if request.method == 'POST':
        contenido = request.POST.get('contenido', '').strip()
        media = request.FILES.get('media_url')

        if not contenido and not media:
            return redirect('muro')

        if not request.user.is_authenticated:
            return redirect('inicio_Sesion')

        Publicacion.objects.create(
            contenido=escape(contenido),
            perfil=request.user,
            media_url=media
        )
        return redirect('muro')
    
    qs = Publicacion.objects.select_related('perfil').order_by('-fecha_creacion')

    # 2. Annotate: Contamos likes, comentarios y favoritos en la BD
    qs = qs.annotate(
        num_likes=Count('like', distinct=True),
        num_comentarios=Count('comentario', distinct=True),
        num_favoritos=Count('favoritopublicacion', distinct=True)
    )

    if request.user.is_authenticated:
        # Subqueries para verificar existencia
        liked_subquery = Like.objects.filter(publicacion=OuterRef('pk'), perfil=request.user)
        fav_subquery = FavoritoPublicacion.objects.filter(publicacion=OuterRef('pk'), perfil=request.user)
        
        # Para seguir: Verificamos si el usuario logueado sigue al autor del post
        siguiendo_subquery = SeguimientoUsuario.objects.filter(
            seguidor=request.user, 
            seguido=OuterRef('perfil')
        )

        qs = qs.annotate(
            es_liked=Exists(liked_subquery),
            es_favorited=Exists(fav_subquery),
            es_siguiendo=Exists(siguiendo_subquery)
        )
    
    # Ejecutamos la consulta (Limitamos a 50 posts para no saturar si hay miles)
    publicaciones = qs[:50] 

    # Tips (Optimizado)
    tips = Tip.objects.filter(vigente=True).order_by('-fecha_creacion')[:5]


    ahora = timezone.now()
    hace_7_dias = ahora - timedelta(days=7)

    # KPIs simples (Count es rápido en DB)
    total_grupos = GrupoEntrenamiento.objects.filter(vigente=True).count()
    posts_semana = Publicacion.objects.filter(fecha_creacion__gte=hace_7_dias).count()
    comentarios_semana = Comentario.objects.filter(fecha_creacion__gte=hace_7_dias).count()

    mis_grupos_qs = GrupoMiembro.objects.none()
    mis_grupos_ids = set()
    total_mis_grupos = 0

    if request.user.is_authenticated:
        # select_related para no hacer queries en el bucle del template
        mis_grupos_qs = GrupoMiembro.objects.filter(
            perfil=request.user,
            activo=True
        ).select_related("grupo_entrenamiento")
        
        total_mis_grupos = mis_grupos_qs.count()
        mis_grupos_ids = set(mis_grupos_qs.values_list("grupo_entrenamiento_id", flat=True))

    # Grupos: Annotate para contar miembros sin loops
    grupos_base = GrupoEntrenamiento.objects.filter(vigente=True).annotate(
        miembros_count=Count("grupomiembro", filter=Q(grupomiembro__activo=True), distinct=True),
        activos_count=Count("grupomiembro", filter=Q(grupomiembro__activo=True), distinct=True)
    )

    grupos_todos = grupos_base.order_by('-fecha_creacion')[:10] 
    grupos_tendencia = grupos_base.order_by('-activos_count')[:5]

    if request.user.is_authenticated:
        grupos_recomendados = grupos_base.exclude(
            id__in=mis_grupos_ids
        ).order_by('-miembros_count')[:5]
    else:
        grupos_recomendados = grupos_base.order_by('-miembros_count')[:5]

    # Reportes
    reportes_recientes = ComentarioReporte.objects.select_related(
        "comentario", "perfil", "comentario__perfil"
    ).order_by('-fecha')[:5]

    context = {
        "publicaciones": publicaciones,
        "tips": tips,
        "kpi_total_grupos": total_grupos,
        "kpi_mis_grupos": total_mis_grupos,
        "kpi_posts_semana": posts_semana,
        "kpi_comentarios_semana": comentarios_semana,
        "kpi_ultima_actualizacion": ahora,
        "mis_grupos": mis_grupos_qs,
        "mis_grupos_ids": mis_grupos_ids,
        "grupos_todos": grupos_todos,
        "grupos_tendencia": grupos_tendencia,
        "grupos_recomendados": grupos_recomendados,
        "reportes_recientes": reportes_recientes,
    }

    return render(request, 'Red/muro.html', context)


# ======================================================
# COMENTARIOS
# ======================================================

@login_required
def crear_comentario(request, publicacion_id):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=400)

    contenido = request.POST.get('contenido', '').strip()
    if not contenido:
        return JsonResponse({"error": "Comentario vacío"}, status=400)

    publicacion = get_object_or_404(Publicacion, id=publicacion_id)

    comentario = Comentario.objects.create(
        publicacion=publicacion,
        perfil=request.user,
        comentario=escape(contenido)
    )

    fecha_local = timezone.localtime(comentario.fecha_creacion)
    foto_url = (
        request.user.foto.url
        if getattr(request.user, "foto", None)
        else "/media/avatar.png"
    )

    return JsonResponse({
        "id": comentario.id,
        "usuario": comentario.perfil.username,
        "comentario": comentario.comentario,
        "fecha": date_format(fecha_local, "d/m/Y H:i"),
        "foto": foto_url
    })


@login_required
def obtener_comentarios(request, publicacion_id):
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    comentarios = Comentario.objects.filter(
        publicacion=publicacion
    ).order_by("-fecha_creacion")

    data = []
    for c in comentarios:
        fecha_local = timezone.localtime(c.fecha_creacion)
        foto_url = (
            c.perfil.foto.url
            if getattr(c.perfil, "foto", None)
            else "/media/avatar.png"
        )

        data.append({
            "id": c.id,
            "usuario": c.perfil.username,
            "comentario": c.comentario,
            "fecha": date_format(fecha_local, "d/m/Y H:i"),
            "foto": foto_url
        })
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def reportar_comentario(request, comentario_id):
    try:
        data = json.loads(request.body.decode("utf-8"))
        motivo = data.get("motivo", "").strip()

        if not motivo:
            return JsonResponse({"success": False, "error": "Debes ingresar un motivo."})

        comentario = Comentario.objects.get(id=comentario_id)

        ComentarioReporte.objects.create(
            comentario=comentario,
            perfil=request.user,
            motivo=motivo
        )

        return JsonResponse({"success": True, "message": "Reporte enviado correctamente."})

    except Comentario.DoesNotExist:
        return JsonResponse({"success": False, "error": "Comentario no encontrado."})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# ======================================================
# LIKES Y FAVORITOS
# ======================================================

@login_required
@require_POST
def toggle_like(request, publicacion_id):
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)

    like, created = Like.objects.get_or_create(
        publicacion=publicacion,
        perfil=request.user
    )

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    total_likes = Like.objects.filter(publicacion=publicacion).count()

    return JsonResponse({
        "liked": liked,
        "total_likes": total_likes
    })


@login_required
@require_POST
def toggle_favorite(request, publicacion_id):
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)

    fav, created = FavoritoPublicacion.objects.get_or_create(
        publicacion=publicacion,
        perfil=request.user
    )

    if not created:
        fav.delete()
        favorited = False
        status = 'removed'
    else:
        favorited = True
        status = 'added'

    total_favs = FavoritoPublicacion.objects.filter(
        publicacion=publicacion
    ).count()

    return JsonResponse({
        'favorited': favorited,
        'total_favorites': total_favs,
        'status': status
    })


# ======================================================
# EDITAR Y ELIMINAR PUBLICACIÓN
# ======================================================

@login_required
@require_POST
def editar_publicacion(request, publicacion_id):
    publicacion = get_object_or_404(
        Publicacion,
        id=publicacion_id,
        perfil=request.user
    )
    nuevo_contenido = request.POST.get('contenido', '').strip()

    if not nuevo_contenido:
        return JsonResponse({"success": False, "error": "Contenido vacío"})

    publicacion.contenido = escape(nuevo_contenido)
    publicacion.save(update_fields=["contenido", "ultima_actualizacion"])

    return JsonResponse({"success": True})


@login_required
@require_POST
def eliminar_publicacion(request, publicacion_id):
    publicacion = get_object_or_404(
        Publicacion,
        id=publicacion_id,
        perfil=request.user
    )
    publicacion.delete()
    return JsonResponse({"success": True})


# ======================================================
# SEGUIR / DEJAR DE SEGUIR
# ======================================================

@login_required
@require_POST
def toggle_follow(request, perfil_id):
    perfil = get_object_or_404(Perfil, pk=perfil_id)

    seguimiento, creado = SeguimientoUsuario.objects.get_or_create(
        seguidor=request.user,
        seguido=perfil
    )

    if not creado:
        seguimiento.delete()
        return JsonResponse({'siguiendo': False})

    return JsonResponse({'siguiendo': True})


# ======================================================
# COMPARTIR RUTINAS EN EL MURO
# ======================================================

@csrf_exempt
@login_required
def compartir_rutina_en_muro(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        rutina_id = data.get("rutina_id")
        es_ia = data.get("es_ia", False)

        rutina = Rutina.objects.select_related(
            "nivel_dificultad"
        ).get(id=rutina_id)

        ejercicios = (
            RutinaEjercicio.objects
            .filter(rutina=rutina)
            .select_related("ejercicio")
            .values("ejercicio__nombre", "ejercicio__descripcion")
        )

        ejercicios_json_str = json.dumps(list(ejercicios))

        nombre_usuario = request.user.first_name or request.user.username

        if es_ia:
            encabezado = "🤖 <b>AthletIA</b> ha generado una nueva rutina automática:"
        else:
            encabezado = (
                f"🧍‍♂️ <b>{escape(nombre_usuario)}</b> "
                f"ha compartido su rutina personalizada:"
            )

        contenido_html = f"""
        <div class="rutina-compartida-card"
            data-rutina="{escape(ejercicios_json_str)}"
            data-rutinaid="{rutina.id}">
          <p class="rutina-encabezado">{encabezado}</p>

          <div class="rutina-info bg-light p-3 rounded mt-2 mb-2">
              <h6 class="fw-bold mb-1">🏋️ {escape(rutina.nombre)}</h6>
              <p class="mb-1"><b>💪 Nivel:</b> {escape(rutina.nivel_dificultad.nombre)}</p>
              <p class="mb-0 text-muted">
                 <b>📝 Descripción:</b>
                 {escape(rutina.descripcion or 'Sin descripción disponible.')}
              </p>
          </div>

          <div class="text-center">
              <button class="btn btn-outline-primary btn-ver-rutina mt-2"
                      onclick="verRutinaDesdePost(this)">
                  📋 Ver Rutina
              </button>
          </div>
        </div>
        """

        # 🔥 CORRECCIÓN: siempre asignar request.user
        Publicacion.objects.create(
            perfil=request.user,
            contenido=contenido_html
        )

        return JsonResponse({"success": True})

    except Rutina.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "La rutina no existe."},
            status=404
        )

    except Exception as e:
        import traceback
        print("🔥 ERROR compartir_rutina_en_muro:", traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)}, status=500)



# ======================================================
# LISTAR RUTINAS PROPIAS Y GUARDADAS
# ======================================================

@login_required
def obtener_rutinas_usuario(request):
    perfil = request.user

    propias = list(Rutina.objects.filter(
        perfil=perfil,
        vigente=True
    ).values("id", "nombre", "descripcion", "fecha_creacion"))

    guardadas = list(
        RutinaGuardada.objects.filter(perfil=perfil)
        .select_related("rutina")
        .values(
            "rutina__id",
            "rutina__nombre",
            "rutina__descripcion",
            "rutina__fecha_creacion"
        )
    )

    return JsonResponse({
        "success": True,
        "propias": propias,
        "guardadas": guardadas,
    })


# ======================================================
# PREVIEW DE RUTINA PARA LA TARJETA DEL MURO
# ======================================================

@login_required
def preview_rutina(request, rutina_id):
    try:
        rutina = Rutina.objects.get(id=rutina_id)
    except Rutina.DoesNotExist:
        return JsonResponse({"success": False, "error": "Rutina no encontrada"})

    ejercicios = list(
        RutinaEjercicio.objects.filter(rutina=rutina)
        .select_related("ejercicio")
        .values(
            "ejercicio__nombre",
            "ejercicio__descripcion",
            "repeticiones",
            "orden",
            "ejercicio__musculo__nombre",
        )
    )

    total_ejercicios = len(ejercicios)
    musculos = list({e["ejercicio__musculo__nombre"] for e in ejercicios})

    return JsonResponse({
        "success": True,
        "rutina": {
            "id": rutina.id,
            "nombre": rutina.nombre,
            "descripcion": rutina.descripcion,
            "ejercicios": ejercicios,
            "total_ejercicios": total_ejercicios,
            "musculos": musculos,
        }
    })


# =====================================================
# GRUPOS (crear / unirse / salir / detalle)
# ====================================================

@login_required
@require_POST
def crear_grupo(request):
    data = json.loads(request.body.decode("utf-8"))

    nombre = data.get("nombre", "").strip()
    descripcion = data.get("descripcion", "").strip()

    if not nombre:
        return JsonResponse({"success": False, "error": "El grupo debe tener un nombre."})

    nuevo = GrupoEntrenamiento.objects.create(
        nombre=nombre,
        descripcion=descripcion,
        perfil_creador=request.user
    )

    # Creador entra automáticamente como ADMIN
    GrupoMiembro.objects.create(
        grupo_entrenamiento=nuevo,
        perfil=request.user,
        rol="admin",
        activo=True
    )

    return JsonResponse({"success": True, "grupo_id": nuevo.id})


@login_required
@require_POST
def unirse_grupo(request, grupo_id):
    grupo = get_object_or_404(GrupoEntrenamiento, pk=grupo_id, vigente=True)

    miembro = GrupoMiembro.objects.filter(
        grupo_entrenamiento=grupo,
        perfil=request.user
    ).first()

    # Ya es miembro activo
    if miembro and miembro.activo:
        return JsonResponse({
            "success": False,
            "already_member": True,
            "message": "Ya eres miembro de este grupo."
        })

    # Existía pero estaba inactivo → reactivar
    if miembro and not miembro.activo:
        miembro.activo = True
        miembro.save()
        return JsonResponse({
            "success": True,
            "reactivated": True,
            "message": "Has vuelto al grupo."
        })

    # No existía → crear registro nuevo
    GrupoMiembro.objects.create(
        grupo_entrenamiento=grupo,
        perfil=request.user,
        rol="miembro",
        activo=True
    )

    return JsonResponse({
        "success": True,
        "joined": True,
        "message": "Te has unido al grupo."
    })


@login_required
@require_POST
def salir_grupo(request, grupo_id):
    miembro = GrupoMiembro.objects.filter(
        grupo_entrenamiento_id=grupo_id,
        perfil=request.user
    ).first()

    # No está en el grupo
    if not miembro:
        return JsonResponse({
            "success": False,
            "not_member": True,
            "message": "No perteneces a este grupo."
        })

    # Ya estaba inactivo
    if not miembro.activo:
        return JsonResponse({
            "success": False,
            "already_out": True,
            "message": "Ya has salido del grupo previamente."
        })

    # Salida correcta
    miembro.activo = False
    miembro.save()

    return JsonResponse({
        "success": True,
        "left_group": True,
        "message": "Has salido del grupo."
    })

@login_required
@require_POST
def editar_grupo(request, grupo_id):
    grupo = get_object_or_404(GrupoEntrenamiento, pk=grupo_id, vigente=True)

    # validar si es admin
    es_admin = GrupoMiembro.objects.filter(
        grupo_entrenamiento=grupo,
        perfil=request.user,
        rol="admin",
        activo=True
    ).exists()

    if not es_admin:
        return JsonResponse({"success": False, "error": "No tienes permisos."}, status=403)

    data = json.loads(request.body.decode("utf-8"))
    nombre = data.get("nombre", "").strip()
    descripcion = data.get("descripcion", "").strip()

    if not nombre:
        return JsonResponse({"success": False, "error": "El nombre no puede estar vacío."}, status=400)

    grupo.nombre = nombre
    grupo.descripcion = descripcion
    grupo.save()

    return JsonResponse({"success": True, "message": "Grupo actualizado correctamente."})


@login_required
def grupo_detalle(request, grupo_id):
    grupo = get_object_or_404(GrupoEntrenamiento, pk=grupo_id, vigente=True)

    # Miembros activos
    miembros = GrupoMiembro.objects.filter(
        grupo_entrenamiento=grupo,
        activo=True
    ).select_related("perfil").order_by("fecha_ingreso")

    # Es miembro del grupo
    es_miembro = miembros.filter(perfil=request.user).exists()

    # Es admin del grupo
    es_admin = miembros.filter(
        perfil=request.user,
        rol="admin",
        activo=True
    ).exists()

    # Miembro más nuevo / antiguo
    miembro_mas_reciente = miembros.order_by("-fecha_ingreso").first()
    miembro_mas_antiguo = miembros.order_by("fecha_ingreso").first()

    # Contadores reales
    total_miembros = miembros.count()
    total_admins = miembros.filter(rol="admin").count()

    return render(request, "Red/grupo_detalle.html", {
        "grupo": grupo,
        "miembros": miembros,
        "es_miembro": es_miembro,
        "es_admin": es_admin,
        "total_miembros": total_miembros,
        "total_admins": total_admins,
        "miembro_mas_reciente": miembro_mas_reciente,
        "miembro_mas_antiguo": miembro_mas_antiguo,
    })

@login_required
@require_POST
def expulsar_miembro(request, grupo_id, perfil_id):

    miembro = get_object_or_404(
        GrupoMiembro,
        grupo_entrenamiento_id=grupo_id,
        perfil_id=perfil_id
    )

    # validar admin
    admin = GrupoMiembro.objects.filter(
        grupo_entrenamiento_id=grupo_id,
        perfil=request.user,
        rol="admin",
        activo=True
    ).exists()

    if not admin:
        return JsonResponse({"success": False, "error": "No tienes permisos."})

    miembro.activo = False
    miembro.save()

    return JsonResponse({"success": True})

@login_required
@require_POST
def hacer_admin(request, grupo_id, perfil_id):
    # ¿el que ejecuta es admin?
    es_admin = GrupoMiembro.objects.filter(
        grupo_entrenamiento_id=grupo_id,
        perfil=request.user,
        rol="admin",
        activo=True
    ).exists()

    if not es_admin:
        return JsonResponse({"success": False, "error": "No tienes permisos."}, status=403)

    miembro = get_object_or_404(
        GrupoMiembro,
        grupo_entrenamiento_id=grupo_id,
        perfil_id=perfil_id,
        activo=True
    )

    miembro.rol = "admin"
    miembro.save()

    return JsonResponse({"success": True, "message": "Ahora este miembro es administrador."})


@login_required
@require_POST
def quitar_admin(request, grupo_id, perfil_id):
    # ¿el que ejecuta es admin?
    es_admin = GrupoMiembro.objects.filter(
        grupo_entrenamiento_id=grupo_id,
        perfil=request.user,
        rol="admin",
        activo=True
    ).exists()

    if not es_admin:
        return JsonResponse({"success": False, "error": "No tienes permisos."}, status=403)

    miembro = get_object_or_404(
        GrupoMiembro,
        grupo_entrenamiento_id=grupo_id,
        perfil_id=perfil_id,
        activo=True
    )

    # evitar dejar el grupo sin admins
    admins_activos = GrupoMiembro.objects.filter(
        grupo_entrenamiento_id=grupo_id,
        rol="admin",
        activo=True
    ).count()

    if admins_activos <= 1 and miembro.rol == "admin":
        return JsonResponse({
            "success": False,
            "error": "No puedes quitar el último administrador del grupo."
        }, status=400)

    miembro.rol = "miembro"
    miembro.save()

    return JsonResponse({"success": True, "message": "Este miembro ya no es administrador."})

