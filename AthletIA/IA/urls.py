from django.urls import path

from . import views_detalle_rutina
from . import views
from . import views_calendario
from . import views_dashboard

app_name = 'ia'

urlpatterns = [
    # Chat IA
    path("chat/", views.chat_view, name="chat"),

    # IA AthletIA
    path("recomendar/", views.recomendar_rutina, name="recomendar_rutina"),
    path("guardar_rutina/", views.guardar_rutina, name="guardar_rutina"),
    path("recomendador/wizard/", views.recomendador_wizard_view, name="recomendador_wizard"),

    # Interfaz principal
    path("recomendador/", views.recomendador_view, name="recomendador_view"),
    path("generar/", views.generar_rutina_view, name="generar_rutina"),

    # Datos del usuario
    path("verificar_datos_usuario/", views.verificar_datos_usuario, name="verificar_datos_usuario"),
    path("guardar_datos_faltantes/", views.guardar_datos_faltantes, name="guardar_datos_faltantes"),

    # Calendario
    path("calendario/", views_calendario.calendario_view, name="calendario_view"),
    path("calendario/registrar/", views_calendario.registrar_rutina_calendario, name="registrar_rutina_calendario"),
    path("calendario/eventos/", views_calendario.obtener_calendario, name="obtener_calendario"),
    path("calendario/actualizar/", views_calendario.actualizar_rutina_calendario, name="actualizar_rutina_calendario"),

    # KPI mensual
    path("calendario/kpi-mensual/", views_calendario.obtener_kpi_mensual, name="obtener_kpi_mensual"),

    # Rutina Manual (Mapa Corporal)
    path("manual/guardar/", views.guardar_rutina_manual, name="guardar_rutina_manual"),
    path("manual/seleccionar/", views.seleccionar_ejercicios_view, name="seleccionar_ejercicios"),
    path("calendario/manual/registrar/", views_calendario.registrar_rutina_calendario_manual, name="registrar_rutina_calendario_manual"),
    path("calendario/manual/eventos/", views_calendario.obtener_calendario_manual, name="obtener_calendario_manual"),

    # Guardar / info / listado rutinas guardadas
    path("calendario/guardar-rutina/", views_calendario.guardar_rutina_en_perfil, name="guardar_rutina_en_perfil"),
    path("calendario/info-guardado/", views_calendario.obtener_info_guardado, name="obtener_info_guardado"),
    path("obtener_rutinas_guardadas/", views_calendario.obtener_rutinas_guardadas, name="obtener_rutinas_guardadas"),
    path("asignar_rutina_guardada/", views_calendario.asignar_rutina_guardada, name="asignar_rutina_guardada"),
    path("rutina/unsave/", views_calendario.eliminar_rutina_guardada, name="eliminar_rutina_guardada"),

    # Tendencias
    path("obtener_tendencias/", views_calendario.obtener_tendencias, name="obtener_tendencias"),

    # Dashboard
    path("dashboard/", views_dashboard.dashboard_view, name="dashboard_view"),

    # Detalle Rutina
    path("rutina/ver/<int:rutina_id>/", views_detalle_rutina.ver_rutina_detalle, name="ver_rutina"),
    path("rutina/editar/", views_detalle_rutina.editar_rutina, name="editar_rutina"),
    path("rutina/duplicar/", views_detalle_rutina.duplicar_rutina, name="duplicar_rutina"),
    path("rutina/eliminar/", views_detalle_rutina.eliminar_rutina, name="eliminar_rutina"),
    path("rutina/toggle/", views_detalle_rutina.toggle_rutina, name="toggle_rutina"),
    path("mis-rutinas/", views_detalle_rutina.obtener_mis_rutinas, name="mis_rutinas"),

    # Dashboard
    path("dashboard/kpi/", views_dashboard.obtener_kpi_dashboard, name="kpi_dashboard"),
    path("dashboard/datos-graficos/", views_dashboard.datos_graficos_dashboard, name="datos_graficos_dashboard"),

    # Ejercicios Rutinas
    path("ejercicios/listar/", views.listar_ejercicios, name="listar_ejercicios"),
    path('api/calendario/mover/', views_calendario.mover_rutina_calendario, name='mover_rutina_calendario'),

    # --- GOOGLE CALENDAR ---
    path("google/auth/", views_calendario.iniciar_google_auth, name="iniciar_google_auth"),
    path("google/callback/", views_calendario.google_callback, name="google_callback"),
    path("google/sync/", views_calendario.sincronizar_rutina_google, name="sincronizar_rutina_google"),
    
]
