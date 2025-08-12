from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Producto, Factura, DetalleFactura, Notificacion

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
