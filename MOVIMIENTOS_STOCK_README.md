# 🔧 Solución: Movimientos de Stock - Avícola CVA

## 📋 Problema Identificado

**Problema**: Al hacer un ajuste de stock en productos, no se mostraba el movimiento en la sección "Movimientos de Stock".

**Causa**: El sistema no tenía un modelo específico para registrar movimientos de stock, y la función de ajuste de stock no creaba registros de movimientos.

## ✅ Solución Implementada

### 1. **Nuevo Modelo: MovimientoStock**

Se creó un modelo completo para registrar todos los movimientos de stock:

```python
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
    referencia = models.CharField(max_length=100, blank=True, null=True)
    observacion = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
```

### 2. **Método de Registro Automático**

Se implementó un método de clase para registrar movimientos automáticamente:

```python
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
```

### 3. **Función de Ajuste de Stock Actualizada**

Se modificó la función `producto_ajustar_stock` para registrar movimientos:

```python
@login_required
def producto_ajustar_stock(request, pk):
    """Ajustar el stock de un producto"""
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        tipo_movimiento = request.POST.get('tipo_movimiento')
        observacion = request.POST.get('observacion', '')
        try:
            cantidad = int(request.POST.get('cantidad', 0))
            if cantidad <= 0:
                raise ValueError('La cantidad debe ser mayor a 0')
            
            # Registrar el movimiento de stock
            if tipo_movimiento == 'entrada':
                MovimientoStock.registrar_movimiento(
                    producto=producto,
                    tipo='entrada',
                    origen='ajuste_manual',
                    cantidad=cantidad,
                    usuario=request.user,
                    observacion=observacion
                )
            elif tipo_movimiento == 'salida':
                if producto.stock < cantidad:
                    raise ValueError('No hay suficiente stock disponible')
                MovimientoStock.registrar_movimiento(
                    producto=producto,
                    tipo='salida',
                    origen='ajuste_manual',
                    cantidad=cantidad,
                    usuario=request.user,
                    observacion=observacion
                )
            
            # Crear notificación si el stock es bajo
            if producto.stock <= producto.stock_minimo:
                Notificacion.objects.create(
                    mensaje=f'Stock bajo en producto {producto.nombre} ({producto.stock} unidades)',
                    tipo='warning'
                )
            
            messages.success(request, f'Stock ajustado correctamente. Nuevo stock: {producto.stock}')
        except ValueError as e:
            messages.error(request, str(e))
        
    return redirect('productos_list')
```

### 4. **Vista de Movimientos Actualizada**

Se actualizó la vista `stock_movimientos` para usar el nuevo modelo:

```python
@login_required
def stock_movimientos(request):
    """Vista de movimientos de stock"""
    movimientos = MovimientoStock.objects.select_related('producto', 'usuario').all().order_by('-fecha')
    
    # Filtros mejorados
    q = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    origen = request.GET.get('origen', '')
    desde = request.GET.get('desde', '')
    hasta = request.GET.get('hasta', '')
    
    if q:
        movimientos = movimientos.filter(
            Q(producto__nombre__icontains=q) | Q(producto__codigo__icontains=q)
        )
    
    if tipo:
        movimientos = movimientos.filter(tipo=tipo)
    
    if origen:
        movimientos = movimientos.filter(origen=origen)
    
    if desde:
        movimientos = movimientos.filter(fecha__date__gte=desde)
    
    if hasta:
        movimientos = movimientos.filter(fecha__date__lte=hasta)
    
    # Paginación
    from django.core.paginator import Paginator
    paginator = Paginator(movimientos, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'movimientos': page_obj,
        'tipos_movimiento': MovimientoStock.TIPO_CHOICES,
        'origenes_movimiento': MovimientoStock.ORIGEN_CHOICES,
    }
    
    return render(request, 'stock_movimientos.html', context)
```

### 5. **Template Actualizado**

Se actualizó el template `stock_movimientos.html` para mostrar:

- **Fecha y hora** del movimiento
- **Producto** afectado
- **Tipo** de movimiento (Entrada/Salida/Ajuste/Inicial)
- **Origen** del movimiento
- **Cantidad** movida
- **Stock anterior** y **nuevo**
- **Usuario** que realizó el movimiento
- **Referencia** (opcional)

### 6. **Admin de Django**

Se registró el modelo en el admin para gestión desde la interfaz de administración:

```python
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
```

## 🧪 Pruebas Realizadas

Se ejecutó un script de prueba que verificó:

✅ **Registro de entradas** de stock  
✅ **Registro de salidas** de stock  
✅ **Cálculo correcto** de stock anterior y nuevo  
✅ **Asociación con usuario** que realiza el movimiento  
✅ **Observaciones** opcionales  
✅ **Integración** con el sistema de notificaciones  

### Resultado de las Pruebas:

```
=== PRUEBA DEL SISTEMA DE MOVIMIENTOS DE STOCK ===

✅ Usuario de prueba: admin
✅ Producto de prueba: Alpiste 1/2 kg. (Stock actual: 50)

📝 Registrando movimientos de prueba...
✅ Movimiento 1 registrado:
   - Tipo: Entrada
   - Cantidad: 50
   - Stock anterior: 50
   - Stock nuevo: 100
   - Observación: Prueba de entrada de stock

✅ Movimiento 2 registrado:
   - Tipo: Salida
   - Cantidad: 10
   - Stock anterior: 100
   - Stock nuevo: 90
   - Observación: Prueba de salida de stock

✅ Movimiento 3 registrado:
   - Tipo: Entrada
   - Cantidad: 25
   - Stock anterior: 90
   - Stock nuevo: 115
   - Observación: Segunda entrada de prueba

📊 Stock final del producto: 115
📋 Total de movimientos registrados: 3

✅ Prueba completada exitosamente!
```

## 🎯 Beneficios de la Solución

### **Para el Usuario:**
- ✅ **Visibilidad completa** de todos los movimientos de stock
- ✅ **Trazabilidad** de quién realizó cada movimiento
- ✅ **Historial detallado** con fechas y observaciones
- ✅ **Filtros avanzados** por tipo, origen, fecha, producto
- ✅ **Paginación** para manejar grandes volúmenes de datos

### **Para el Sistema:**
- ✅ **Auditoría completa** de movimientos de stock
- ✅ **Integración** con el sistema de notificaciones
- ✅ **Escalabilidad** para futuros tipos de movimientos
- ✅ **Consistencia** en el registro de datos
- ✅ **Seguridad** con validaciones y permisos

## 🚀 Cómo Usar

### **1. Ajustar Stock de un Producto:**
1. Ve a **Productos** → **Lista de Productos**
2. Haz clic en el botón **"Ajustar Stock"** del producto
3. Selecciona **Tipo** (Entrada/Salida)
4. Ingresa la **Cantidad**
5. Agrega una **Observación** (opcional)
6. Haz clic en **"Registrar Movimiento"**

### **2. Ver Movimientos de Stock:**
1. Ve a **Stock** → **Movimientos de Stock**
2. Usa los **filtros** para buscar movimientos específicos
3. Los movimientos se muestran ordenados por fecha (más recientes primero)

### **3. Filtros Disponibles:**
- **Buscar producto** por nombre o código
- **Filtrar por tipo** (Entrada/Salida/Ajuste/Inicial)
- **Filtrar por origen** (Ajuste Manual/Factura Compra/Factura Venta/etc.)
- **Filtrar por fecha** (desde/hasta)

## 📁 Archivos Modificados

- ✅ `core/models.py` - Nuevo modelo MovimientoStock
- ✅ `core/views.py` - Función de ajuste actualizada y vista de movimientos
- ✅ `core/admin.py` - Registro en admin de Django
- ✅ `templates/stock_movimientos.html` - Template actualizado
- ✅ `templates/productos_list.html` - Formulario con campo observación

## 🔄 Migraciones

Se crearon y aplicaron las migraciones necesarias:
- `core/migrations/0002_movimientostock.py`

---

> **Estado**: ✅ COMPLETADO  
> **Fecha**: Diciembre 2024  
> **Problema**: Resuelto completamente  
> **Sistema**: Avícola CVA 