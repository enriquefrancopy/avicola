from django import forms
from .models import Producto, Proveedor, Cliente, Factura, DetalleFactura, Pago, PagoFactura

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'costo', 'precio', 'stock_minimo', 'iva', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código único del producto'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'costo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'iva': forms.Select(choices=[(5, '5%'), (10, '10%')], attrs={'class': 'form-select'}),
        }
    
    def clean_iva(self):
        iva = self.cleaned_data.get('iva')
        if iva not in [5, 10]:
            raise forms.ValidationError('El IVA debe ser 5% o 10%')
        return int(iva)
    
    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if codigo:
            # Verificar duplicados solo si no es una edición del mismo producto
            if self.instance and self.instance.pk:
                # Es una edición, excluir el producto actual
                if Producto.objects.filter(codigo=codigo).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError('Ya existe un producto con este código')
            else:
                # Es una creación nueva
                if Producto.objects.filter(codigo=codigo).exists():
                    raise forms.ValidationError('Ya existe un producto con este código')
        return codigo
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre or nombre.strip() == '':
            raise forms.ValidationError('El nombre del producto es requerido')
        return nombre.strip()
    
    def clean_costo(self):
        costo = self.cleaned_data.get('costo')
        if costo is None or costo == '':
            return 0
        return int(costo)
    
    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is None or precio == '':
            raise forms.ValidationError('El precio es requerido')
        return int(precio)
    

    
    def clean_stock_minimo(self):
        stock_minimo = self.cleaned_data.get('stock_minimo')
        if stock_minimo is None or stock_minimo == '':
            return 10
        return int(stock_minimo)

class ProductoCrearForm(forms.ModelForm):
    """Formulario específico para crear productos con stock inicial"""
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'costo', 'precio', 'stock', 'stock_minimo', 'iva', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código único del producto'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'costo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'iva': forms.Select(choices=[(5, '5%'), (10, '10%')], attrs={'class': 'form-select'}),
        }
    
    def clean_iva(self):
        iva = self.cleaned_data.get('iva')
        if iva not in [5, 10]:
            raise forms.ValidationError('El IVA debe ser 5% o 10%')
        return int(iva)
    
    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if codigo:
            if Producto.objects.filter(codigo=codigo).exists():
                raise forms.ValidationError('Ya existe un producto con este código')
        return codigo
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre or nombre.strip() == '':
            raise forms.ValidationError('El nombre del producto es requerido')
        return nombre.strip()
    
    def clean_costo(self):
        costo = self.cleaned_data.get('costo')
        if costo is None or costo == '':
            return 0
        return int(costo)
    
    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is None or precio == '':
            raise forms.ValidationError('El precio es requerido')
        return int(precio)
    
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is None or stock == '':
            return 0
        return int(stock)
    
    def clean_stock_minimo(self):
        stock_minimo = self.cleaned_data.get('stock_minimo')
        if stock_minimo is None or stock_minimo == '':
            return 10
        return int(stock_minimo)

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'rif', 'direccion', 'telefono', 'email', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del proveedor'}),
            'rif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RUC del proveedor'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre or nombre.strip() == '':
            raise forms.ValidationError('El nombre del proveedor es requerido')
        return nombre.strip()
    
    def clean_rif(self):
        rif = self.cleaned_data.get('rif')
        if not rif or rif.strip() == '':
            raise forms.ValidationError('El RUC es requerido')
        
        # Verificar duplicados solo si no es una edición del mismo proveedor
        if self.instance and self.instance.pk:
            # Es una edición, excluir el proveedor actual
            if Proveedor.objects.filter(rif=rif).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Ya existe un proveedor con este RUC')
        else:
            # Es una creación nueva
            if Proveedor.objects.filter(rif=rif).exists():
                raise forms.ValidationError('Ya existe un proveedor con este RUC')
        
        return rif.strip()
    
    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')
        if not direccion or direccion.strip() == '':
            raise forms.ValidationError('La dirección es requerida')
        return direccion.strip()
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono or telefono.strip() == '':
            raise forms.ValidationError('El teléfono es requerido')
        return telefono.strip()
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email or email.strip() == '':
            raise forms.ValidationError('El email es requerido')
        return email.strip()

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'rif', 'direccion', 'telefono', 'email', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente'}),
            'rif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RUC del cliente'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre or nombre.strip() == '':
            raise forms.ValidationError('El nombre del cliente es requerido')
        return nombre.strip()
    
    def clean_rif(self):
        rif = self.cleaned_data.get('rif')
        if not rif or rif.strip() == '':
            raise forms.ValidationError('El RUC es requerido')
        
        # Verificar duplicados solo si no es una edición del mismo cliente
        if self.instance and self.instance.pk:
            # Es una edición, excluir el cliente actual
            if Cliente.objects.filter(rif=rif).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Ya existe un cliente con este RUC')
        else:
            # Es una creación nueva
            if Cliente.objects.filter(rif=rif).exists():
                raise forms.ValidationError('Ya existe un cliente con este RUC')
        
        return rif.strip()
    
    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')
        if not direccion or direccion.strip() == '':
            raise forms.ValidationError('La dirección es requerida')
        return direccion.strip()
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono or telefono.strip() == '':
            raise forms.ValidationError('El teléfono es requerido')
        return telefono.strip()
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email or email.strip() == '':
            raise forms.ValidationError('El email es requerido')
        return email.strip()

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['tipo', 'numero', 'fecha', 'proveedor', 'cliente', 'observacion']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'observacion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar proveedores y clientes activos
        self.fields['proveedor'].queryset = Proveedor.objects.filter(activo=True)
        self.fields['cliente'].queryset = Cliente.objects.filter(activo=True)
        
        # Hacer el campo número readonly
        self.fields['numero'].widget.attrs['readonly'] = 'readonly'
    
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        proveedor = cleaned_data.get('proveedor')
        cliente = cleaned_data.get('cliente')
        
        if tipo == 'compra' and not proveedor:
            raise forms.ValidationError('Para facturas de compra debe seleccionar un proveedor')
        
        if tipo == 'venta' and not cliente:
            raise forms.ValidationError('Para facturas de venta debe seleccionar un cliente')
        
        return cleaned_data

DetalleFacturaFormSet = forms.inlineformset_factory(
    Factura,
    DetalleFactura,
    fields=['producto', 'cantidad', 'precio_unitario'],
    extra=1,
    can_delete=True
)

class PagoForm(forms.ModelForm):
    # Campo adicional para el monto del billete (solo para clientes)
    monto_billete = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'placeholder': 'Monto del billete recibido'
        }),
        help_text='Ingrese el monto del billete para calcular el vuelto'
    )
    
    class Meta:
        model = Pago
        fields = ['monto_total', 'tipo', 'referencia', 'observacion']
        widgets = {
            'monto_total': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'referencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de transferencia, cheque, etc.'}),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones adicionales del pago'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.factura = kwargs.pop('factura', None)
        super().__init__(*args, **kwargs)
        
        if self.factura:
            # Configurar el monto máximo según el tipo de factura
            if self.factura.tipo == 'compra':
                # Para proveedores: pagos parciales permitidos
                self.fields['monto_total'].widget.attrs.update({
                    'max': self.factura.saldo_pendiente,
                    'placeholder': f'Máximo: Gs. {self.factura.saldo_pendiente:,}'
                })
                self.fields['monto_total'].help_text = f'Pago parcial permitido. Saldo pendiente: Gs. {self.factura.saldo_pendiente:,}'
                
                # Ocultar campo de monto del billete para proveedores
                self.fields['monto_billete'].widget = forms.HiddenInput()
                self.fields['monto_billete'].required = False
            else:
                # Para clientes: solo pagos completos
                self.fields['monto_total'].widget.attrs.update({
                    'value': self.factura.total,
                    'readonly': 'readonly'
                })
                self.fields['monto_total'].help_text = 'Pago completo requerido para clientes'
                
                # Preseleccionar tipo como efectivo para clientes
                self.fields['tipo'].initial = 'efectivo'
                
                # Mostrar campo de monto del billete para clientes
                self.fields['monto_billete'].required = True
                self.fields['monto_billete'].widget.attrs.update({
                    'min': self.factura.total,
                    'placeholder': f'Mínimo: Gs. {self.factura.total:,}'
                })
                self.fields['monto_billete'].help_text = f'Ingrese el monto del billete (mínimo: Gs. {self.factura.total:,})'
    
    def clean_monto_total(self):
        monto = self.cleaned_data.get('monto_total')
        if not monto or monto <= 0:
            raise forms.ValidationError('El monto debe ser mayor a 0')
        
        if self.factura:
            if self.factura.tipo == 'compra':
                # Para proveedores: validar contra saldo pendiente
                if not self.factura.validar_monto_pago(monto):
                    raise forms.ValidationError(f'El monto debe ser menor o igual al saldo pendiente (Gs. {self.factura.saldo_pendiente:,})')
            else:
                # Para clientes: validar contra total de la factura
                if monto != self.factura.total:
                    raise forms.ValidationError(f'Para clientes solo se permiten pagos completos. Monto requerido: Gs. {self.factura.total:,}')
        
        return monto
    
    def clean_monto_billete(self):
        monto_billete = self.cleaned_data.get('monto_billete')
        monto_total = self.cleaned_data.get('monto_total')
        
        # Solo validar para facturas de venta (clientes)
        if self.factura and self.factura.tipo == 'venta':
            if not monto_billete:
                raise forms.ValidationError('Debe ingresar el monto del billete para calcular el vuelto')
            
            # Validar que monto_total no sea None antes de comparar
            if monto_total is not None and monto_billete < monto_total:
                raise forms.ValidationError(f'El monto del billete debe ser mayor o igual al monto a pagar (Gs. {monto_total:,})')
        
        return monto_billete
    
    def clean(self):
        cleaned_data = super().clean()
        monto_billete = cleaned_data.get('monto_billete')
        monto_total = cleaned_data.get('monto_total')
        
        # Calcular vuelto para facturas de venta
        if (self.factura and self.factura.tipo == 'venta' and 
            monto_billete is not None and monto_total is not None):
            vuelto = monto_billete - monto_total
            cleaned_data['vuelto'] = vuelto
        
        return cleaned_data

class PagoMultipleForm(forms.ModelForm):
    """Formulario para crear un pago que puede asignarse a múltiples facturas"""
    class Meta:
        model = Pago
        fields = ['monto_total', 'tipo', 'referencia']
        widgets = {
            'monto_total': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'referencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de transferencia, cheque, etc.'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.proveedor = kwargs.pop('proveedor', None)
        self.factura_especifica = kwargs.pop('factura_especifica', None)
        super().__init__(*args, **kwargs)
        
        # Siempre predeterminar tipo como efectivo
        self.fields['tipo'].initial = 'efectivo'
        
        # Si hay una factura específica, configurar para esa factura
        if self.factura_especifica:
            saldo_pendiente = self.factura_especifica.saldo_pendiente
            
            self.fields['monto_total'].widget.attrs.update({
                'placeholder': f'Máximo: Gs. {saldo_pendiente:,}',
                'max': saldo_pendiente
            })
            self.fields['monto_total'].help_text = f'Saldo pendiente de la factura: Gs. {saldo_pendiente:,}'
            
        elif self.proveedor:
            # Calcular total pendiente del proveedor
            facturas_pendientes = Factura.objects.filter(
                tipo='compra', 
                proveedor=self.proveedor, 
                estado='pendiente'
            )
            total_pendiente = sum(factura.saldo_pendiente for factura in facturas_pendientes)
            
            self.fields['monto_total'].widget.attrs.update({
                'placeholder': f'Máximo: Gs. {total_pendiente:,}',
                'max': total_pendiente
            })
            self.fields['monto_total'].help_text = f'Total pendiente del proveedor: Gs. {total_pendiente:,}'
    
    def clean_monto_total(self):
        monto = self.cleaned_data.get('monto_total')
        if not monto or monto <= 0:
            raise forms.ValidationError('El monto debe ser mayor a 0')
        
        # Si hay una factura específica, validar contra su saldo pendiente
        if self.factura_especifica:
            saldo_pendiente = self.factura_especifica.saldo_pendiente
            if monto > saldo_pendiente:
                raise forms.ValidationError(f'El monto excede el saldo pendiente de la factura (Gs. {saldo_pendiente:,})')
        
        # Validar contra el total pendiente del proveedor
        elif self.proveedor:
            facturas_pendientes = Factura.objects.filter(
                tipo='compra', 
                proveedor=self.proveedor, 
                estado='pendiente'
            )
            total_pendiente = sum(factura.saldo_pendiente for factura in facturas_pendientes)
            if monto > total_pendiente:
                raise forms.ValidationError(f'El monto excede el total pendiente del proveedor (Gs. {total_pendiente:,})')
        
        return monto

class AsignacionPagoForm(forms.ModelForm):
    """Formulario para asignar montos de un pago a facturas específicas"""
    class Meta:
        model = PagoFactura
        fields = ['factura', 'monto']
        widgets = {
            'factura': forms.Select(attrs={'class': 'form-select'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.pago = kwargs.pop('pago', None)
        self.proveedor = kwargs.pop('proveedor', None)
        self.cliente = kwargs.pop('cliente', None)
        super().__init__(*args, **kwargs)
        
        if self.pago:
            # Filtrar facturas pendientes según el tipo
            if self.proveedor:
                self.fields['factura'].queryset = Factura.objects.filter(
                    tipo='compra',
                    proveedor=self.proveedor,
                    estado='pendiente'
                ).order_by('fecha')
            elif self.cliente:
                self.fields['factura'].queryset = Factura.objects.filter(
                    tipo='venta',
                    cliente=self.cliente,
                    estado='pendiente'
                ).order_by('fecha')
            
            # Configurar monto máximo
            self.fields['monto'].widget.attrs.update({
                'max': self.pago.monto_disponible,
                'placeholder': f'Máximo: Gs. {self.pago.monto_disponible:,}'
            })
            self.fields['monto'].help_text = f'Monto disponible: Gs. {self.pago.monto_disponible:,}'
    
    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        factura = self.cleaned_data.get('factura')
        
        if not monto or monto <= 0:
            raise forms.ValidationError('El monto debe ser mayor a 0')
        
        if self.pago and monto > self.pago.monto_disponible:
            raise forms.ValidationError(f'El monto excede el disponible del pago (Gs. {self.pago.monto_disponible:,})')
        
        if factura and monto > factura.saldo_pendiente:
            raise forms.ValidationError(f'El monto excede el saldo pendiente de la factura (Gs. {factura.saldo_pendiente:,})')
        
        return monto

class PagoFacturaFormSet(forms.BaseModelFormSet):
    """FormSet para manejar múltiples asignaciones de pagos a facturas"""
    
    def __init__(self, *args, **kwargs):
        self.pago = kwargs.pop('pago', None)
        super().__init__(*args, **kwargs)
        
        if self.pago:
            for form in self.forms:
                form.fields['monto'].widget.attrs.update({
                    'max': self.pago.monto_disponible,
                    'placeholder': f'Máximo: Gs. {self.pago.monto_disponible:,}'
                })
    
    def clean(self):
        super().clean()
        
        if not self.pago:
            return
        
        total_asignado = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                monto = form.cleaned_data.get('monto', 0)
                total_asignado += monto
        
        if total_asignado > self.pago.monto_total:
            raise forms.ValidationError(
                f'El total asignado (Gs. {total_asignado:,}) excede el monto del pago (Gs. {self.pago.monto_total:,})'
            )
