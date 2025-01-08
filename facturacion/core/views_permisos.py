from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import PermisoUsuario
from .decorators import puede_ver_modulo, puede_editar_modulo


@login_required
@puede_ver_modulo('configuracion')
def permisos_usuarios_list(request):
    """Lista de usuarios con sus permisos"""
    usuarios = User.objects.filter(is_active=True).order_by('first_name', 'last_name', 'username')
    
    # Obtener permisos para cada usuario
    for usuario in usuarios:
        usuario.permisos_dict = {}
        for modulo, _ in PermisoUsuario.MODULO_CHOICES:
            permiso = PermisoUsuario.objects.filter(usuario=usuario, modulo=modulo).first()
            usuario.permisos_dict[modulo] = permiso
    
    context = {
        'usuarios': usuarios,
        'modulos': PermisoUsuario.MODULO_CHOICES,
        'titulo': 'Gestión de Permisos de Usuarios'
    }
    
    return render(request, 'permisos_usuarios_list.html', context)


@login_required
@puede_editar_modulo('configuracion')
def permisos_usuario_editar(request, user_id):
    """Editar permisos de un usuario específico"""
    usuario = get_object_or_404(User, id=user_id, is_active=True)
    
    if request.method == 'POST':
        # Procesar cambios de permisos
        for modulo, _ in PermisoUsuario.MODULO_CHOICES:
            puede_ver = request.POST.get(f'{modulo}_ver') == 'on'
            puede_crear = request.POST.get(f'{modulo}_crear') == 'on'
            puede_editar = request.POST.get(f'{modulo}_editar') == 'on'
            puede_eliminar = request.POST.get(f'{modulo}_eliminar') == 'on'
            
            # Si puede crear/editar/eliminar, debe poder ver
            if puede_crear or puede_editar or puede_eliminar:
                puede_ver = True
            
            permiso, created = PermisoUsuario.objects.get_or_create(
                usuario=usuario,
                modulo=modulo,
                defaults={
                    'puede_ver': puede_ver,
                    'puede_crear': puede_crear,
                    'puede_editar': puede_editar,
                    'puede_eliminar': puede_eliminar
                }
            )
            
            if not created:
                permiso.puede_ver = puede_ver
                permiso.puede_crear = puede_crear
                permiso.puede_editar = puede_editar
                permiso.puede_eliminar = puede_eliminar
                permiso.save()
        
        messages.success(request, f'Permisos de {usuario.get_full_name()} actualizados correctamente.')
        return redirect('permisos_usuarios_list')
    
    # Obtener permisos actuales
    permisos = {}
    for modulo, _ in PermisoUsuario.MODULO_CHOICES:
        permiso = PermisoUsuario.objects.filter(usuario=usuario, modulo=modulo).first()
        permisos[modulo] = permiso
    
    context = {
        'usuario': usuario,
        'permisos': permisos,
        'modulos': PermisoUsuario.MODULO_CHOICES,
        'titulo': f'Editar Permisos - {usuario.get_full_name()}'
    }
    
    return render(request, 'permisos_usuario_editar.html', context)


@login_required
@puede_editar_modulo('configuracion')
def permisos_usuario_reset(request, user_id):
    """Resetear permisos de un usuario a valores por defecto"""
    usuario = get_object_or_404(User, id=user_id, is_active=True)
    
    # Eliminar permisos existentes
    PermisoUsuario.objects.filter(usuario=usuario).delete()
    
    # Crear permisos por defecto
    PermisoUsuario.crear_permisos_por_defecto(usuario)
    
    messages.success(request, f'Permisos de {usuario.get_full_name()} reseteados a valores por defecto.')
    return redirect('permisos_usuarios_list')


@login_required
@puede_editar_modulo('configuracion')
def permisos_usuario_ajax(request, user_id):
    """API para actualizar permisos via AJAX"""
    if request.method == 'POST':
        usuario = get_object_or_404(User, id=user_id, is_active=True)
        modulo = request.POST.get('modulo')
        accion = request.POST.get('accion')
        valor = request.POST.get('valor') == 'true'
        
        if modulo and accion in ['ver', 'crear', 'editar', 'eliminar']:
            permiso, created = PermisoUsuario.objects.get_or_create(
                usuario=usuario,
                modulo=modulo,
                defaults={
                    'puede_ver': True,
                    'puede_crear': False,
                    'puede_editar': False,
                    'puede_eliminar': False
                }
            )
            
            if accion == 'ver':
                permiso.puede_ver = valor
            elif accion == 'crear':
                permiso.puede_crear = valor
            elif accion == 'editar':
                permiso.puede_editar = valor
            elif accion == 'eliminar':
                permiso.puede_eliminar = valor
            
            # Si se desactiva ver, desactivar todas las demás
            if not permiso.puede_ver:
                permiso.puede_crear = False
                permiso.puede_editar = False
                permiso.puede_eliminar = False
            
            permiso.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Permiso {accion} para {modulo} actualizado'
            })
    
    return JsonResponse({'success': False, 'message': 'Error en la solicitud'})


@login_required
@puede_editar_modulo('configuracion')
def crear_permisos_por_defecto(request):
    """Crear permisos por defecto para todos los usuarios activos"""
    usuarios = User.objects.filter(is_active=True)
    count = 0
    
    for usuario in usuarios:
        # Verificar si ya tiene permisos
        if not PermisoUsuario.objects.filter(usuario=usuario).exists():
            PermisoUsuario.crear_permisos_por_defecto(usuario)
            count += 1
    
    messages.success(request, f'Permisos por defecto creados para {count} usuarios.')
    return redirect('permisos_usuarios_list')
