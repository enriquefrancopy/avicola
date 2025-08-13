from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    costo = models.IntegerField(default=0)
    precio = models.IntegerField()
    stock = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=10)
    iva = models.IntegerField(default=10)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)
    rif = models.CharField(max_length=20, unique=True)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    saldo = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.rif})'

class Cliente(models.Model):
    nombre = models.CharField(max_length=200)
    rif = models.CharField(max_length=20, unique=True)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    saldo = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.rif})'

class Factura(models.Model):
    TIPO_CHOICES = [
        ('compra', 'Compra'),
        ('venta', 'Venta'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
        ('anulada', 'Anulada'),
    ]

    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='compra')
    numero = models.CharField(max_length=20)
    fecha = models.DateTimeField(default=timezone.now)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, null=True, blank=True)
    subtotal = models.IntegerField()
    iva = models.IntegerField()
    total = models.IntegerField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    observacion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-fecha']
        unique_together = ['tipo', 'numero']

    def __str__(self):
        if self.tipo == 'compra':
            return f'Factura Compra #{self.numero} - {self.proveedor}'
        else:
            return f'Factura Venta #{self.numero} - {self.cliente}'
    
    def save(self, *args, **kwargs):
        if not self.numero:
            # Generar número correlativo por tipo
            ultima_factura = Factura.objects.filter(tipo=self.tipo).order_by('-numero').first()
            if ultima_factura:
                try:
                    ultimo_numero = int(ultima_factura.numero)
                    self.numero = str(ultimo_numero + 1).zfill(6)
                except ValueError:
                    self.numero = '000001'
            else:
                self.numero = '000001'
        super().save(*args, **kwargs)
    
    @property
    def total_pagado(self):
        """Calcula el total pagado de la factura"""
        return sum(pago_factura.monto for pago_factura in self.pagos_facturas.all())
    
    @property
    def saldo_pendiente(self):
        """Calcula el saldo pendiente de la factura"""
        return self.total - self.total_pagado
    
    @property
    def porcentaje_pagado(self):
        """Calcula el porcentaje pagado de la factura"""
        if self.total == 0:
            return 0
        return (self.total_pagado / self.total) * 100
    
    @property
    def total_iva(self):
        """Retorna el total de IVA de la factura"""
        return self.iva
    
    def puede_pagar_parcialmente(self):
        """Determina si la factura permite pagos parciales"""
        # Solo las facturas de compra (proveedores) permiten pagos parciales
        return self.tipo == 'compra'
    
    def validar_monto_pago(self, monto):
        """Valida si el monto del pago es válido según el tipo de factura"""
        if self.tipo == 'compra':
            # Para proveedores: pagos parciales permitidos
            return 0 < monto <= self.saldo_pendiente
        else:
            # Para clientes: solo pagos completos
            return monto == self.saldo_pendiente
    
    def actualizar_estado(self):
        """Actualiza el estado de la factura basado en los pagos realizados"""
        if self.saldo_pendiente <= 0:
            self.estado = 'pagada'
        else:
            self.estado = 'pendiente'
        self.save(update_fields=['estado'])
    
    @property
    def estado_actualizado(self):
        """Retorna el estado actual basado en los pagos, sin guardar"""
        if self.saldo_pendiente <= 0:
            return 'pagada'
        else:
            return 'pendiente'

class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.IntegerField()
    iva = models.IntegerField()
    subtotal = models.IntegerField()
    total = models.IntegerField()

    class Meta:
        verbose_name = 'Detalle de Factura'
        verbose_name_plural = 'Detalles de Factura'

    def __str__(self):
        return f'{self.producto} - {self.cantidad} unidades'

class Pago(models.Model):
    TIPO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('cheque', 'Cheque'),
    ]

    fecha = models.DateTimeField(default=timezone.now)
    monto_total = models.IntegerField(default=0, help_text='Monto total del pago')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    referencia = models.CharField(max_length=50, blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    observacion = models.TextField(blank=True, null=True, help_text='Observaciones adicionales del pago')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, null=True, blank=True, help_text='Proveedor al que se realiza el pago')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, null=True, blank=True, help_text='Cliente que realiza el pago')

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha']

    def __str__(self):
        return f'Pago {self.tipo} - Gs. {self.monto_total:,} - {self.fecha.strftime("%d/%m/%Y")}'
    
    @property
    def monto_asignado(self):
        """Calcula el monto total asignado a facturas"""
        return sum(pago_factura.monto for pago_factura in self.pagos_facturas.all())
    
    @property
    def monto_disponible(self):
        """Calcula el monto disponible para asignar"""
        return self.monto_total - self.monto_asignado
    
    @property
    def facturas_afectadas(self):
        """Retorna las facturas afectadas por este pago"""
        return [pago_factura.factura for pago_factura in self.pagos_facturas.all()]
    
    @property
    def completamente_asignado(self):
        """Verifica si el pago está completamente asignado"""
        return self.monto_disponible == 0
    
    def puede_asignar_monto(self, monto):
        """Verifica si puede asignar un monto específico"""
        return self.monto_disponible >= monto
    
    def asignar_a_factura(self, factura, monto):
        """Asigna un monto específico a una factura"""
        if not self.puede_asignar_monto(monto):
            raise ValueError(f'No hay suficiente monto disponible. Disponible: {self.monto_disponible}, Solicitado: {monto}')
        
        # Crear la asignación
        PagoFactura.objects.create(
            pago=self,
            factura=factura,
            monto=monto
        )
        
        # Actualizar saldo del proveedor o cliente
        if factura.tipo == 'compra' and factura.proveedor:
            factura.proveedor.saldo -= monto
            factura.proveedor.save()
        elif factura.tipo == 'venta' and factura.cliente:
            factura.cliente.saldo -= monto
            factura.cliente.save()
        
        # Actualizar estado de la factura
        factura.actualizar_estado()

class PagoFactura(models.Model):
    """Modelo intermedio para relacionar pagos con facturas y asignar montos específicos"""
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name='pagos_facturas')
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='pagos_facturas')
    monto = models.IntegerField(help_text='Monto asignado de este pago a esta factura')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Asignación de Pago a Factura'
        verbose_name_plural = 'Asignaciones de Pagos a Facturas'
        unique_together = ['pago', 'factura']
        ordering = ['-fecha_asignacion']
    
    def __str__(self):
        return f'Pago #{self.pago.id} → Factura #{self.factura.numero} - Gs. {self.monto:,}'
    
    def save(self, *args, **kwargs):
        # Validar que el monto no exceda el saldo pendiente de la factura
        if self.monto > self.factura.saldo_pendiente:
            raise ValueError(f'El monto asignado ({self.monto:,}) excede el saldo pendiente de la factura ({self.factura.saldo_pendiente:,})')
        
        # Validar que el monto no exceda el monto disponible del pago
        monto_disponible = self.pago.monto_total - sum(
            pf.monto for pf in self.pago.pagos_facturas.all() if pf != self
        )
        if self.monto > monto_disponible:
            raise ValueError(f'El monto asignado ({self.monto:,}) excede el monto disponible del pago ({monto_disponible:,})')
        
        super().save(*args, **kwargs)
        
        # Actualizar el estado de la factura después de guardar
        self.factura.actualizar_estado()
        
        # Actualizar saldo del proveedor o cliente
        if self.factura.tipo == 'compra' and self.factura.proveedor:
            self.factura.proveedor.saldo -= self.monto
            self.factura.proveedor.save()
        elif self.factura.tipo == 'venta' and self.factura.cliente:
            self.factura.cliente.saldo += self.monto
            self.factura.cliente.save()
    
    def delete(self, *args, **kwargs):
        """Eliminar la asignación y restaurar saldos"""
        # Guardar el monto antes de eliminar
        monto_eliminado = self.monto
        factura = self.factura
        
        # Solo manejar facturas de compra (proveedores)
        if factura.tipo == 'compra' and factura.proveedor:
            factura.proveedor.saldo += monto_eliminado
            factura.proveedor.save()
        
        # Eliminar la asignación
        super().delete(*args, **kwargs)
        
        # Actualizar el estado de la factura después de eliminar
        factura.actualizar_estado()

class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('info', 'Información'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
    ]

    mensaje = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='info')
    fecha = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.tipo}: {self.mensaje[:50]}'

class ConfiguracionSistema(models.Model):
    """Configuraciones del sistema"""
    CATEGORIA_CHOICES = [
        ('general', 'General'),
        ('alertas', 'Alertas'),
        ('email', 'Email'),
        ('stock', 'Stock'),
        ('facturacion', 'Facturación'),
        ('tema', 'Tema Visual'),
    ]
    
    clave = models.CharField(max_length=100, unique=True)
    valor = models.TextField()
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='general')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'
        ordering = ['categoria', 'clave']
    
    def __str__(self):
        return f"{self.categoria}: {self.clave}"
    
    @classmethod
    def get_valor(cls, clave, valor_por_defecto=None):
        """Obtener valor de configuración"""
        try:
            config = cls.objects.get(clave=clave, activo=True)
            return config.valor
        except cls.DoesNotExist:
            return valor_por_defecto
    
    @classmethod
    def set_valor(cls, clave, valor, descripcion='', categoria='general'):
        """Establecer valor de configuración"""
        config, created = cls.objects.get_or_create(
            clave=clave,
            defaults={
                'valor': str(valor),
                'descripcion': descripcion,
                'categoria': categoria,
            }
        )
        if not created:
            config.valor = str(valor)
            config.descripcion = descripcion
            config.categoria = categoria
            config.save()
        return config



class MovimientoStock(models.Model):
    """Modelo para registrar movimientos de stock"""
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
        ('inicial', 'Stock Inicial'),
    ]
    
    ORIGEN_CHOICES = [
        ('factura_compra', 'Factura de Compra'),
        ('factura_venta', 'Factura de Venta'),
        ('ajuste_manual', 'Ajuste Manual'),
        ('stock_inicial', 'Stock Inicial'),
        ('devolucion', 'Devolución'),
        ('merma', 'Merma'),
    ]
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos_stock')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    origen = models.CharField(max_length=20, choices=ORIGEN_CHOICES)
    cantidad = models.IntegerField()
    stock_anterior = models.IntegerField()
    stock_nuevo = models.IntegerField()
    referencia = models.CharField(max_length=100, blank=True, null=True, help_text='Número de factura, observación, etc.')
    observacion = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Movimiento de Stock'
        verbose_name_plural = 'Movimientos de Stock'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.get_tipo_display()} ({self.cantidad}) - {self.fecha.strftime('%d/%m/%Y %H:%M')}"
    
    @classmethod
    def registrar_movimiento(cls, producto, tipo, origen, cantidad, usuario, referencia='', observacion=''):
        """Registrar un movimiento de stock"""
        stock_anterior = producto.stock
        
        # Calcular el nuevo stock según el tipo de movimiento
        if tipo == 'entrada':
            stock_nuevo = stock_anterior + cantidad
        elif tipo == 'salida':
            stock_nuevo = stock_anterior - cantidad
        elif tipo == 'ajuste':
            stock_nuevo = cantidad  # Para ajustes, la cantidad es el nuevo stock
        else:  # inicial
            stock_nuevo = cantidad
        
        # Crear el registro de movimiento
        movimiento = cls.objects.create(
            producto=producto,
            tipo=tipo,
            origen=origen,
            cantidad=cantidad,
            stock_anterior=stock_anterior,
            stock_nuevo=stock_nuevo,
            referencia=referencia,
            observacion=observacion,
            usuario=usuario
        )
        
        # Actualizar el stock del producto
        producto.stock = stock_nuevo
        producto.save()
        
        return movimiento

class Denominacion(models.Model):
    """Modelo para las denominaciones de billetes y monedas"""
    VALOR_CHOICES = [
        (100000, '100.000 Gs.'),
        (50000, '50.000 Gs.'),
        (20000, '20.000 Gs.'),
        (10000, '10.000 Gs.'),
        (5000, '5.000 Gs.'),
        (2000, '2.000 Gs.'),
        (1000, '1.000 Gs.'),
        (500, '500 Gs.'),
        (100, '100 Gs.'),
        (50, '50 Gs.'),
    ]
    
    valor = models.IntegerField(choices=VALOR_CHOICES)
    cantidad = models.IntegerField(default=0)
    caja = models.ForeignKey('Caja', on_delete=models.CASCADE, related_name='denominaciones')
    
    class Meta:
        verbose_name = 'Denominación'
        verbose_name_plural = 'Denominaciones'
        unique_together = ['valor', 'caja']
        ordering = ['-valor']
    
    def __str__(self):
        return f"{self.get_valor_display()} - {self.cantidad} unidades"
    
    @property
    def subtotal(self):
        """Calcular el subtotal de esta denominación"""
        return self.valor * self.cantidad

class Caja(models.Model):
    """Modelo para control de caja diario"""
    fecha = models.DateField(unique=True)
    saldo_inicial = models.IntegerField(default=0)
    saldo_final = models.IntegerField(default=0)
    saldo_real = models.IntegerField(default=0)
    diferencia = models.IntegerField(default=0)
    observaciones = models.TextField(blank=True, null=True)
    cerrada = models.BooleanField(default=False)
    usuario_apertura = models.ForeignKey(User, on_delete=models.PROTECT, related_name='cajas_aperturadas')
    usuario_cierre = models.ForeignKey(User, on_delete=models.PROTECT, related_name='cajas_cerradas', null=True, blank=True)
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Caja'
        verbose_name_plural = 'Cajas'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Caja {self.fecha.strftime('%d/%m/%Y')} - {'Cerrada' if self.cerrada else 'Abierta'}"
    
    def calcular_saldo_inicial_denominaciones(self):
        """Calcular el saldo inicial basado en las denominaciones"""
        total = 0
        for denominacion in self.denominaciones.all():
            total += denominacion.subtotal
        self.saldo_inicial = total
        return total
    
    def calcular_saldo_final(self):
        """Calcular saldo final basado en movimientos"""
        total_ingresos = self.movimientos.filter(tipo='ingreso').aggregate(total=models.Sum('monto'))['total'] or 0
        total_egresos = self.movimientos.filter(tipo='egreso').aggregate(total=models.Sum('monto'))['total'] or 0
        self.saldo_final = self.saldo_inicial + total_ingresos - total_egresos
        return self.saldo_final
    
    def calcular_diferencia(self):
        """Calcular diferencia entre saldo final y saldo real"""
        self.diferencia = self.saldo_real - self.saldo_final
        return self.diferencia
    
    def cerrar_caja(self, saldo_real, usuario_cierre, observaciones=''):
        """Cerrar la caja con arqueo"""
        self.saldo_real = saldo_real
        self.calcular_saldo_final()
        self.calcular_diferencia()
        self.cerrada = True
        self.usuario_cierre = usuario_cierre
        self.fecha_cierre = timezone.now()
        self.observaciones = observaciones
        self.save()
    
    @classmethod
    def obtener_caja_activa(cls, fecha=None):
        """
        Obtener la caja activa para una fecha específica o el día actual
        """
        if fecha is None:
            fecha = timezone.now().date()
        
        # Buscar caja activa para la fecha específica
        caja = cls.objects.filter(
            fecha=fecha,
            cerrada=False
        ).first()
        
        # Si no hay caja para hoy, buscar la caja más reciente abierta
        if not caja:
            caja = cls.objects.filter(
                cerrada=False
            ).order_by('-fecha').first()
        
        return caja
    
    @classmethod
    def obtener_ultimo_saldo_cierre(cls):
        """
        Obtener el saldo final de la última caja cerrada
        """
        ultima_caja_cerrada = cls.objects.filter(
            cerrada=True
        ).order_by('-fecha').first()
        
        if ultima_caja_cerrada:
            return ultima_caja_cerrada.saldo_final
        return 0


class MovimientoCaja(models.Model):
    """Modelo para registrar movimientos de caja"""
    TIPO_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('egreso', 'Egreso'),
    ]
    
    CATEGORIA_CHOICES = [
        ('venta', 'Venta'),
        ('pago_proveedor', 'Pago a Proveedor'),
        ('gasto', 'Gasto'),
        ('retiro', 'Retiro'),
        ('deposito', 'Depósito'),
        ('ajuste', 'Ajuste'),
        ('otro', 'Otro'),
    ]
    
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    monto = models.IntegerField()
    descripcion = models.CharField(max_length=200)
    referencia = models.CharField(max_length=100, blank=True, null=True, help_text='Número de factura, recibo, etc.')
    observacion = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Movimiento de Caja'
        verbose_name_plural = 'Movimientos de Caja'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.get_categoria_display()} - {self.monto} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"
    
    @classmethod
    def registrar_movimiento(cls, caja, tipo, categoria, monto, descripcion, usuario, referencia='', observacion=''):
        """Registrar un movimiento de caja"""
        movimiento = cls.objects.create(
            caja=caja,
            tipo=tipo,
            categoria=categoria,
            monto=monto,
            descripcion=descripcion,
            referencia=referencia,
            observacion=observacion,
            usuario=usuario
        )
        
        # Actualizar saldo final de la caja
        caja.calcular_saldo_final()
        caja.save()
        
        return movimiento


class Gasto(models.Model):
    """Modelo para registrar gastos diarios"""
    CATEGORIA_CHOICES = [
        ('combustible', 'Combustible'),
        ('mantenimiento', 'Mantenimiento'),
        ('servicios', 'Servicios'),
        ('alimentacion', 'Alimentación'),
        ('transporte', 'Transporte'),
        ('utiles', 'Útiles de Oficina'),
        ('limpieza', 'Limpieza'),
        ('seguridad', 'Seguridad'),
        ('otro', 'Otro'),
    ]
    
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name='gastos')
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    descripcion = models.CharField(max_length=200)
    monto = models.IntegerField()
    comprobante = models.CharField(max_length=100, blank=True, null=True, help_text='Número de factura, recibo, etc.')
    observacion = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Gasto'
        verbose_name_plural = 'Gastos'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.get_categoria_display()} - {self.descripcion} - {self.monto} - {self.fecha.strftime('%d/%m/%Y')}"
    
    def save(self, *args, **kwargs):
        # Crear movimiento de caja automáticamente
        super().save(*args, **kwargs)
        
        # Registrar movimiento de caja si no existe
        if not hasattr(self, '_movimiento_creado'):
            MovimientoCaja.registrar_movimiento(
                caja=self.caja,
                tipo='egreso',
                categoria='gasto',
                monto=self.monto,
                descripcion=f"Gasto: {self.get_categoria_display()} - {self.descripcion}",
                usuario=self.usuario,
                referencia=self.comprobante,
                observacion=self.observacion
            )
            self._movimiento_creado = True
