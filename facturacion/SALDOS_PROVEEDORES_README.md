# Actualización Automática de Saldos de Proveedores y Clientes

## Problema Identificado

Cuando se creaba una factura de compra, el saldo del proveedor no se actualizaba automáticamente, lo que causaba inconsistencias en los datos financieros.

## Solución Implementada

Se ha agregado la lógica para actualizar automáticamente los saldos de proveedores y clientes en las siguientes operaciones:

### 1. Creación de Facturas

**Archivo:** `facturacion/core/views.py` - Función `factura_crear()`

**Lógica agregada:**
```python
# Actualizar saldo del proveedor o cliente según el tipo de factura
if factura.tipo == 'compra' and factura.proveedor:
    factura.proveedor.saldo += factura.total
    factura.proveedor.save()
elif factura.tipo == 'venta' and factura.cliente:
    factura.cliente.saldo += factura.total
    factura.cliente.save()
```

**Comportamiento:**
- **Factura de Compra:** Aumenta el saldo del proveedor en el monto total de la factura
- **Factura de Venta:** Aumenta el saldo del cliente en el monto total de la factura

### 2. Registro de Pagos

**Archivo:** `facturacion/core/views.py` - Funciones `factura_pagos()` y `pago_crear()`

**Lógica agregada:**
```python
# Actualizar saldo del proveedor o cliente según el tipo de factura
if factura.tipo == 'compra' and factura.proveedor:
    factura.proveedor.saldo -= pago.monto
    factura.proveedor.save()
elif factura.tipo == 'venta' and factura.cliente:
    factura.cliente.saldo -= pago.monto
    factura.cliente.save()
```

**Comportamiento:**
- **Pago de Factura de Compra:** Reduce el saldo del proveedor en el monto del pago
- **Pago de Factura de Venta:** Reduce el saldo del cliente en el monto del pago

### 3. Eliminación de Pagos

**Archivo:** `facturacion/core/views.py` - Función `pago_eliminar()`

**Lógica agregada:**
```python
# Restaurar saldo del proveedor o cliente antes de eliminar el pago
if pago.factura.tipo == 'compra' and pago.factura.proveedor:
    pago.factura.proveedor.saldo += pago.monto
    pago.factura.proveedor.save()
elif pago.factura.tipo == 'venta' and pago.factura.cliente:
    pago.factura.cliente.saldo += pago.monto
    pago.factura.cliente.save()
```

**Comportamiento:**
- **Eliminar Pago de Compra:** Restaura el saldo del proveedor sumando el monto del pago eliminado
- **Eliminar Pago de Venta:** Restaura el saldo del cliente sumando el monto del pago eliminado

## Flujo de Saldos

### Para Proveedores (Facturas de Compra):

1. **Crear Factura de Compra:** `saldo_proveedor += total_factura`
2. **Registrar Pago:** `saldo_proveedor -= monto_pago`
3. **Eliminar Pago:** `saldo_proveedor += monto_pago`

### Para Clientes (Facturas de Venta):

1. **Crear Factura de Venta:** `saldo_cliente += total_factura`
2. **Registrar Pago:** `saldo_cliente -= monto_pago`
3. **Eliminar Pago:** `saldo_cliente += monto_pago`

## Beneficios

- ✅ **Consistencia de datos:** Los saldos siempre reflejan el estado real de las cuentas
- ✅ **Automatización:** No es necesario actualizar manualmente los saldos
- ✅ **Integridad:** Los saldos se mantienen sincronizados con las facturas y pagos
- ✅ **Trazabilidad:** Se puede rastrear el historial completo de movimientos

## Consideraciones

- Los saldos se actualizan automáticamente sin intervención manual
- La lógica maneja tanto facturas de compra como de venta
- Se incluyen validaciones para evitar errores cuando no hay proveedor o cliente asignado
- Los cambios son reversibles al eliminar pagos

## Archivos Modificados

- `facturacion/core/views.py`:
  - `factura_crear()` - Actualización de saldo al crear factura
  - `factura_pagos()` - Actualización de saldo al registrar pago
  - `pago_crear()` - Actualización de saldo al crear pago
  - `pago_eliminar()` - Restauración de saldo al eliminar pago 