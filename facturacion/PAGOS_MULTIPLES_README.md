# Sistema de Pagos Múltiples

## Descripción General

Se ha implementado un sistema de pagos múltiples que permite que un pago pueda cancelar varias facturas. Esta funcionalidad es especialmente útil para casos donde se recibe un pago único que cubre múltiples facturas pendientes de un mismo proveedor o cliente.

## Arquitectura del Sistema

### Modelos Principales

#### 1. Modelo `Pago` (Modificado)
```python
class Pago(models.Model):
    fecha = models.DateTimeField(default=timezone.now)
    monto_total = models.IntegerField(default=0, help_text='Monto total del pago')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    referencia = models.CharField(max_length=50, blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    observacion = models.TextField(blank=True, null=True)
```

**Propiedades calculadas:**
- `monto_asignado`: Calcula el total asignado a facturas
- `monto_disponible`: Calcula el monto disponible para asignar
- `facturas_afectadas`: Retorna las facturas afectadas por este pago

#### 2. Modelo `PagoFactura` (Nuevo)
```python
class PagoFactura(models.Model):
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name='pagos_facturas')
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='pagos_facturas')
    monto = models.IntegerField(help_text='Monto asignado de este pago a esta factura')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
```

**Características:**
- Relación muchos a muchos entre pagos y facturas
- Asigna montos específicos a cada factura
- Validaciones automáticas de montos
- Actualización automática de saldos

## Funcionalidades Implementadas

### 1. Creación de Pagos Múltiples

**URL:** `/pagos/multiple/crear/`

**Características:**
- Crear un pago con monto total
- Seleccionar proveedor o cliente
- Ver facturas pendientes disponibles
- Validaciones de montos

### 2. Asignación de Facturas

**URL:** `/pagos/<pago_id>/asignar/`

**Características:**
- Asignar montos específicos a facturas
- Validación en tiempo real
- Interfaz intuitiva con checkboxes
- Cálculo automático de totales

### 3. Visualización de Pagos

**URL:** `/pagos/<pago_id>/ver/`

**Características:**
- Ver detalles completos del pago
- Lista de facturas asignadas
- Resumen financiero
- Acciones de gestión

### 4. Eliminación de Pagos y Asignaciones

**URLs:**
- `/pagos/<pago_id>/eliminar/` - Eliminar pago completo
- `/asignaciones/<pk>/eliminar/` - Eliminar asignación específica

**Características:**
- Restauración automática de saldos
- Confirmaciones detalladas
- Trazabilidad completa

## Flujo de Trabajo

### Escenario 1: Pago Múltiple a Proveedor

1. **Crear Pago:**
   ```
   Proveedor: Distribuidora ABC
   Monto Total: Gs. 2,500,000
   Tipo: Transferencia
   Referencia: TRANS-001
   ```

2. **Asignar a Facturas:**
   ```
   Factura #001: Gs. 800,000 (32%)
   Factura #002: Gs. 1,200,000 (48%)
   Factura #003: Gs. 500,000 (20%)
   Total Asignado: Gs. 2,500,000 (100%)
   ```

3. **Resultado:**
   - Saldo del proveedor se reduce en Gs. 2,500,000
   - Las 3 facturas se marcan como pagadas
   - Pago queda completamente asignado

### Escenario 2: Pago Parcial Múltiple

1. **Crear Pago:**
   ```
   Cliente: Restaurante XYZ
   Monto Total: Gs. 1,000,000
   Tipo: Efectivo
   ```

2. **Asignar a Facturas:**
   ```
   Factura #004: Gs. 600,000 (60%)
   Factura #005: Gs. 400,000 (40%)
   Total Asignado: Gs. 1,000,000 (100%)
   ```

3. **Resultado:**
   - Saldo del cliente se reduce en Gs. 1,000,000
   - Las 2 facturas se marcan como pagadas
   - Pago queda completamente asignado

## Validaciones Implementadas

### 1. Validaciones de Monto
- **Monto total > 0**: El pago debe tener un monto válido
- **Monto asignado ≤ Monto total**: No se puede asignar más del disponible
- **Monto por factura ≤ Saldo pendiente**: No se puede asignar más del saldo de la factura

### 2. Validaciones de Estado
- **Facturas pendientes**: Solo se pueden asignar facturas con estado 'pendiente'
- **Proveedor/Cliente**: Las facturas deben corresponder al mismo proveedor o cliente

### 3. Validaciones de Integridad
- **Saldos automáticos**: Los saldos se actualizan automáticamente
- **Estados de facturas**: Los estados se actualizan según los pagos
- **Trazabilidad**: Todo cambio queda registrado

## Interfaz de Usuario

### 1. Lista de Facturas
- Botón "Pago Múltiple" en la barra de herramientas
- Filtrado por tipo de factura (compra/venta)

### 2. Creación de Pago
- Formulario intuitivo con validaciones
- Información del proveedor/cliente
- Lista de facturas pendientes

### 3. Asignación de Facturas
- Tabla con checkboxes para selección
- Campos de monto editables
- Cálculo automático de totales
- Validaciones en tiempo real

### 4. Visualización
- Resumen financiero con barras de progreso
- Tabla detallada de asignaciones
- Acciones de gestión

## Beneficios del Sistema

### Para Proveedores:
- ✅ **Flexibilidad**: Pagos parciales a múltiples facturas
- ✅ **Eficiencia**: Un pago puede cubrir varias facturas
- ✅ **Control**: Seguimiento detallado de asignaciones

### Para Clientes:
- ✅ **Simplicidad**: Pago único para múltiples facturas
- ✅ **Claridad**: Distribución transparente de montos
- ✅ **Conveniencia**: Menos transacciones bancarias

### Para el Sistema:
- ✅ **Trazabilidad**: Historial completo de asignaciones
- ✅ **Integridad**: Validaciones robustas
- ✅ **Escalabilidad**: Fácil extensión para nuevas funcionalidades

## Casos de Uso Comunes

### 1. Pago de Proveedor con Múltiples Facturas
```
Situación: Proveedor envía un pago único por Gs. 3,000,000
Facturas pendientes:
- Factura #001: Gs. 1,200,000
- Factura #002: Gs. 800,000
- Factura #003: Gs. 1,000,000
Resultado: Las 3 facturas se marcan como pagadas
```

### 2. Pago de Cliente con Facturas Diferentes
```
Situación: Cliente paga Gs. 1,500,000 por varias facturas
Facturas asignadas:
- Factura #004: Gs. 900,000 (60%)
- Factura #005: Gs. 600,000 (40%)
Resultado: Cliente queda al día con sus obligaciones
```

### 3. Pago Parcial con Reasignación
```
Situación: Pago de Gs. 2,000,000 con asignación posterior
Primera asignación:
- Factura #006: Gs. 1,500,000
Segunda asignación:
- Factura #007: Gs. 500,000
Resultado: Pago completamente asignado
```

## Archivos Modificados

### Modelos:
- `facturacion/core/models.py`: Nuevos modelos y modificaciones

### Formularios:
- `facturacion/core/forms.py`: Nuevos formularios para pagos múltiples

### Vistas:
- `facturacion/core/views.py`: Nuevas vistas para gestión de pagos múltiples

### URLs:
- `facturacion/core/urls.py`: Nuevas rutas para pagos múltiples

### Plantillas:
- `facturacion/templates/pago_multiple_crear.html`: Creación de pagos
- `facturacion/templates/pago_asignar_facturas.html`: Asignación de facturas
- `facturacion/templates/pago_ver.html`: Visualización de pagos
- `facturacion/templates/pago_confirm_delete.html`: Confirmación de eliminación
- `facturacion/templates/asignacion_confirm_delete.html`: Eliminación de asignaciones
- `facturacion/templates/factura_list.html`: Botón de pago múltiple

### Admin:
- `facturacion/core/admin.py`: Configuración para nuevos modelos

## Migraciones

### Archivo: `core/migrations/0006_remove_pago_factura_remove_pago_monto_and_more.py`
- Elimina campos `factura` y `monto` del modelo `Pago`
- Agrega campos `monto_total` y `observacion` al modelo `Pago`
- Crea el nuevo modelo `PagoFactura`

## Consideraciones Técnicas

### 1. Integridad de Datos
- Todas las operaciones son transaccionales
- Los saldos se actualizan automáticamente
- Validaciones en múltiples niveles

### 2. Rendimiento
- Consultas optimizadas con `select_related`
- Cálculos en memoria cuando es posible
- Paginación para grandes volúmenes

### 3. Seguridad
- Validaciones en frontend y backend
- Confirmaciones para operaciones críticas
- Registro de usuario en todas las operaciones

## Próximas Mejoras

### 1. Reportes Avanzados
- Reporte de pagos múltiples por período
- Análisis de distribución de pagos
- Exportación a Excel

### 2. Notificaciones
- Alertas de pagos parciales
- Notificaciones de facturas pagadas
- Recordatorios de pagos pendientes

### 3. Integración Bancaria
- Conciliación automática con extractos
- Importación de pagos desde archivos
- Validación de referencias bancarias 