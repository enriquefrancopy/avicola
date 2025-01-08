from django.db.models import F, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Producto, Factura, Notificacion, ConfiguracionSistema, PermisoUsuario


def alertas_globales(request):
    """Context processor para alertas globales"""
    if not request.user.is_authenticated:
        return {}
    
    alertas = []
    
    # Verificar stock bajo
    alertas_stock_bajo = ConfiguracionSistema.get_valor('alertas_stock_bajo', 'True')
    if alertas_stock_bajo.lower() == 'true':
        productos_stock_bajo = Producto.objects.filter(
            activo=True,
            stock__gt=0,
            stock__lte=F('stock_minimo')
        ).count()
        
        if productos_stock_bajo > 0:
            alertas.append({
                'tipo': 'warning',
                'mensaje': f'{productos_stock_bajo} producto(s) con stock bajo',
                'icono': 'bi-exclamation-triangle'
            })
    
    # Verificar productos agotados
    productos_agotados = Producto.objects.filter(activo=True, stock=0).count()
    if productos_agotados > 0:
        alertas.append({
            'tipo': 'danger',
            'mensaje': f'{productos_agotados} producto(s) agotado(s)',
            'icono': 'bi-x-circle'
        })
    
    # Verificar facturas vencidas
    alertas_facturas_vencidas = ConfiguracionSistema.get_valor('alertas_facturas_vencidas', 'True')
    if alertas_facturas_vencidas.lower() == 'true':
        dias_vencimiento = int(ConfiguracionSistema.get_valor('dias_factura_vencida', '30'))
        fecha_limite = timezone.now().date() - timedelta(days=dias_vencimiento)
        
        facturas_vencidas = Factura.objects.filter(
            estado='pendiente',
            fecha__lt=fecha_limite
        ).count()
        
        if facturas_vencidas > 0:
            alertas.append({
                'tipo': 'warning',
                'mensaje': f'{facturas_vencidas} factura(s) vencida(s)',
                'icono': 'bi-clock'
            })
    
    return {'alertas_globales': alertas}


def configuracion_global(request):
    """Context processor para configuración global"""
    if not request.user.is_authenticated:
        return {}
    
    try:
        tema_actual = ConfiguracionSistema.get_valor('tema_visual', 'azul')
        return {
            'configuracion_global': {
                'tema_visual': tema_actual
            },
            'tema_actual': tema_actual
        }
    except:
        return {
            'configuracion_global': {
                'tema_visual': 'azul'
            },
            'tema_actual': 'azul'
        }


def permisos_usuario(request):
    """Context processor para permisos del usuario en templates"""
    if not request.user.is_authenticated:
        return {}
    
    # Si es superusuario, tiene todos los permisos
    if request.user.is_superuser:
        return {
            'usuario_permisos': {
                'dashboard': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
                'productos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
                'proveedores': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
                'clientes': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
                'facturas_venta': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
                'facturas_compra': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
                'pagos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
                'stock': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
                'caja': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
                'reportes': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
                'configuracion': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
                'notificaciones': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
            }
        }
    
    # Obtener permisos del usuario
    permisos = PermisoUsuario.objects.filter(usuario=request.user)
    permisos_dict = {}
    
    for permiso in permisos:
        permisos_dict[permiso.modulo] = {
            'ver': permiso.puede_ver,
            'crear': permiso.puede_crear,
            'editar': permiso.puede_editar,
            'eliminar': permiso.puede_eliminar,
        }
    
    return {'usuario_permisos': permisos_dict} 