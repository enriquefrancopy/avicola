from django.core.management.base import BaseCommand
from django.db.models import F
from datetime import datetime, timedelta
from core.models import Producto, Factura, Notificacion

class Command(BaseCommand):
    help = 'Verificar y crear alertas automáticas de stock y facturas vencidas'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando verificación de alertas...')
        
        # Verificar productos con stock bajo
        productos_stock_bajo = Producto.objects.filter(
            activo=True,
            stock__lte=F('stock_minimo'),
            stock__gt=0
        )
        
        for producto in productos_stock_bajo:
            mensaje = f"Stock bajo: {producto.nombre} (Código: {producto.codigo}) - Stock actual: {producto.stock}, Mínimo: {producto.stock_minimo}"
            Notificacion.objects.create(
                mensaje=mensaje,
                tipo='warning'
            )
            self.stdout.write(f'  - Alerta creada: {mensaje}')
        
        # Verificar productos agotados
        productos_agotados = Producto.objects.filter(
            activo=True,
            stock=0
        )
        
        for producto in productos_agotados:
            mensaje = f"Producto agotado: {producto.nombre} (Código: {producto.codigo}) - Stock: 0"
            Notificacion.objects.create(
                mensaje=mensaje,
                tipo='error'
            )
            self.stdout.write(f'  - Alerta creada: {mensaje}')
        
        # Verificar facturas vencidas
        fecha_limite = datetime.now() - timedelta(days=30)
        facturas_vencidas = Factura.objects.filter(
            estado='pendiente',
            fecha__lt=fecha_limite
        )
        
        for factura in facturas_vencidas:
            dias_vencida = (datetime.now() - factura.fecha.replace(tzinfo=None)).days
            mensaje = f"Factura vencida: #{factura.id} - {factura.get_tipo_display()} - Vencida hace {dias_vencida} días - Total: Gs. {factura.total:,}"
            Notificacion.objects.create(
                mensaje=mensaje,
                tipo='error'
            )
            self.stdout.write(f'  - Alerta creada: {mensaje}')
        
        total_alertas = productos_stock_bajo.count() + productos_agotados.count() + facturas_vencidas.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Verificación completada. {total_alertas} alertas creadas.'
            )
        ) 