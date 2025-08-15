from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import *
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Crea datos de prueba para el sistema'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Creando datos de prueba...')

        # Crear usuario de prueba si no existe
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write('✅ Usuario admin creado')

        # Crear configuraciones del sistema
        configuraciones = [
            {'clave': 'nombre_empresa', 'valor': 'Avícola CVA', 'descripcion': 'Nombre de la empresa', 'categoria': 'general'},
            {'clave': 'ruc', 'valor': '12345678-9', 'descripcion': 'RUC de la empresa', 'categoria': 'general'},
            {'clave': 'direccion', 'valor': 'Asunción, Paraguay', 'descripcion': 'Dirección de la empresa', 'categoria': 'general'},
            {'clave': 'telefono', 'valor': '+595 21 123456', 'descripcion': 'Teléfono de la empresa', 'categoria': 'general'},
            {'clave': 'email', 'valor': 'info@avicolacva.com', 'descripcion': 'Email de la empresa', 'categoria': 'general'},
            {'clave': 'moneda', 'valor': 'Guaraní', 'descripcion': 'Moneda del sistema', 'categoria': 'general'},
            {'clave': 'simbolo_moneda', 'valor': 'Gs.', 'descripcion': 'Símbolo de la moneda', 'categoria': 'general'},
            {'clave': 'stock_minimo', 'valor': '10', 'descripcion': 'Stock mínimo para alertas', 'categoria': 'stock'},
            {'clave': 'alertas_email', 'valor': 'True', 'descripcion': 'Activar alertas por email', 'categoria': 'alertas'},
        ]
        
        for config_data in configuraciones:
            config, created = ConfiguracionSistema.objects.get_or_create(
                clave=config_data['clave'],
                defaults=config_data
            )
            if created:
                self.stdout.write(f'✅ Configuración {config.clave} creada')

        # Crear proveedores
        proveedores_data = [
            {'nombre': 'Proveedor A', 'ruc': '12345678-1', 'direccion': 'Dirección A', 'telefono': '021-111111', 'email': 'proveedorA@email.com'},
            {'nombre': 'Proveedor B', 'ruc': '12345678-2', 'direccion': 'Dirección B', 'telefono': '021-222222', 'email': 'proveedorB@email.com'},
            {'nombre': 'Proveedor C', 'ruc': '12345678-3', 'direccion': 'Dirección C', 'telefono': '021-333333', 'email': 'proveedorC@email.com'},
        ]

        for data in proveedores_data:
            proveedor, created = Proveedor.objects.get_or_create(
                ruc=data['ruc'],
                defaults=data
            )
            if created:
                self.stdout.write(f'✅ Proveedor {proveedor.nombre} creado')

        # Crear clientes
        clientes_data = [
            {'nombre': 'Cliente A', 'ruc': '98765432-1', 'direccion': 'Dirección A', 'telefono': '021-444444', 'email': 'clienteA@email.com'},
            {'nombre': 'Cliente B', 'ruc': '98765432-2', 'direccion': 'Dirección B', 'telefono': '021-555555', 'email': 'clienteB@email.com'},
            {'nombre': 'Cliente C', 'ruc': '98765432-3', 'direccion': 'Dirección C', 'telefono': '021-666666', 'email': 'clienteC@email.com'},
        ]

        for data in clientes_data:
            cliente, created = Cliente.objects.get_or_create(
                ruc=data['ruc'],
                defaults=data
            )
            if created:
                self.stdout.write(f'✅ Cliente {cliente.nombre} creado')

        # Crear productos
        productos_data = [
            {'nombre': 'Huevos AA', 'codigo': 'HUE001', 'precio': 5000, 'stock': 100, 'stock_minimo': 20},
            {'nombre': 'Huevos A', 'codigo': 'HUE002', 'precio': 4500, 'stock': 150, 'stock_minimo': 25},
            {'nombre': 'Huevos B', 'codigo': 'HUE003', 'precio': 4000, 'stock': 200, 'stock_minimo': 30},
            {'nombre': 'Pollo Entero', 'codigo': 'POL001', 'precio': 25000, 'stock': 50, 'stock_minimo': 10},
            {'nombre': 'Pollo Deshuesado', 'codigo': 'POL002', 'precio': 35000, 'stock': 30, 'stock_minimo': 5},
        ]

        for data in productos_data:
            producto, created = Producto.objects.get_or_create(
                codigo=data['codigo'],
                defaults=data
            )
            if created:
                self.stdout.write(f'✅ Producto {producto.nombre} creado')

        # Crear caja abierta para hoy
        caja_hoy, created = Caja.objects.get_or_create(
            fecha=timezone.now().date(),
            defaults={
                'saldo_inicial': 100000,
                'saldo_final': 0,
                'cerrada': False,
                'usuario_apertura': user
            }
        )
        
        if created:
            # Crear denominaciones de apertura
            denominaciones_apertura = [
                {'valor': 100000, 'cantidad': 1, 'es_cierre': False},
                {'valor': 50000, 'cantidad': 2, 'es_cierre': False},
                {'valor': 20000, 'cantidad': 5, 'es_cierre': False},
                {'valor': 10000, 'cantidad': 10, 'es_cierre': False},
                {'valor': 5000, 'cantidad': 20, 'es_cierre': False},
                {'valor': 2000, 'cantidad': 50, 'es_cierre': False},
                {'valor': 1000, 'cantidad': 100, 'es_cierre': False},
                {'valor': 500, 'cantidad': 200, 'es_cierre': False},
                {'valor': 100, 'cantidad': 500, 'es_cierre': False},
            ]
            
            for denom_data in denominaciones_apertura:
                Denominacion.objects.create(
                    caja=caja_hoy,
                    valor=denom_data['valor'],
                    cantidad=denom_data['cantidad'],
                    es_cierre=denom_data['es_cierre']
                )
            
            self.stdout.write('✅ Caja abierta creada con denominaciones')

        # Crear algunas facturas de ejemplo
        # Factura de compra
        proveedor = Proveedor.objects.first()
        if proveedor:
            factura_compra = Factura.objects.create(
                numero='FC-001',
                fecha=timezone.now().date(),
                tipo='compra',
                proveedor=proveedor,
                subtotal=100000,
                iva=10000,
                total=110000,
                estado='pendiente',
                usuario=user
            )
            
            # Detalle de factura de compra
            producto = Producto.objects.first()
            if producto:
                DetalleFactura.objects.create(
                    factura=factura_compra,
                    producto=producto,
                    cantidad=20,
                    precio_unitario=5000,
                    subtotal=100000,
                    iva=10000,
                    total=110000
                )
            
            # Actualizar saldo del proveedor
            proveedor.saldo += factura_compra.total
            proveedor.save()
            
            self.stdout.write('✅ Factura de compra creada')

        # Factura de venta
        cliente = Cliente.objects.first()
        if cliente:
            factura_venta = Factura.objects.create(
                numero='FV-001',
                fecha=timezone.now().date(),
                tipo='venta',
                cliente=cliente,
                subtotal=75000,
                iva=7500,
                total=82500,
                estado='pendiente',
                usuario=user
            )
            
            # Detalle de factura de venta
            producto = Producto.objects.first()
            if producto:
                DetalleFactura.objects.create(
                    factura=factura_venta,
                    producto=producto,
                    cantidad=15,
                    precio_unitario=5000,
                    subtotal=75000,
                    iva=7500,
                    total=82500
                )
            
            # Actualizar saldo del cliente
            cliente.saldo += factura_venta.total
            cliente.save()
            
            self.stdout.write('✅ Factura de venta creada')

        self.stdout.write(
            self.style.SUCCESS(
                '🎉 ¡Datos de prueba creados exitosamente!\n'
                'Usuario: admin / Contraseña: admin123\n'
                'Caja abierta con saldo inicial de Gs. 100,000\n'
                'Puedes empezar a probar el sistema.'
            )
        )
