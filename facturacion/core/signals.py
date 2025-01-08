from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Producto, Factura, DetalleFactura, Notificacion, Pago, Caja, MovimientoCaja, PagoFactura

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

@receiver(post_save, sender=PagoFactura)
def crear_movimiento_caja_pago_factura(sender, instance, created, **kwargs):
    """
    Señal que crea automáticamente un movimiento de caja cuando se registra una relación PagoFactura
    """
    if created:
        print(f"Signal PagoFactura activado para pago #{instance.pago.id} - Factura #{instance.factura.numero} - Monto: {instance.monto}")
        
        try:
            factura = instance.factura
            pago = instance.pago
            
            print(f"Factura encontrada: #{factura.numero} - Tipo: {factura.tipo}")
            
            if factura.tipo == 'venta':
                # Solo para facturas de venta (ingresos)
                print(f"Procesando pago de factura de venta #{factura.numero}")
                
                try:
                    # Obtener la caja del día actual
                    caja_hoy = Caja.objects.filter(
                        fecha=timezone.now().date(),
                        cerrada=False
                    ).first()
                    
                    print(f"Caja activa encontrada: {caja_hoy}")
                    
                    if caja_hoy:
                        # Crear movimiento de caja como ingreso
                        movimiento = MovimientoCaja.registrar_movimiento(
                            caja=caja_hoy,
                            tipo='ingreso',
                            categoria='venta',
                            monto=instance.monto,
                            descripcion=f'Pago factura #{factura.numero} - {factura.cliente.nombre if factura.cliente else "Cliente"}',
                            usuario=pago.usuario,
                            referencia=f'Factura #{factura.numero}',
                            observacion=f'Pago registrado automáticamente desde factura de venta'
                        )
                        print(f"Movimiento de caja creado exitosamente: #{movimiento.id}")
                    else:
                        print("No se encontró caja activa para el día de hoy")
                except Exception as e:
                    print(f"Error al crear movimiento de caja: {e}")
            elif factura.tipo == 'compra':
                # Solo para facturas de compra (egresos)
                print(f"Procesando pago de factura de compra #{factura.numero}")
                
                try:
                    # Obtener la caja del día actual
                    caja_hoy = Caja.objects.filter(
                        fecha=timezone.now().date(),
                        cerrada=False
                    ).first()
                    
                    print(f"Caja activa encontrada (proveedor): {caja_hoy}")
                    
                    if caja_hoy:
                        # Crear movimiento de caja como egreso
                        movimiento = MovimientoCaja.registrar_movimiento(
                            caja=caja_hoy,
                            tipo='egreso',
                            categoria='pago_proveedor',
                            monto=instance.monto,
                            descripcion=f'Pago factura #{factura.numero} - {factura.proveedor.nombre if factura.proveedor else "Proveedor"}',
                            usuario=pago.usuario,
                            referencia=f'Factura #{factura.numero}',
                            observacion=f'Pago registrado automáticamente desde factura de compra'
                        )
                        print(f"Movimiento de caja creado exitosamente (proveedor): #{movimiento.id}")
                    else:
                        print("No se encontró caja activa para el día de hoy (proveedor)")
                except Exception as e:
                    print(f"Error al crear movimiento de caja (proveedor): {e}")
            else:
                print(f"Factura no es de venta ni compra, es de tipo: {factura.tipo}")
        except Exception as e:
            print(f"Error al obtener datos del pago/factura: {e}")

# Mantener las señales originales de Pago por compatibilidad, pero comentadas
# @receiver(post_save, sender=Pago)
# def crear_movimiento_caja_pago(sender, instance, created, **kwargs):
#     """
#     Señal que crea automáticamente un movimiento de caja cuando se registra un pago
#     """
#     if created:
#         print(f"Signal activado para pago #{instance.id} - Monto: {instance.monto_total}")
#         
#         # Obtener la factura a través de la relación PagoFactura
#         try:
#             pago_factura = instance.pagos_facturas.first()
#             print(f"PagoFactura encontrada: {pago_factura}")
#             
#             if pago_factura:
#                 factura = pago_factura.factura
#                 print(f"Factura encontrada: #{factura.numero} - Tipo: {factura.tipo}")
#                 
#                 if factura.tipo == 'venta':
#                     # Solo para facturas de venta (ingresos)
#                     print(f"Procesando pago de factura de venta #{factura.numero}")
#                     
#                     try:
#                         # Obtener la caja del día actual
#                         caja_hoy = Caja.objects.filter(
#                             fecha=timezone.now().date(),
#                             cerrada=False
#                         ).first()
#                         
#                         print(f"Caja activa encontrada: {caja_hoy}")
#                         
#                         if caja_hoy:
#                             # Crear movimiento de caja como ingreso
#                             movimiento = MovimientoCaja.registrar_movimiento(
#                                 caja=caja_hoy,
#                                 tipo='ingreso',
#                                 categoria='venta',
#                                 monto=instance.monto_total,
#                                 descripcion=f'Pago factura #{factura.numero} - {factura.cliente.nombre if factura.cliente else "Cliente"}',
#                                 usuario=instance.usuario,
#                                 referencia=f'Factura #{factura.numero}',
#                                 observacion=f'Pago registrado automáticamente desde factura de venta'
#                             )
#                             print(f"Movimiento de caja creado exitosamente: #{movimiento.id}")
#                         else:
#                             print("No se encontró caja activa para el día de hoy")
#                     except Exception as e:
#                         # Si hay algún error, no interrumpir el flujo del pago
#                         print(f"Error al crear movimiento de caja: {e}")
#                 else:
#                     print(f"Factura no es de venta, es de tipo: {factura.tipo}")
#             else:
#                 print("No se encontró relación PagoFactura")
#         except Exception as e:
#             print(f"Error al obtener factura del pago: {e}")

# @receiver(post_save, sender=Pago)
# def crear_movimiento_caja_pago_proveedor(sender, instance, created, **kwargs):
#     """
#     Señal que crea automáticamente un movimiento de caja cuando se registra un pago a proveedor
#     """
#     if created:
#         print(f"Signal proveedor activado para pago #{instance.id} - Monto: {instance.monto_total}")
#         
#         # Obtener la factura a través de la relación PagoFactura
#         try:
#             pago_factura = instance.pagos_facturas.first()
#             print(f"PagoFactura encontrada (proveedor): {pago_factura}")
#             
#             if pago_factura:
#                 factura = pago_factura.factura
#                 print(f"Factura encontrada (proveedor): #{factura.numero} - Tipo: {factura.tipo}")
#                 
#                 if factura.tipo == 'compra':
#                     # Solo para facturas de compra (egresos)
#                     print(f"Procesando pago de factura de compra #{factura.numero}")
#                     
#                     try:
#                         # Obtener la caja del día actual
#                         caja_hoy = Caja.objects.filter(
#                             fecha=timezone.now().date(),
#                             cerrada=False
#                         ).first()
#                         
#                         print(f"Caja activa encontrada (proveedor): {caja_hoy}")
#                         
#                         if caja_hoy:
#                             # Crear movimiento de caja como egreso
#                             movimiento = MovimientoCaja.registrar_movimiento(
#                                 caja=caja_hoy,
#                                 tipo='egreso',
#                                 categoria='pago_proveedor',
#                                 monto=instance.monto_total,
#                                 descripcion=f'Pago factura #{factura.numero} - {factura.proveedor.nombre if factura.proveedor else "Proveedor"}',
#                                 usuario=instance.usuario,
#                                 referencia=f'Factura #{factura.numero}',
#                                 observacion=f'Pago registrado automáticamente desde factura de compra'
#                             )
#                             print(f"Movimiento de caja creado exitosamente (proveedor): #{movimiento.id}")
#                         else:
#                             print("No se encontró caja activa para el día de hoy (proveedor)")
#                     except Exception as e:
#                         # Si hay algún error, no interrumpir el flujo del pago
#                         print(f"Error al crear movimiento de caja (proveedor): {e}")
#                 else:
#                     print(f"Factura no es de compra, es de tipo: {factura.tipo}")
#             else:
#                 print("No se encontró relación PagoFactura (proveedor)")
#         except Exception as e:
#             print(f"Error al obtener factura del pago (proveedor): {e}")
