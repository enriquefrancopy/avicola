from django.db.models import F
from datetime import datetime, timedelta
from .models import Producto, Factura, Notificacion, ConfiguracionSistema

def alertas_globales(request):
    """Context processor para agregar alertas globales a todas las plantillas"""
    if not request.user.is_authenticated:
        return {}
    
    # Productos con stock bajo (stock <= stock_minimo)
    productos_stock_bajo = Producto.objects.filter(
        activo=True,
        stock__lte=F('stock_minimo'),
        stock__gt=0
    ).order_by('stock')
    
    # Productos agotados (stock = 0)
    productos_agotados = Producto.objects.filter(
        activo=True,
        stock=0
    ).order_by('nombre')
    
    # Facturas pendientes de pago (más de 30 días)
    fecha_limite = datetime.now() - timedelta(days=30)
    facturas_vencidas = Factura.objects.filter(
        estado='pendiente',
        fecha__lt=fecha_limite
    ).order_by('fecha')
    
    total_alertas = productos_stock_bajo.count() + productos_agotados.count() + facturas_vencidas.count()
    
    return {
        'alertas': {
            'stock_bajo': productos_stock_bajo,
            'agotados': productos_agotados,
            'facturas_vencidas': facturas_vencidas,
        },
        'total_alertas': total_alertas,
    }

def configuracion_global(request):
    """Context processor para agregar configuración global a todas las plantillas"""
    if not request.user.is_authenticated:
        return {}
    
    # Obtener tema visual
    tema_visual = ConfiguracionSistema.get_valor('tema_visual', 'azul')
    
    return {
        'configuracion_sistema': {
            'tema_visual': tema_visual,
        }
    } 