from django.urls import path, include
from api_ejercicio import views

urlpatterns = [

    # API / IA
    path('IA/', include('IA.urls')),

    # ------------------------------
    # Páginas públicas
    # ------------------------------
    path('mapa-corporal/', views.mapa_corporal, name='mapa_corporal'),
    path('musculo/<str:nombre>/', views.musculo_detalle, name='musculo_detalle'),

]
