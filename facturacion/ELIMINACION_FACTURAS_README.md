# Eliminación de Facturas con Ajuste de Stock

## Cambio Implementado

Se ha reemplazado la funcionalidad de "anular" facturas por "eliminar" facturas, que incluye el ajuste automático del stock de productos.

## Funcionalidad de Eliminación

### **¿Qué hace la eliminación?**

1. **Elimina permanentemente** la factura y todos sus datos asociados
2. **Ajusta el stock** de los productos según el tipo de factura
3. **Restaura saldos** de proveedores/clientes si hay pagos
4. **Registra movimientos** de stock para auditoría

### **Lógica de Ajuste de Stock:**

#### **Para Facturas de Compra:**
- **Al crear:** Se suma al stock
- **Al eliminar:** Se resta del stock
- **Movimiento registrado:** Salida por eliminación

#### **Para Facturas de Venta:**
- **Al crear:** Se resta del stock
- **Al eliminar:** Se suma al stock
- **Movimiento registrado:** Entrada por eliminación

## Cambios Técnicos

### 1. Vista Modificada

**Archivo:** `facturacion/core/views.py`

**Función:** `factura_eliminar()` (antes `factura_anular()`)

**Lógica implementada:**
```python
def factura_eliminar(request, pk):
    """Eliminar una factura y descontar productos del stock"""
    factura = get_object_or_404(Factura, pk=pk)
    if request.method == 'POST':
        try:
            # Descontar productos del stock según el tipo de factura
            for detalle in factura.detalles.all():
                producto = detalle.producto
                if factura.tipo == 'compra':
                    # Si es factura de compra, restar del stock
                    producto.stock -= detalle.cantidad
                    # Registrar movimiento de stock
                    MovimientoStock.registrar_movimiento(
                        producto=producto,
                        tipo='salida',
                        origen='factura_compra',
                        cantidad=detalle.cantidad,
                        usuario=request.user,
                        referencia=f'Factura #{factura.numero} eliminada',
                        observacion='Eliminación de factura de compra'
                    )
                else:
                    # Si es factura de venta, sumar al stock
                    producto.stock += detalle.cantidad
                    # Registrar movimiento de stock
                    MovimientoStock.registrar_movimiento(
                        producto=producto,
                        tipo='entrada',
                        origen='factura_venta',
                        cantidad=detalle.cantidad,
                        usuario=request.user,
                        referencia=f'Factura #{factura.numero} eliminada',
                        observacion='Eliminación de factura de venta'
                    )
                producto.save()
            
            # Restaurar saldos de proveedor/cliente si hay pagos
            if factura.tipo == 'compra' and factura.proveedor:
                factura.proveedor.saldo -= factura.total_pagado
                factura.proveedor.save()
            elif factura.tipo == 'venta' and factura.cliente:
                factura.cliente.saldo -= factura.total_pagado
                factura.cliente.save()
            
            # Eliminar la factura (esto también eliminará los pagos por CASCADE)
            factura.delete()
            
            messages.success(request, 'Factura eliminada correctamente.')
            return redirect('factura_list')
            
        except Exception as e:
            messages.error(request, f'Error al eliminar la factura: {str(e)}')
            return redirect('factura_ver', pk=pk)
    
    return render(request, 'factura_confirm_eliminar.html', {'factura': factura})
```

### 2. URL Actualizada

**Archivo:** `facturacion/core/urls.py`

**Cambio:**
```python
# Antes
path('facturas/<int:pk>/anular/', views.factura_anular, name='factura_anular'),

# Ahora
path('facturas/<int:pk>/eliminar/', views.factura_eliminar, name='factura_eliminar'),
```

### 3. Plantilla de Confirmación

**Archivo:** `facturacion/templates/factura_confirm_eliminar.html`

**Características:**
- ✅ **Advertencia crítica** sobre eliminación permanente
- ✅ **Información completa** de la factura
- ✅ **Efectos en el stock** claramente explicados
- ✅ **Tabla de productos** afectados con stock actual y final
- ✅ **Información de pagos** si existen

### 4. Interfaz Actualizada

**Archivo:** `facturacion/templates/factura_ver.html`

**Cambio:**
```html
<!-- Antes -->
<a href="{% url 'factura_anular' factura.pk %}" class="btn btn-outline-light me-2" title="Anular factura">
  <i class="bi bi-x-circle"></i> Anular
</a>

<!-- Ahora -->
<a href="{% url 'factura_eliminar' factura.pk %}" class="btn btn-outline-light me-2" title="Eliminar factura">
  <i class="bi bi-trash"></i> Eliminar
</a>
```

## Ejemplos de Comportamiento

### **Escenario 1: Eliminar Factura de Compra**
```
Producto: Pollo
Stock actual: 100 kg
Factura de compra: 50 kg
Al eliminar la factura:
- Stock final: 100 - 50 = 50 kg
- Movimiento registrado: Salida de 50 kg
- Saldo del proveedor: Se resta el monto pagado
```

### **Escenario 2: Eliminar Factura de Venta**
```
Producto: Pollo
Stock actual: 30 kg
Factura de venta: 20 kg
Al eliminar la factura:
- Stock final: 30 + 20 = 50 kg
- Movimiento registrado: Entrada de 20 kg
- Saldo del cliente: Se resta el monto pagado
```

## Beneficios del Sistema

### **Para el Usuario:**
- ✅ **Claridad:** Efectos claramente explicados antes de eliminar
- ✅ **Seguridad:** Confirmación obligatoria con información detallada
- ✅ **Trazabilidad:** Movimientos de stock registrados automáticamente

### **Para el Sistema:**
- ✅ **Integridad:** Stock siempre sincronizado con facturas
- ✅ **Auditoría:** Historial completo de movimientos
- ✅ **Consistencia:** Saldos de proveedores/clientes actualizados

### **Para la Gestión:**
- ✅ **Control:** Eliminación segura con efectos predecibles
- ✅ **Reportes:** Datos consistentes para análisis
- ✅ **Compliance:** Trazabilidad completa de cambios

## Consideraciones Importantes

### **Eliminación Permanente:**
- ❌ **No se puede deshacer** la eliminación
- ❌ **Se pierden todos los datos** de la factura
- ❌ **Se eliminan todos los pagos** asociados

### **Efectos en el Stock:**
- ⚠️ **Verificar stock final** antes de confirmar
- ⚠️ **Considerar productos con stock bajo**
- ⚠️ **Revisar movimientos** después de eliminar

### **Saldos de Proveedores/Clientes:**
- ⚠️ **Se restauran automáticamente** los saldos
- ⚠️ **Solo se afectan los pagos realizados**
- ⚠️ **Verificar saldos** después de eliminar

## Archivos Modificados

- `facturacion/core/views.py`:
  - Función `factura_eliminar()` con lógica de ajuste de stock
- `facturacion/core/urls.py`:
  - URL actualizada de anular a eliminar
- `facturacion/templates/factura_confirm_eliminar.html`:
  - Nueva plantilla de confirmación
- `facturacion/templates/factura_ver.html`:
  - Botón actualizado de anular a eliminar 