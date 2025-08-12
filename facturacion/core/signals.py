from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Producto, Factura, DetalleFactura, Notificacion, Pago, Caja, MovimientoCaja

@receiver(pre_save, sender=Producto)
def verificar_stock_minimo(sender, instance, **kwargs):
    """
    Señal que verifica si un producto está por debajo del stock mínimo
    y crea una notificación si es necesario
    """
    if instance.stock and instance.stock_minimo and instance.stock <= instance.stock_minimo:
        Notificacion.objects.create(
            mensaje=f'Stock bajo en producto {instance.nombre}. Stock actual: {instance.stock}',
            tipo='warning'
        )

@receiver(post_save, sender=Factura)
def actualizar_stock_productos(sender, instance, created, **kwargs):
    """
    Señal que actualiza el stock de productos cuando se crea una factura
    """
    if created:
        detalles = DetalleFactura.objects.filter(factura=instance)
        for detalle in detalles:
            producto = detalle.producto
            if producto.stock is not None:  # Solo si el producto maneja stock
                producto.stock -= detalle.cantidad
                producto.save()

@receiver(post_save, sender=User)
def crear_notificacion_usuario(sender, instance, created, **kwargs):
    """
    Señal que crea una notificación cuando se registra un nuevo usuario
    """
    if created:
        Notificacion.objects.create(
            mensaje=f'Nuevo usuario registrado: {instance.username}',
            tipo='info'
        )

@receiver(post_save, sender=Pago)
def crear_movimiento_caja_pago(sender, instance, created, **kwargs):
    """
    Señal que crea automáticamente un movimiento de caja cuando se registra un pago
    """
    if created and instance.factura and instance.factura.tipo == 'venta':
        # Solo para facturas de venta (ingresos)
        try:
            # Obtener la caja del día actual
            caja_hoy = Caja.objects.filter(
                fecha=timezone.now().date(),
                cerrada=False
            ).first()
            
            if caja_hoy:
                # Crear movimiento de caja como ingreso
                MovimientoCaja.registrar_movimiento(
                    caja=caja_hoy,
                    tipo='ingreso',
                    categoria='venta',
                    monto=instance.monto_total,
                    descripcion=f'Pago factura #{instance.factura.numero} - {instance.factura.cliente.nombre if instance.factura.cliente else "Cliente"}',
                    usuario=instance.usuario,
                    referencia=f'Factura #{instance.factura.numero}',
                    observacion=f'Pago registrado automáticamente desde factura de venta'
                )
        except Exception as e:
            # Si hay algún error, no interrumpir el flujo del pago
            print(f"Error al crear movimiento de caja: {e}")

@receiver(post_save, sender=Pago)
def crear_movimiento_caja_pago_proveedor(sender, instance, created, **kwargs):
    """
    Señal que crea automáticamente un movimiento de caja cuando se registra un pago a proveedor
    """
    if created and instance.factura and instance.factura.tipo == 'compra':
        # Solo para facturas de compra (egresos)
        try:
            # Obtener la caja del día actual
            caja_hoy = Caja.objects.filter(
                fecha=timezone.now().date(),
                cerrada=False
            ).first()
            
            if caja_hoy:
                # Crear movimiento de caja como egreso
                MovimientoCaja.registrar_movimiento(
                    caja=caja_hoy,
                    tipo='egreso',
                    categoria='pago_proveedor',
                    monto=instance.monto_total,
                    descripcion=f'Pago factura #{instance.factura.numero} - {instance.factura.proveedor.nombre if instance.factura.proveedor else "Proveedor"}',
                    usuario=instance.usuario,
                    referencia=f'Factura #{instance.factura.numero}',
                    observacion=f'Pago registrado automáticamente desde factura de compra'
                )
        except Exception as e:
            # Si hay algún error, no interrumpir el flujo del pago
            print(f"Error al crear movimiento de caja: {e}")
