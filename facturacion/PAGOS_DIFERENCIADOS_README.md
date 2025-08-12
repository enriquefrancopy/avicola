# Sistema de Pagos Diferenciados por Tipo de Factura

## Problema Identificado

El sistema de pagos no diferenciaba entre facturas de compra (proveedores) y facturas de venta (clientes), lo que causaba confusión en el manejo de pagos parciales y completos.

## Solución Implementada

Se ha implementado un sistema de pagos diferenciado que maneja de manera específica los pagos según el tipo de factura:

### **Para Facturas de Compra (Proveedores):**
- ✅ **Pagos parciales permitidos**
- ✅ **Múltiples pagos por factura**
- ✅ **Flexibilidad en montos**

### **Para Facturas de Venta (Clientes):**
- ✅ **Solo pagos completos**
- ✅ **Un pago por factura**
- ✅ **Monto fijo (saldo pendiente)**

## Cambios Implementados

### 1. Modelo Factura - Nuevos Métodos

**Archivo:** `facturacion/core/models.py`

**Métodos agregados:**
```python
@property
def total_pagado(self):
    """Calcula el total pagado de la factura"""
    return sum(pago.monto for pago in self.pagos.all())

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

def puede_pagar_parcialmente(self):
    """Determina si la factura permite pagos parciales"""
    return self.tipo == 'compra'

def validar_monto_pago(self, monto):
    """Valida si el monto del pago es válido según el tipo de factura"""
    if self.tipo == 'compra':
        # Para proveedores: pagos parciales permitidos
        return 0 < monto <= self.saldo_pendiente
    else:
        # Para clientes: solo pagos completos
        return monto == self.saldo_pendiente
```

### 2. Formulario de Pagos - Validaciones Inteligentes

**Archivo:** `facturacion/core/forms.py`

**Funcionalidades agregadas:**
```python
def __init__(self, *args, **kwargs):
    self.factura = kwargs.pop('factura', None)
    super().__init__(*args, **kwargs)
    
    if self.factura:
        if self.factura.tipo == 'compra':
            # Para proveedores: pagos parciales permitidos
            self.fields['monto'].widget.attrs.update({
                'max': self.factura.saldo_pendiente,
                'placeholder': f'Máximo: Gs. {self.factura.saldo_pendiente:,}'
            })
            self.fields['monto'].help_text = f'Pago parcial permitido. Saldo pendiente: Gs. {self.factura.saldo_pendiente:,}'
        else:
            # Para clientes: solo pagos completos
            self.fields['monto'].widget.attrs.update({
                'value': self.factura.saldo_pendiente,
                'readonly': 'readonly'
            })
            self.fields['monto'].help_text = 'Pago completo requerido para clientes'

def clean_monto(self):
    monto = self.cleaned_data.get('monto')
    if not monto or monto <= 0:
        raise forms.ValidationError('El monto debe ser mayor a 0')
    
    if self.factura:
        if not self.factura.validar_monto_pago(monto):
            if self.factura.tipo == 'compra':
                raise forms.ValidationError(f'El monto debe ser menor o igual al saldo pendiente (Gs. {self.factura.saldo_pendiente:,})')
            else:
                raise forms.ValidationError(f'Para clientes solo se permiten pagos completos. Monto requerido: Gs. {self.factura.saldo_pendiente:,}')
    
    return monto
```

### 3. Vistas de Pagos - Contexto de Factura

**Archivo:** `facturacion/core/views.py`

**Modificaciones:**
```python
# En factura_pagos() y pago_crear()
form = PagoForm(request.POST, factura=factura)  # POST
form = PagoForm(factura=factura)                # GET
```

### 4. Interfaz de Usuario - Información Contextual

**Archivo:** `facturacion/templates/factura_pagos.html`

**Mejoras visuales:**
- **Encabezado diferenciado:** Color y texto según tipo de factura
- **Alertas informativas:** Explican las reglas de pago
- **Campos adaptativos:** Monto editable para proveedores, fijo para clientes
- **Validaciones en tiempo real:** Mensajes de error específicos

## Flujo de Pagos por Tipo

### **Facturas de Compra (Proveedores):**

1. **Crear factura** → Saldo del proveedor aumenta
2. **Registrar pago parcial** → Saldo del proveedor disminuye
3. **Registrar más pagos** → Saldo sigue disminuyendo
4. **Factura pagada** → Saldo del proveedor = 0

**Ejemplo:**
- Factura: Gs. 1,000,000
- Pago 1: Gs. 300,000 (parcial)
- Pago 2: Gs. 400,000 (parcial)
- Pago 3: Gs. 300,000 (final)
- **Total pagado:** Gs. 1,000,000

### **Facturas de Venta (Clientes):**

1. **Crear factura** → Saldo del cliente aumenta
2. **Registrar pago completo** → Saldo del cliente disminuye a 0
3. **No más pagos** → Una sola transacción

**Ejemplo:**
- Factura: Gs. 500,000
- Pago único: Gs. 500,000 (completo)
- **Total pagado:** Gs. 500,000

## Beneficios del Sistema

### **Para Proveedores:**
- ✅ **Flexibilidad:** Pagos parciales según disponibilidad
- ✅ **Control:** Seguimiento de deudas pendientes
- ✅ **Historial:** Múltiples pagos por factura

### **Para Clientes:**
- ✅ **Simplicidad:** Un solo pago por factura
- ✅ **Claridad:** Sin confusión sobre montos
- ✅ **Eficiencia:** Proceso rápido y directo

### **Para el Sistema:**
- ✅ **Consistencia:** Reglas claras y aplicadas
- ✅ **Validación:** Prevención de errores
- ✅ **Trazabilidad:** Historial completo de pagos

## Casos de Uso

### **Escenario 1: Proveedor con Pagos Parciales**
```
Proveedor: "Distribuidora ABC"
Factura: Gs. 2,000,000
- Pago 1: Gs. 800,000 (40%)
- Pago 2: Gs. 600,000 (30%)
- Pago 3: Gs. 600,000 (30%)
Resultado: Factura completamente pagada
```

### **Escenario 2: Cliente con Pago Completo**
```
Cliente: "Restaurante XYZ"
Factura: Gs. 750,000
- Pago único: Gs. 750,000 (100%)
Resultado: Factura pagada inmediatamente
```

## Validaciones Implementadas

### **Para Proveedores:**
- ✅ Monto > 0
- ✅ Monto ≤ Saldo pendiente
- ✅ Múltiples pagos permitidos

### **Para Clientes:**
- ✅ Monto = Saldo pendiente (exacto)
- ✅ Un solo pago por factura
- ✅ Campo de monto bloqueado

## Archivos Modificados

- `facturacion/core/models.py`:
  - Agregados métodos de cálculo de saldos
  - Agregadas validaciones de pagos
- `facturacion/core/forms.py`:
  - Formulario PagoForm con validaciones inteligentes
  - Configuración dinámica según tipo de factura
- `facturacion/core/views.py`:
  - Vistas de pagos con contexto de factura
- `facturacion/templates/factura_pagos.html`:
  - Interfaz adaptativa según tipo de factura
  - Información contextual y validaciones visuales 