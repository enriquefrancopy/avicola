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

@register.filter
def div(value, arg):
    """Divide el valor por el argumento"""
    try:
        if arg == 0:
            return 0
        return value / arg
    except (ValueError, TypeError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiplica el valor por el argumento"""
    try:
        return value * arg
    except (ValueError, TypeError):
        return 0

@register.filter
def mul(value, arg):
    """Alias para multiply"""
    return multiply(value, arg)

@register.filter
def sum_list(value, key):
    """Suma los valores de una lista de diccionarios por clave"""
    try:
        return sum(item.get(key, 0) for item in value)
    except (ValueError, TypeError):
        return 0

@register.filter
def get_item(dictionary, key):
    """Obtiene un elemento de un diccionario por clave"""
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        return None

@register.filter
def tiene_permiso(usuario_permisos, modulo_accion):
    """Verifica si el usuario tiene un permiso específico"""
    try:
        modulo, accion = modulo_accion.split('.')
        if modulo in usuario_permisos:
            return usuario_permisos[modulo].get(accion, False)
        return False
    except (ValueError, AttributeError, TypeError):
        return False

@register.filter
def puede_ver(usuario_permisos, modulo):
    """Verifica si el usuario puede ver un módulo"""
    return tiene_permiso(usuario_permisos, f"{modulo}.ver")

@register.filter
def puede_crear(usuario_permisos, modulo):
    """Verifica si el usuario puede crear en un módulo"""
    return tiene_permiso(usuario_permisos, f"{modulo}.crear")

@register.filter
def puede_editar(usuario_permisos, modulo):
    """Verifica si el usuario puede editar en un módulo"""
    return tiene_permiso(usuario_permisos, f"{modulo}.editar")

@register.filter
def puede_eliminar(usuario_permisos, modulo):
    """Verifica si el usuario puede eliminar en un módulo"""
    return tiene_permiso(usuario_permisos, f"{modulo}.eliminar")
