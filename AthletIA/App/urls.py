from django.urls import path
from .views import *
from .red import *

urlpatterns = [
    # =========================================
    # Páginas principales
    # =========================================
    path('', base, name='base'),
    path('index/', index, name='index'),
    path('nosotros/', nosotros, name='nosotros'),
    path('contactanos/', contactanos, name='contactanos'),
    path("mensajes/quick/", mensajes_quick, name="mensajes_quick"),

    # Perfil
    path('perfil/', perfil, name='perfil'),
    path('perfil/estilo-vida/', editar_estilo_vida, name='editar_estilo_vida'),
    path('perfil/<int:pk>/', detalle_perfil, name='detalle_perfil'),

    # Comentarios / perfil
    path('perfil/<int:pk>/comentarios/', obtener_comentarios, name="obtener_comentarios"),
    path('perfil/<int:pk>/like/', toggle_like, name="toggle_like"),
    path('perfil/<int:pk>/favorite/', toggle_favorite, name="toggle_favorite"),
    path('toggle-follow/<int:perfil_id>/', toggle_follow, name='toggle_follow'),
    path("perfil/<int:perfil_id>/seguidores/", obtener_seguidores, name="obtener_seguidores"),
    path("perfil/<int:perfil_id>/siguiendo/", obtener_siguiendo, name="obtener_siguiendo"),


    # =========================================
    # API
    # =========================================
    path('g_Ejercicio/', g_Ejercicio, name='g_Ejercicio'),
    path('g_Dieta/', g_Dieta, name='g_Dieta'),
    path('api/guardar-alimento/', guardar_alimento_api, name='guardar_alimento'),

    # =========================================
    # RED SOCIAL — MURO
    # =========================================
    path('muro/', publicacion, name='muro'),

    # Comentarios
    path('muro/<int:publicacion_id>/comentario/', crear_comentario, name="crear_comentario"),
    path('muro/<int:publicacion_id>/comentarios/', obtener_comentarios, name="muro_obtener_comentarios"),
    path('comentario/<int:comentario_id>/reportar/', reportar_comentario, name='reportar_comentario'),

    # Likes / Favoritos
    path('muro/<int:publicacion_id>/like/', toggle_like, name="muro_toggle_like"),
    path('muro/<int:publicacion_id>/favorite/', toggle_favorite, name="muro_toggle_favorite"),

    # CRUD publicaciones
    path('muro/<int:publicacion_id>/editar/', editar_publicacion, name='editar_publicacion'),
    path('muro/<int:publicacion_id>/eliminar/', eliminar_publicacion, name='eliminar_publicacion'),

    # Compartir rutina (del calendario) — SIN MODIFICAR
    path("muro/compartir-rutina/", compartir_rutina_en_muro, name="compartir_rutina_en_muro"),
    path("panel-admin/calendario-rutinas/eliminar/<int:pk>/", eliminar_calendario_rutina, name="eliminar_calendario_rutina"),

    # NUEVO — RUTINAS PARA EL MURO (tarjeta premium)
    path("muro/rutinas/list/", obtener_rutinas_usuario, name="obtener_rutinas_usuario"),
    path("muro/rutina/<int:rutina_id>/preview/", preview_rutina, name="preview_rutina"),

    # =========================================
    # Mensajes privados
    # =========================================
    path('mensajes/', mensajes_inbox, name='mensajes_inbox'),
    path('mensajes/enviar/', enviar_mensaje, name='enviar_mensaje'),
    path('mensajes/<int:perfil_id>/', mensajes_conversacion, name='mensajes_conversacion'),
    path('mensajes/<int:perfil_id>/cargar/', cargar_mensajes, name='cargar_mensajes'),
    path('mensajes/<int:perfil_id>/nuevos/', obtener_nuevos_mensajes, name='obtener_nuevos_mensajes'),

    # Notificaciones
    path('notifications/list/', notifications_list, name='notifications_list'),
    path('notifications/count-unread/', notifications_unread_count, name='notifications_unread_count'),
    path('notifications/mark-read/<int:pk>/', notification_mark_read, name='notification_mark_read'),
    path('notifications/mark-all-read/', notifications_mark_all_read, name='notifications_mark_all_read'),
    path('notificaciones/', notifications_list_view, name='notifications_list'),

    # =========================================
    # Autenticación
    # =========================================
    path('inicio_Sesion/', inicio_Sesion, name='inicio_Sesion'),
    path('registro/', registro, name='registro'),
    path('cerrar_Sesion', cerrar_Sesion, name='cerrar_Sesion'),
    path('panel-admin/usuarios/toggle-staff/<int:pk>/', toggle_staff, name='toggle_staff'),


    # =========================================
    # Panel admin
    # =========================================

    # Usuarios
    path('panel-admin/', panel_admin, name='panel_admin'),
    path('panel-admin/usuarios/', listar_usuarios, name='listar_usuarios'),
    path('panel-admin/usuarios/crear/', crear_usuario, name='crear_usuario'),
    path('panel-admin/usuarios/editar/<int:pk>/', editar_usuario, name='editar_usuario'),
    path('panel-admin/usuarios/eliminar/<int:pk>/', eliminar_usuario, name='eliminar_usuario'),

    # Contacto
    path('admin/contactos/', listar_contactos, name='listar_contactos'),
    path('admin/contactos/eliminar/<int:pk>/', eliminar_contacto, name='eliminar_contacto'),

    # Publicaciones
    path('panel-admin/publicaciones/', listar_publicaciones, name='listar_publicaciones'),
    path('panel-admin/publicaciones/crear/', crear_publicacion, name='crear_publicacion'),
    path('panel-admin/publicaciones/editar/<int:pk>/', editar_publicacion, name='editar_publicacion'),
    path('panel-admin/publicaciones/eliminar/<int:pk>/', eliminar_publicacion, name='eliminar_publicacion'),
    
    # Analisi
    path('panel-admin/analisis-rutinas/', panel_analisis_rutinas, name='panel_analisis_rutinas'),

    # Comentarios
    path('panel-admin/comentarios/', listar_comentarios, name='listar_comentarios'),
    path('panel-admin/comentarios/eliminar/<int:pk>/', eliminar_comentario, name='eliminar_comentario'),

    # Progresos
    path('panel-admin/progresos/', listar_progresos, name='listar_progresos'),
    path('panel-admin/progresos/eliminar/<int:pk>/', eliminar_progreso, name='eliminar_progreso'),

    # Opiniones y tips
    path('panel-admin/opiniones/', listar_opiniones, name='listar_opiniones'),
    path('panel-admin/opiniones/eliminar/<int:pk>/', eliminar_opinion, name='eliminar_opinion'),

    path('panel-admin/tips/', listar_tips, name='listar_tips'),
    path('panel-admin/tips/crear/', crear_tip, name='crear_tip'),
    path('panel-admin/tips/editar/<int:pk>/', editar_tip, name='editar_tip'),
    path('panel-admin/tips/eliminar/<int:pk>/', eliminar_tip, name='eliminar_tip'),

    # Objetivos / Estilo de vida / Calendario / Salud
    path('panel-admin/objetivos/', listar_objetivos, name='listar_objetivos'),
    path('panel-admin/objetivos/eliminar/<int:pk>/', eliminar_objetivo, name='eliminar_objetivo'),

    path('panel-admin/estilos-vida/', listar_estilos_vida, name='listar_estilos_vida'),
    path('panel-admin/calendario-rutinas/', listar_calendario_rutinas, name='listar_calendario_rutinas'),
    path('panel-admin/salud-usuarios/', listar_salud_usuarios, name='listar_salud_usuarios'),

    # Tipos sangre
    path('panel-admin/tipos-sangre/', listar_tipos_sangre, name='listar_tipos_sangre'),
    path('panel-admin/tipos-sangre/crear/', crear_tipo_sangre, name='crear_tipo_sangre'),
    path('panel-admin/tipos-sangre/editar/<int:pk>/', editar_tipo_sangre, name='editar_tipo_sangre'),
    path('panel-admin/tipos-sangre/eliminar/<int:pk>/', eliminar_tipo_sangre, name='eliminar_tipo_sangre'),

    # Grupos
    path('panel-admin/grupos/', listar_grupos, name='listar_grupos'),
    path('panel-admin/grupos/eliminar/<int:pk>/', eliminar_grupo, name='eliminar_grupo'),

    # Historial / Nutrición / Sueño
    path('panel-admin/historial-medidas/', listar_historial_medidas, name='listar_historial_medidas'),
    path('panel-admin/nutricion-registros/', listar_nutricion_registros, name='listar_nutricion_registros'),
    path('panel-admin/sueno-usuarios/', listar_sueno_usuarios, name='listar_sueno_usuarios'),

    # REPORTES (Las que estaban fallando en el último error)
    path('panel-admin/reportes/', listar_reportes_comentarios, name='listar_reportes_comentarios'),
    path('panel-admin/reportes/eliminar/<int:pk>/', eliminar_reporte_comentario, name='eliminar_reporte_comentario'),

    # GESTIÓN COMUNIDAD Y SISTEMA (Añadir estas)
    path('panel-admin/comentarios/eliminar/<int:pk>/', eliminar_comentario_admin, name='eliminar_comentario_admin'), 
    path('panel-admin/publicaciones/eliminar/<int:pk>/', eliminar_publicacion_admin, name='eliminar_publicacion_admin'),

    # Grupos
    path("grupos/crear/", crear_grupo, name="crear_grupo"),
    path("grupos/<int:grupo_id>/unirse/", unirse_grupo, name="unirse_grupo"),
    path("grupos/<int:grupo_id>/editar/", editar_grupo, name="editar_grupo"),
    path("grupos/<int:grupo_id>/salir/", salir_grupo, name="salir_grupo"),
    path("grupos/<int:grupo_id>/", grupo_detalle, name="grupo_detalle"),
    path("grupos/<int:grupo_id>/expulsar/<int:perfil_id>/", expulsar_miembro, name="expulsar_miembro"),
    path("grupos/<int:grupo_id>/hacer-admin/<int:perfil_id>/", hacer_admin, name="hacer_admin"),
    path("grupos/<int:grupo_id>/quitar-admin/<int:perfil_id>/", quitar_admin, name="quitar_admin"),


    # Músculos
    path('panel-admin/musculos/', listar_musculos, name='listar_musculos'),
    path('panel-admin/musculos/crear/', crear_musculo, name='crear_musculo'),
    path('panel-admin/musculos/editar/<int:pk>/', editar_musculo, name='editar_musculo'),
    path('panel-admin/musculos/eliminar/<int:pk>/', eliminar_musculo, name='eliminar_musculo'),

    # Tipos de Ejercicio
    path('panel-admin/tipos/', listar_tipos, name='listar_tipos'),
    path('panel-admin/tipos/crear/', crear_tipo_ejercicio, name='crear_tipo_ejercicio'),
    path('panel-admin/tipos/editar/<int:pk>/', editar_tipo_ejercicio, name='editar_tipo_ejercicio'),
    path('panel-admin/tipos/eliminar/<int:pk>/', eliminar_tipo_ejercicio, name='eliminar_tipo_ejercicio'),

    # Niveles
    path('panel-admin/niveles/', listar_niveles, name='listar_niveles'),
    path('panel-admin/niveles/crear/', crear_nivel, name='crear_nivel'),
    path('panel-admin/niveles/editar/<int:pk>/', editar_nivel, name='editar_nivel'),
    path('panel-admin/niveles/eliminar/<int:pk>/', eliminar_nivel, name='eliminar_nivel'),

    # Ejercicios
    path('panel-admin/ejercicios/', listar_ejercicios, name='listar_ejercicios'),
    path('panel-admin/ejercicios/crear/', crear_ejercicio, name='crear_ejercicio'),
    path('panel-admin/ejercicios/editar/<int:pk>/', editar_ejercicio, name='editar_ejercicio'),
    path('panel-admin/ejercicios/eliminar/<int:pk>/', eliminar_ejercicio, name='eliminar_ejercicio'),

    # Rutinas
    path('panel-admin/rutinas/', listar_rutinas, name='listar_rutinas'),
    path('panel-admin/rutinas/crear/', crear_rutina, name='crear_rutina'),
    path('panel-admin/rutinas/eliminar/<int:pk>/', eliminar_rutina, name='eliminar_rutina')
    
]
