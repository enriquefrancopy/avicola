from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import PermisoUsuario


class Command(BaseCommand):
    help = 'Crea permisos por defecto para todos los usuarios activos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            help='Nombre de usuario específico para crear permisos',
        )
        parser.add_argument(
            '--forzar',
            action='store_true',
            help='Forzar la creación de permisos incluso si ya existen',
        )
        parser.add_argument(
            '--perfil',
            type=str,
            choices=['admin', 'vendedor', 'comprador', 'usuario_limite'],
            help='Perfil predefinido de permisos',
        )

    def handle(self, *args, **options):
        usuario_especifico = options['usuario']
        forzar = options['forzar']
        perfil = options['perfil']
        
        if usuario_especifico:
            try:
                usuario = User.objects.get(username=usuario_especifico, is_active=True)
                self.crear_permisos_usuario(usuario, forzar, perfil)
                self.stdout.write(
                    self.style.SUCCESS(f'Permisos creados para el usuario: {usuario.username}')
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Usuario no encontrado: {usuario_especifico}')
                )
        else:
            usuarios = User.objects.filter(is_active=True)
            count = 0
            
            for usuario in usuarios:
                if self.crear_permisos_usuario(usuario, forzar, perfil):
                    count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Permisos creados para {count} usuarios')
            )

    def crear_permisos_usuario(self, usuario, forzar=False, perfil=None):
        """Crea permisos por defecto para un usuario específico"""
        if not forzar and PermisoUsuario.objects.filter(usuario=usuario).exists():
            self.stdout.write(
                self.style.WARNING(f'El usuario {usuario.username} ya tiene permisos configurados')
            )
            return False
        
        # Eliminar permisos existentes si se fuerza
        if forzar:
            PermisoUsuario.objects.filter(usuario=usuario).delete()
        
        if perfil:
            self.crear_permisos_por_perfil(usuario, perfil)
        else:
            # Crear permisos por defecto
            PermisoUsuario.crear_permisos_por_defecto(usuario)
        
        self.stdout.write(
            self.style.SUCCESS(f'Permisos creados para: {usuario.username}')
        )
        return True

    def crear_permisos_por_perfil(self, usuario, perfil):
        """Crear permisos según un perfil específico"""
        if perfil == 'admin':
            # Superusuario con todos los permisos
            permisos_config = {
                'dashboard': {'puede_ver': True, 'puede_crear': True, 'puede_editar': True, 'puede_eliminar': True},
                'productos': {'puede_ver': True, 'puede_crear': True, 'puede_editar': True, 'puede_eliminar': True},
                'proveedores': {'puede_ver': True, 'puede_crear': True, 'puede_editar': True, 'puede_eliminar': True},
                'clientes': {'puede_ver': True, 'puede_crear': True, 'puede_editar': True, 'puede_eliminar': True},
                'facturas_venta': {'puede_ver': True, 'puede_crear': True, 'puede_editar': True, 'puede_eliminar': True},
                'facturas_compra': {'puede_ver': True, 'puede_crear': True, 'puede_editar': True, 'puede_eliminar': True},
                'pagos': {'puede_ver': True, 'puede_crear': True, 'puede_editar': True, 'puede_eliminar': True},
                'stock': {'puede_ver': True, 'puede_crear': True, 'puede_editar': True, 'puede_eliminar': True},
                'caja': {'puede_ver': True, 'puede_crear': True, 'puede_editar': True, 'puede_eliminar': True},
                'reportes': {'puede_ver': True, 'puede_crear': True, 'puede_editar': True, 'puede_eliminar': True},
                'configuracion': {'puede_ver': True, 'puede_crear': True, 'puede_editar': True, 'puede_eliminar': True},
                'notificaciones': {'puede_ver': True, 'puede_crear': True, 'puede_editar': True, 'puede_eliminar': True},
            }
        elif perfil == 'vendedor':
            # Vendedor: puede crear facturas de venta y gestionar clientes
            permisos_config = {
                'dashboard': {'puede_ver': True, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'productos': {'puede_ver': True, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'proveedores': {'puede_ver': False, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'clientes': {'puede_ver': True, 'puede_crear': True, 'puede_editar': True, 'puede_eliminar': False},
                'facturas_venta': {'puede_ver': True, 'puede_crear': True, 'puede_editar': True, 'puede_eliminar': False},
                'facturas_compra': {'puede_ver': False, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'pagos': {'puede_ver': True, 'puede_crear': True, 'puede_editar': False, 'puede_eliminar': False},
                'stock': {'puede_ver': True, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'caja': {'puede_ver': False, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'reportes': {'puede_ver': True, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'configuracion': {'puede_ver': False, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'notificaciones': {'puede_ver': True, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
            }
        elif perfil == 'comprador':
            # Comprador: puede crear facturas de compra y gestionar proveedores
            permisos_config = {
                'dashboard': {'puede_ver': True, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'productos': {'puede_ver': True, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'proveedores': {'puede_ver': True, 'puede_crear': True, 'puede_editar': True, 'puede_eliminar': False},
                'clientes': {'puede_ver': False, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'facturas_venta': {'puede_ver': False, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'facturas_compra': {'puede_ver': True, 'puede_crear': True, 'puede_editar': True, 'puede_eliminar': False},
                'pagos': {'puede_ver': True, 'puede_crear': True, 'puede_editar': False, 'puede_eliminar': False},
                'stock': {'puede_ver': True, 'puede_crear': True, 'puede_editar': True, 'puede_eliminar': False},
                'caja': {'puede_ver': False, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'reportes': {'puede_ver': True, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'configuracion': {'puede_ver': False, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'notificaciones': {'puede_ver': True, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
            }
        elif perfil == 'usuario_limite':
            # Usuario con permisos muy limitados
            permisos_config = {
                'dashboard': {'puede_ver': True, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'productos': {'puede_ver': True, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'proveedores': {'puede_ver': True, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'clientes': {'puede_ver': True, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'facturas_venta': {'puede_ver': True, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'facturas_compra': {'puede_ver': False, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'pagos': {'puede_ver': True, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'stock': {'puede_ver': True, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'caja': {'puede_ver': False, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'reportes': {'puede_ver': False, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'configuracion': {'puede_ver': False, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
                'notificaciones': {'puede_ver': True, 'puede_crear': False, 'puede_editar': False, 'puede_eliminar': False},
            }
        
        # Crear permisos según el perfil
        for modulo, permisos in permisos_config.items():
            PermisoUsuario.objects.create(usuario=usuario, modulo=modulo, **permisos)
