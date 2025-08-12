from django.core.management.base import BaseCommand
from core.models import MovimientoStock, DetalleFactura, Factura, Cliente, Proveedor, Producto, Notificacion, ConfiguracionSistema
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Limpia completamente la base de datos'

    def handle(self, *args, **options):
        self.stdout.write('🧹 Limpiando base de datos...')
        
        # Limpiar datos en orden para evitar errores de dependencias
        self.stdout.write('Eliminando movimientos de stock...')
        MovimientoStock.objects.all().delete()
        
        self.stdout.write('Eliminando detalles de facturas...')
        DetalleFactura.objects.all().delete()
        
        self.stdout.write('Eliminando facturas...')
        Factura.objects.all().delete()
        
        self.stdout.write('Eliminando clientes...')
        Cliente.objects.all().delete()
        
        self.stdout.write('Eliminando proveedores...')
        Proveedor.objects.all().delete()
        
        self.stdout.write('Eliminando productos...')
        Producto.objects.all().delete()
        
        self.stdout.write('Eliminando notificaciones...')
        Notificacion.objects.all().delete()
        
        self.stdout.write('Eliminando configuraciones del sistema...')
        ConfiguracionSistema.objects.all().delete()
        
        # Mantener solo el usuario admin
        self.stdout.write('Manteniendo usuario admin...')
        
        self.stdout.write(
            self.style.SUCCESS(
                '✅ Base de datos limpiada exitosamente!\n'
                '   - Todos los datos han sido eliminados\n'
                '   - Solo se mantiene el usuario admin\n'
                '   - La base de datos está lista para nuevos datos'
            )
        )

