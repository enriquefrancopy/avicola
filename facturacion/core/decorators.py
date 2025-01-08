from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps
from .models import PermisoUsuario


def requiere_permiso(modulo, accion='ver'):
    """
    Decorador para verificar si un usuario tiene permiso para acceder a un módulo
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Superusuarios tienen todos los permisos
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verificar permiso específico
            if not PermisoUsuario.tiene_permiso(request.user, modulo, accion):
                messages.error(request, f'No tienes permisos para acceder al módulo {modulo}.')
                return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def puede_ver_modulo(modulo):
    """Decorador para verificar si puede ver un módulo"""
    return requiere_permiso(modulo, 'ver')


def puede_crear_modulo(modulo):
    """Decorador para verificar si puede crear en un módulo"""
    return requiere_permiso(modulo, 'crear')


def puede_editar_modulo(modulo):
    """Decorador para verificar si puede editar en un módulo"""
    return requiere_permiso(modulo, 'editar')


def puede_eliminar_modulo(modulo):
    """Decorador para verificar si puede eliminar en un módulo"""
    return requiere_permiso(modulo, 'eliminar')
