from django.core.management.base import BaseCommand
from core.models import Notificacion
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Crear notificaciones de prueba para el sistema'

    def handle(self, *args, **options):
        # Obtener el primer usuario o crear uno si no existe
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@avicolacva.com',
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Usuario creado: {user.username}'))
        
        # Crear notificaciones de prueba
        notificaciones_prueba = [
            {
                'mensaje': 'Producto "Huevos AA" tiene stock bajo (5 unidades)',
                'tipo': 'warning',
                'usuario': None,  # Notificación global
                'fecha': datetime.now() - timedelta(hours=2)
            },
            {
                'mensaje': 'Producto "Pollo Entero" se ha agotado',
                'tipo': 'error',
                'usuario': None,  # Notificación global
                'fecha': datetime.now() - timedelta(hours=1)
            },
            {
                'mensaje': 'Factura #123 está vencida por 5 días',
                'tipo': 'error',
                'usuario': None,  # Notificación global
                'fecha': datetime.now() - timedelta(minutes=30)
            },
            {
                'mensaje': 'Nuevo proveedor "Distribuidora ABC" registrado',
                'tipo': 'info',
                'usuario': user,  # Notificación específica del usuario
                'fecha': datetime.now() - timedelta(minutes=15)
            },
            {
                'mensaje': 'Sistema actualizado correctamente',
                'tipo': 'info',
                'usuario': None,  # Notificación global
                'fecha': datetime.now() - timedelta(minutes=5)
            }
        ]
        
        # Crear las notificaciones
        for notif_data in notificaciones_prueba:
            notificacion, created = Notificacion.objects.get_or_create(
                mensaje=notif_data['mensaje'],
                tipo=notif_data['tipo'],
                usuario=notif_data['usuario'],
                defaults={
                    'fecha': notif_data['fecha'],
                    'leida': False
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Notificación creada: {notif_data["mensaje"]}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Notificación ya existe: {notif_data["mensaje"]}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Se crearon {len(notificaciones_prueba)} notificaciones de prueba')
        ) 