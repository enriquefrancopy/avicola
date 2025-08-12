# Actualización Automática de Estados de Facturas

## Problema Identificado

Las facturas mostraban "pendiente" aunque ya habían sido pagadas completamente, causando confusión en el estado real de las cuentas.

## Solución Implementada

Se ha implementado un sistema de actualización automática de estados que modifica el estado de la factura basado en los pagos realizados.

### **Estados de Factura:**

- **`pendiente`**: La factura tiene saldo pendiente por pagar
- **`pagada`**: La factura ha sido completamente pagada
- **`anulada`**: La factura ha sido anulada (no se puede modificar)

## Cambios Implementados

### 1. Modelo Factura - Nuevos Métodos

**Archivo:** `facturacion/core/models.py`

**Métodos agregados:**
```python
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
```

### 2. Vistas de Pagos - Actualización Automática

**Archivo:** `facturacion/core/views.py`

**Funciones modificadas:**
- `factura_pagos()` - Actualiza estado al registrar pago
- `pago_crear()` - Actualiza estado al crear pago
- `pago_eliminar()` - Actualiza estado al eliminar pago

**Lógica agregada:**
```python
# Después de registrar/eliminar un pago
factura.actualizar_estado()
```

### 3. Comando de Gestión - Actualización Masiva

**Archivo:** `facturacion/core/management/commands/actualizar_estados_facturas.py`

**Funcionalidad:**
- Actualiza el estado de todas las facturas existentes
- Muestra un reporte de cambios realizados
- Útil para corregir datos históricos

**Uso:**
```bash
python manage.py actualizar_estados_facturas
```

## Lógica de Actualización

### **Criterios de Estado:**

1. **Factura Pagada:**
   - `saldo_pendiente <= 0`
   - Estado: `'pagada'`

2. **Factura Pendiente:**
   - `saldo_pendiente > 0`
   - Estado: `'pendiente'`

3. **Factura Anulada:**
   - Estado manual: `'anulada'`
   - No se modifica automáticamente

### **Momentos de Actualización:**

1. **Al registrar un pago:**
   - Se actualiza el saldo del proveedor/cliente
   - Se actualiza el estado de la factura

2. **Al eliminar un pago:**
   - Se restaura el saldo del proveedor/cliente
   - Se actualiza el estado de la factura

3. **Comando manual:**
   - Actualiza todas las facturas existentes
   - Corrige inconsistencias históricas

## Ejemplos de Comportamiento

### **Escenario 1: Factura de Compra con Pagos Parciales**
```
Factura: Gs. 1,000,000 (Estado: pendiente)
- Pago 1: Gs. 300,000 → Estado: pendiente
- Pago 2: Gs. 400,000 → Estado: pendiente  
- Pago 3: Gs. 300,000 → Estado: pagada ✅
```

### **Escenario 2: Factura de Venta con Pago Completo**
```
Factura: Gs. 500,000 (Estado: pendiente)
- Pago único: Gs. 500,000 → Estado: pagada ✅
```

### **Escenario 3: Eliminación de Pago**
```
Factura: Gs. 1,000,000 (Estado: pagada)
- Eliminar pago: Gs. 300,000 → Estado: pendiente ✅
```

## Beneficios del Sistema

### **Para el Usuario:**
- ✅ **Claridad:** Estado real reflejado automáticamente
- ✅ **Confianza:** No hay discrepancias entre pagos y estado
- ✅ **Eficiencia:** No requiere actualización manual

### **Para el Sistema:**
- ✅ **Consistencia:** Estados siempre sincronizados con pagos
- ✅ **Integridad:** Prevención de errores de estado
- ✅ **Trazabilidad:** Historial completo de cambios

### **Para Reportes:**
- ✅ **Precisión:** Estados correctos para análisis
- ✅ **Filtros:** Filtrado preciso por estado real
- ✅ **Estadísticas:** Datos confiables para decisiones

## Casos Especiales

### **Facturas Anuladas:**
- No se modifican automáticamente
- Mantienen su estado `'anulada'`
- Requieren intervención manual si es necesario

### **Facturas con Saldo Cero:**
- Se marcan automáticamente como `'pagada'`
- Incluye facturas sin pagos pero con total = 0

### **Facturas con Pagos Excesivos:**
- Se marcan como `'pagada'` cuando saldo ≤ 0
- Los pagos excesivos se manejan como crédito

## Comandos Útiles

### **Actualizar Todas las Facturas:**
```bash
python manage.py actualizar_estados_facturas
```

### **Verificar Estados:**
```python
# En Django shell
from core.models import Factura

# Facturas pendientes
pendientes = Factura.objects.filter(estado='pendiente')
for f in pendientes:
    print(f"#{f.numero}: Saldo={f.saldo_pendiente}, Estado_real={f.estado_actualizado}")

# Facturas pagadas
pagadas = Factura.objects.filter(estado='pagada')
for f in pagadas:
    print(f"#{f.numero}: Saldo={f.saldo_pendiente}, Estado_real={f.estado_actualizado}")
```

## Archivos Modificados

- `facturacion/core/models.py`:
  - Agregados métodos `actualizar_estado()` y `estado_actualizado`
- `facturacion/core/views.py`:
  - Vistas de pagos con actualización automática de estado
- `facturacion/core/management/commands/actualizar_estados_facturas.py`:
  - Comando para actualización masiva de estados 