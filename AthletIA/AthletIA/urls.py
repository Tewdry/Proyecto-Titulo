from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from App import views 
from IA.chat_virtual import chat_view, chat_api

urlpatterns = [
    path('', views.index, name='base'), 
    path('', include('App.urls')),                  # Tu web principal
    path('api/', include('api_ejercicio.urls')),    # Panel admin + API ejercicios
    path('admin/', admin.site.urls),
    path("ia/chat/", chat_view, name="chat_view"),
    path("ia/chat_api/", chat_api, name="chat_api"),
    path('ia/', include('IA.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
