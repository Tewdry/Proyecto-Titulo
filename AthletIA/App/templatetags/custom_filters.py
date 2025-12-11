from django import template
import re
from django.utils.html import strip_tags

register = template.Library()

@register.filter
def attr_lookup(obj, attr_name):
    try:
        # 1. Maneja lookups anidados (ej: perfil__username)
        if '__' in attr_name:
            attributes = attr_name.split('__')
            value = obj
            for attr in attributes:
                value = getattr(value, attr)
            return value
        
        # 2. Maneja atributos simples
        val = getattr(obj, attr_name)
        
        # 3. Si es un método, ejecutarlo
        if callable(val):
            return val()
        
        return val
    except AttributeError:
        # Devuelve vacío si el atributo no existe o el lookup falla
        return ""
    
@register.filter
def clean_text(value, length=80):
    """Limpia HTML y acorta el texto para mostrarlo bien en tablas."""
    if not value:
        return ""

    # Eliminar etiquetas HTML
    clean = strip_tags(value)

    # Normalizar espacios
    clean = re.sub(r"\s+", " ", clean).strip()

    # Truncar
    if len(clean) > length:
        return clean[:length] + "…"

    return clean