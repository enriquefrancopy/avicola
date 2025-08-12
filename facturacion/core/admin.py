from django.contrib import admin
from .models import (
    Producto, Proveedor, Cliente, Factura, DetalleFactura, 
    Pago, PagoFactura, Notificacion, ConfiguracionSistema, MovimientoStock,
    Caja, MovimientoCaja, Gasto, Denominacion
)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'precio', 'stock', 'stock_minimo', 'activo']
    list_filter = ['activo', 'iva']
    search_fields = ['codigo', 'nombre']
    list_editable = ['stock', 'stock_minimo', 'activo']

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'rif', 'telefono', 'email', 'saldo', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'rif', 'email']

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'rif', 'telefono', 'email', 'saldo', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'rif', 'email']

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'tipo', 'fecha', 'proveedor', 'cliente', 'total', 'estado']
    list_filter = ['tipo', 'estado', 'fecha']
    search_fields = ['numero', 'proveedor__nombre', 'cliente__nombre']
    date_hierarchy = 'fecha'

@admin.register(DetalleFactura)
class DetalleFacturaAdmin(admin.ModelAdmin):
    list_display = ['factura', 'producto', 'cantidad', 'precio_unitario', 'total']
    list_filter = ['factura__tipo', 'producto']
    search_fields = ['factura__numero', 'producto__nombre']

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['id', 'fecha', 'monto_total', 'tipo', 'usuario']
    list_filter = ['tipo', 'fecha']
    search_fields = ['referencia']

@admin.register(PagoFactura)
class PagoFacturaAdmin(admin.ModelAdmin):
    list_display = ['pago', 'factura', 'monto', 'fecha_asignacion']
    list_filter = ['fecha_asignacion']
    search_fields = ['pago__id', 'factura__numero']

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['mensaje', 'tipo', 'fecha', 'leida', 'usuario']
    list_filter = ['tipo', 'leida', 'fecha']
    search_fields = ['mensaje']
    list_editable = ['leida']

@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    list_display = ['clave', 'valor', 'categoria', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['clave', 'descripcion']

@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ['producto', 'tipo', 'origen', 'cantidad', 'stock_anterior', 'stock_nuevo', 'usuario', 'fecha']
    list_filter = ['tipo', 'origen', 'fecha']
    search_fields = ['producto__nombre', 'producto__codigo', 'usuario__username']
    date_hierarchy = 'fecha'
    readonly_fields = ['stock_anterior', 'stock_nuevo']
    
    def has_add_permission(self, request):
        # No permitir agregar movimientos manualmente desde el admin
        return False

@admin.register(Denominacion)
class DenominacionAdmin(admin.ModelAdmin):
    list_display = ['caja', 'valor', 'cantidad', 'subtotal']
    list_filter = ['valor', 'caja__fecha']
    search_fields = ['caja__fecha']
    date_hierarchy = 'caja__fecha'

@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'saldo_inicial', 'saldo_final', 'saldo_real', 'diferencia', 'cerrada', 'usuario_apertura']
    list_filter = ['cerrada', 'fecha']
    search_fields = ['fecha']
    date_hierarchy = 'fecha'
    readonly_fields = ['saldo_final', 'diferencia', 'fecha_apertura', 'fecha_cierre']

@admin.register(MovimientoCaja)
class MovimientoCajaAdmin(admin.ModelAdmin):
    list_display = ['caja', 'tipo', 'categoria', 'monto', 'descripcion', 'usuario', 'fecha']
    list_filter = ['tipo', 'categoria', 'fecha']
    search_fields = ['descripcion', 'referencia', 'usuario__username']
    date_hierarchy = 'fecha'

@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ['caja', 'categoria', 'descripcion', 'monto', 'comprobante', 'usuario', 'fecha']
    list_filter = ['categoria', 'fecha']
    search_fields = ['descripcion', 'comprobante', 'usuario__username']
    date_hierarchy = 'fecha' 