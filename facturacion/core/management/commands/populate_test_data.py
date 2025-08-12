from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random
from core.models import Producto, Proveedor, Cliente, Factura, DetalleFactura, MovimientoStock

class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de prueba para el dashboard'

    def handle(self, *args, **options):
        self.stdout.write('Limpiando base de datos...')
        
        # Limpiar datos existentes
        MovimientoStock.objects.all().delete()
        DetalleFactura.objects.all().delete()
        Factura.objects.all().delete()
        Cliente.objects.all().delete()
        Proveedor.objects.all().delete()
        Producto.objects.all().delete()
        
        # Crear usuario de prueba si no existe
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write('Usuario admin creado (password: admin123)')
        
        self.stdout.write('Creando productos...')
        
        # Crear productos
        productos = []
        productos_data = [
            {'codigo': 'HUE001', 'nombre': 'Huevos de Gallina', 'precio': 5000, 'costo': 3000, 'stock': 1000, 'stock_minimo': 100},
            {'codigo': 'POLL001', 'nombre': 'Pollo Entero', 'precio': 25000, 'costo': 18000, 'stock': 50, 'stock_minimo': 10},
            {'codigo': 'POLL002', 'nombre': 'Pechuga de Pollo', 'precio': 35000, 'costo': 25000, 'stock': 30, 'stock_minimo': 5},
            {'codigo': 'POLL003', 'nombre': 'Muslos de Pollo', 'precio': 20000, 'costo': 15000, 'stock': 40, 'stock_minimo': 8},
            {'codigo': 'HUE002', 'nombre': 'Huevos de Codorniz', 'precio': 8000, 'costo': 5000, 'stock': 500, 'stock_minimo': 50},
            {'codigo': 'POLL004', 'nombre': 'Alas de Pollo', 'precio': 15000, 'costo': 10000, 'stock': 25, 'stock_minimo': 5},
            {'codigo': 'POLL005', 'nombre': 'Pollo Deshuesado', 'precio': 40000, 'costo': 30000, 'stock': 20, 'stock_minimo': 3},
            {'codigo': 'HUE003', 'nombre': 'Huevos Orgánicos', 'precio': 12000, 'costo': 8000, 'stock': 200, 'stock_minimo': 20},
        ]
        
        for prod_data in productos_data:
            producto = Producto.objects.create(
                codigo=prod_data['codigo'],
                nombre=prod_data['nombre'],
                precio=prod_data['precio'],
                costo=prod_data['costo'],
                stock=prod_data['stock'],
                stock_minimo=prod_data['stock_minimo'],
                iva=10
            )
            productos.append(producto)
        
        self.stdout.write('Creando proveedores...')
        
        # Crear proveedores
        proveedores = []
        proveedores_data = [
            {'nombre': 'Granja San José', 'rif': 'J-12345678-9', 'direccion': 'Carretera Nacional Km 45', 'telefono': '0212-555-0101', 'email': 'info@granjasanjose.com'},
            {'nombre': 'Avícola El Paraíso', 'rif': 'J-87654321-0', 'direccion': 'Av. Principal #123', 'telefono': '0212-555-0202', 'email': 'ventas@avicola.com'},
            {'nombre': 'Distribuidora Avícola C.A.', 'rif': 'J-11223344-5', 'direccion': 'Zona Industrial', 'telefono': '0212-555-0303', 'email': 'contacto@distribuidora.com'},
        ]
        
        for prov_data in proveedores_data:
            proveedor = Proveedor.objects.create(
                nombre=prov_data['nombre'],
                rif=prov_data['rif'],
                direccion=prov_data['direccion'],
                telefono=prov_data['telefono'],
                email=prov_data['email'],
                saldo=0
            )
            proveedores.append(proveedor)
        
        self.stdout.write('Creando clientes...')
        
        # Crear clientes
        clientes = []
        clientes_data = [
            {'nombre': 'Restaurante El Buen Sabor', 'rif': 'J-98765432-1', 'direccion': 'Centro Comercial Plaza Mayor', 'telefono': '0212-555-0404', 'email': 'pedidos@buensabor.com'},
            {'nombre': 'Hotel Plaza Central', 'rif': 'J-55667788-9', 'direccion': 'Av. Bolívar #456', 'telefono': '0212-555-0505', 'email': 'compras@hotelplaza.com'},
            {'nombre': 'Cafetería Express', 'rif': 'J-33445566-7', 'direccion': 'Calle Comercial #789', 'telefono': '0212-555-0606', 'email': 'info@cafeteriaexpress.com'},
            {'nombre': 'Supermercado Mega', 'rif': 'J-22334455-6', 'direccion': 'Centro Comercial Mega Plaza', 'telefono': '0212-555-0707', 'email': 'proveedores@megasuper.com'},
            {'nombre': 'Restaurante La Casa', 'rif': 'J-44556677-8', 'direccion': 'Zona Gastronómica', 'telefono': '0212-555-0808', 'email': 'pedidos@lacasa.com'},
        ]
        
        for cli_data in clientes_data:
            cliente = Cliente.objects.create(
                nombre=cli_data['nombre'],
                rif=cli_data['rif'],
                direccion=cli_data['direccion'],
                telefono=cli_data['telefono'],
                email=cli_data['email'],
                saldo=0
            )
            clientes.append(cliente)
        
        self.stdout.write('Creando facturas de venta para varios meses...')
        
        # Crear facturas de venta para los últimos 12 meses
        fecha_actual = timezone.now().date()
        
        for mes in range(12):
            # Calcular fecha del mes
            fecha_mes = fecha_actual - timedelta(days=30*mes)
            inicio_mes = fecha_mes.replace(day=1)
            fin_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            # Número de facturas por mes (entre 15 y 30)
            num_facturas = random.randint(15, 30)
            
            for i in range(num_facturas):
                # Fecha aleatoria dentro del mes
                dias_en_mes = fin_mes.day
                dia_aleatorio = random.randint(1, dias_en_mes)
                fecha_factura = inicio_mes.replace(day=dia_aleatorio)
                
                # Cliente aleatorio
                cliente = random.choice(clientes)
                
                # Crear factura
                factura = Factura.objects.create(
                    tipo='venta',
                    numero=f'V-{fecha_factura.strftime("%Y%m")}-{i+1:03d}',
                    fecha=fecha_factura,
                    cliente=cliente,
                    subtotal=0,
                    iva=0,
                    total=0,
                    estado=random.choice(['pendiente', 'pagada']),
                    usuario=user
                )
                
                # Agregar detalles a la factura
                num_productos = random.randint(1, 4)
                subtotal_factura = 0
                iva_factura = 0
                
                productos_factura = random.sample(productos, min(num_productos, len(productos)))
                
                for producto in productos_factura:
                    cantidad = random.randint(1, 10)
                    precio_unitario = producto.precio
                    subtotal = cantidad * precio_unitario
                    iva = int(subtotal * 0.10)  # 10% IVA
                    total = subtotal + iva
                    
                    DetalleFactura.objects.create(
                        factura=factura,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                        iva=iva,
                        subtotal=subtotal,
                        total=total
                    )
                    
                    subtotal_factura += subtotal
                    iva_factura += iva
                
                # Actualizar totales de la factura
                factura.subtotal = subtotal_factura
                factura.iva = iva_factura
                factura.total = subtotal_factura + iva_factura
                factura.save()
                
                # Registrar movimiento de stock
                for detalle in factura.detalles.all():
                    MovimientoStock.objects.create(
                        producto=detalle.producto,
                        tipo='salida',
                        origen='factura_venta',
                        cantidad=detalle.cantidad,
                        stock_anterior=detalle.producto.stock,
                        stock_nuevo=detalle.producto.stock - detalle.cantidad,
                        referencia=f'Factura {factura.numero}',
                        usuario=user
                    )
                    
                    # Actualizar stock del producto
                    detalle.producto.stock -= detalle.cantidad
                    detalle.producto.save()
        
        self.stdout.write('Creando facturas de compra...')
        
        # Crear algunas facturas de compra
        for mes in range(6):
            fecha_mes = fecha_actual - timedelta(days=30*mes)
            inicio_mes = fecha_mes.replace(day=1)
            fin_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            num_compras = random.randint(3, 8)
            
            for i in range(num_compras):
                dia_aleatorio = random.randint(1, fin_mes.day)
                fecha_factura = inicio_mes.replace(day=dia_aleatorio)
                
                proveedor = random.choice(proveedores)
                
                factura = Factura.objects.create(
                    tipo='compra',
                    numero=f'C-{fecha_factura.strftime("%Y%m")}-{i+1:03d}',
                    fecha=fecha_factura,
                    proveedor=proveedor,
                    subtotal=0,
                    iva=0,
                    total=0,
                    estado=random.choice(['pendiente', 'pagada']),
                    usuario=user
                )
                
                # Agregar detalles
                num_productos = random.randint(1, 3)
                subtotal_factura = 0
                iva_factura = 0
                
                productos_compra = random.sample(productos, min(num_productos, len(productos)))
                
                for producto in productos_compra:
                    cantidad = random.randint(50, 200)
                    precio_unitario = producto.costo
                    subtotal = cantidad * precio_unitario
                    iva = int(subtotal * 0.10)
                    total = subtotal + iva
                    
                    DetalleFactura.objects.create(
                        factura=factura,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                        iva=iva,
                        subtotal=subtotal,
                        total=total
                    )
                    
                    subtotal_factura += subtotal
                    iva_factura += iva
                
                factura.subtotal = subtotal_factura
                factura.iva = iva_factura
                factura.total = subtotal_factura + iva_factura
                factura.save()
                
                # Registrar movimiento de stock
                for detalle in factura.detalles.all():
                    MovimientoStock.objects.create(
                        producto=detalle.producto,
                        tipo='entrada',
                        origen='factura_compra',
                        cantidad=detalle.cantidad,
                        stock_anterior=detalle.producto.stock,
                        stock_nuevo=detalle.producto.stock + detalle.cantidad,
                        referencia=f'Factura {factura.numero}',
                        usuario=user
                    )
                    
                    detalle.producto.stock += detalle.cantidad
                    detalle.producto.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Datos de prueba creados exitosamente:\n'
                f'   - {len(productos)} productos\n'
                f'   - {len(proveedores)} proveedores\n'
                f'   - {len(clientes)} clientes\n'
                f'   - {Factura.objects.filter(tipo="venta").count()} facturas de venta\n'
                f'   - {Factura.objects.filter(tipo="compra").count()} facturas de compra\n'
                f'   - {MovimientoStock.objects.count()} movimientos de stock'
            )
        )
        
        self.stdout.write(
            self.style.WARNING(
                '📊 Ahora puedes acceder al dashboard para ver los gráficos de facturación mensual y ventas diarias'
            )
        )
