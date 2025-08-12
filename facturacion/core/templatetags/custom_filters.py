from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter
def sub(value, arg):
    """Resta el argumento del valor"""
    try:
        return value - arg
    except (ValueError, TypeError):
        return value

@register.filter
def intcomma_dot(value):
    """Formatea números con punto como separador de miles"""
    try:
        # Formatear el número manualmente con puntos
        if value is None:
            return '0'
        
        # Convertir a string y formatear
        num_str = str(int(value))
        result = ''
        for i, digit in enumerate(reversed(num_str)):
            if i > 0 and i % 3 == 0:
                result = '.' + result
            result = digit + result
        return result
    except (ValueError, TypeError):
        return str(value) if value is not None else '0'
