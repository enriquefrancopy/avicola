from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Q, F
from .models import Pago, Gasto, Factura, Producto, Cliente, Proveedor
from datetime import datetime, timedelta
from django.http import HttpResponse
import xlsxwriter
import io


@login_required
def reporte_flujo_caja(request):
    """Reporte de flujo de caja"""
    
    # Parámetros de filtro
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Fechas por defecto (último mes)
    hoy = datetime.now().date()
    if not fecha_inicio:
        fecha_inicio = (hoy - timedelta(days=30)).strftime('%Y-%m-%d')
    if not fecha_fin:
        fecha_fin = hoy.strftime('%Y-%m-%d')
    
    try:
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    except ValueError:
        fecha_inicio_dt = (hoy - timedelta(days=30)).date()
        fecha_fin_dt = hoy
    
    # Ingresos (ventas pagadas)
    ingresos = Factura.objects.filter(
        tipo='venta',
        estado='pagada',
        fecha__date__gte=fecha_inicio_dt,
        fecha__date__lte=fecha_fin_dt
    ).aggregate(
        total=Sum('total'),
        cantidad=Count('id')
    )
    
    # Egresos (pagos a proveedores)
    egresos_proveedores = Pago.objects.filter(
        proveedor__isnull=False,
        fecha__date__gte=fecha_inicio_dt,
        fecha__date__lte=fecha_fin_dt
    ).aggregate(
        total=Sum('monto_total'),
        cantidad=Count('id')
    )
    
    # Gastos
    gastos = Gasto.objects.filter(
        fecha__date__gte=fecha_inicio_dt,
        fecha__date__lte=fecha_fin_dt
    ).aggregate(
        total=Sum('monto'),
        cantidad=Count('id')
    )
    
    # Flujo neto
    total_ingresos = ingresos['total'] or 0
    total_egresos = (egresos_proveedores['total'] or 0) + (gastos['total'] or 0)
    flujo_neto = total_ingresos - total_egresos
    
    # Detalle diario
    detalle_diario = []
    fecha_actual = fecha_inicio_dt
    
    while fecha_actual <= fecha_fin_dt:
        # Ingresos del día
        ingresos_dia = Factura.objects.filter(
            tipo='venta',
            estado='pagada',
            fecha__date=fecha_actual
        ).aggregate(
            total=Sum('total'),
            cantidad=Count('id')
        )
        
        # Egresos del día
        egresos_dia = Pago.objects.filter(
            proveedor__isnull=False,
            fecha__date=fecha_actual
        ).aggregate(
            total=Sum('monto_total')
        )
        
        # Gastos del día
        gastos_dia = Gasto.objects.filter(
            fecha__date=fecha_actual
        ).aggregate(
            total=Sum('monto')
        )
        
        total_ingresos_dia = ingresos_dia['total'] or 0
        total_egresos_dia = (egresos_dia['total'] or 0) + (gastos_dia['total'] or 0)
        flujo_dia = total_ingresos_dia - total_egresos_dia
        
        detalle_diario.append({
            'fecha': fecha_actual,
            'ingresos': total_ingresos_dia,
            'egresos': total_egresos_dia,
            'flujo_neto': flujo_dia,
            'cantidad_ingresos': ingresos_dia['cantidad'] or 0
        })
        
        fecha_actual += timedelta(days=1)
    
    # Top 5 días con más ingresos
    dias_mas_ingresos = sorted(detalle_diario, key=lambda x: x['ingresos'], reverse=True)[:5]
    
    # Top 5 días con más egresos
    dias_mas_egresos = sorted(detalle_diario, key=lambda x: x['egresos'], reverse=True)[:5]
    
    # Análisis por categoría de gastos
    gastos_por_categoria = Gasto.objects.filter(
        fecha__date__gte=fecha_inicio_dt,
        fecha__date__lte=fecha_fin_dt
    ).values('categoria').annotate(
        total=Sum('monto'),
        cantidad=Count('id')
    ).order_by('-total')
    
    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'flujo_neto': flujo_neto,
        'cantidad_ingresos': ingresos['cantidad'] or 0,
        'cantidad_egresos': (egresos_proveedores['cantidad'] or 0) + (gastos['cantidad'] or 0),
        'detalle_diario': detalle_diario,
        'dias_mas_ingresos': dias_mas_ingresos,
        'dias_mas_egresos': dias_mas_egresos,
        'gastos_por_categoria': gastos_por_categoria,
        'titulo': 'Reporte de Flujo de Caja'
    }
    
    return render(request, 'reporte_flujo_caja.html', context)


@login_required
def exportar_flujo_caja_excel(request):
    """Exportar reporte de flujo de caja a Excel"""
    
    # Parámetros de filtro
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Fechas por defecto (último mes)
    hoy = datetime.now().date()
    if not fecha_inicio:
        fecha_inicio = (hoy - timedelta(days=30)).strftime('%Y-%m-%d')
    if not fecha_fin:
        fecha_fin = hoy.strftime('%Y-%m-%d')
    
    try:
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    except ValueError:
        fecha_inicio_dt = (hoy - timedelta(days=30)).date()
        fecha_fin_dt = hoy
    
    # Crear archivo Excel
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    # Formato para moneda
    formato_moneda = workbook.add_format({'num_format': '#,##0'})
    formato_fecha = workbook.add_format({'num_format': 'dd/mm/yyyy'})
    formato_titulo = workbook.add_format({'bold': True, 'font_size': 14})
    formato_subtitulo = workbook.add_format({'bold': True, 'font_size': 12})
    
    # Hoja 1: Resumen
    worksheet1 = workbook.add_worksheet('Resumen')
    
    # Título
    worksheet1.write('A1', 'REPORTE DE FLUJO DE CAJA', formato_titulo)
    worksheet1.write('A2', f'Período: {fecha_inicio} al {fecha_fin}', formato_subtitulo)
    
    # Datos del resumen
    ingresos = Factura.objects.filter(
        tipo='venta',
        estado='pagada',
        fecha__date__gte=fecha_inicio_dt,
        fecha__date__lte=fecha_fin_dt
    ).aggregate(total=Sum('total'))
    
    egresos_proveedores = Pago.objects.filter(
        proveedor__isnull=False,
        fecha__date__gte=fecha_inicio_dt,
        fecha__date__lte=fecha_fin_dt
    ).aggregate(total=Sum('monto_total'))
    
    gastos = Gasto.objects.filter(
        fecha__date__gte=fecha_inicio_dt,
        fecha__date__lte=fecha_fin_dt
    ).aggregate(total=Sum('monto'))
    
    total_ingresos = ingresos['total'] or 0
    total_egresos = (egresos_proveedores['total'] or 0) + (gastos['total'] or 0)
    flujo_neto = total_ingresos - total_egresos
    
    worksheet1.write('A4', 'Concepto', formato_subtitulo)
    worksheet1.write('B4', 'Monto', formato_subtitulo)
    
    worksheet1.write('A5', 'Total Ingresos')
    worksheet1.write('B5', total_ingresos, formato_moneda)
    worksheet1.write('A6', 'Total Egresos')
    worksheet1.write('B6', total_egresos, formato_moneda)
    worksheet1.write('A7', 'Flujo Neto')
    worksheet1.write('B7', flujo_neto, formato_moneda)
    
    # Hoja 2: Detalle Diario
    worksheet2 = workbook.add_worksheet('Detalle Diario')
    
    # Encabezados
    worksheet2.write('A1', 'Fecha', formato_subtitulo)
    worksheet2.write('B1', 'Ingresos', formato_subtitulo)
    worksheet2.write('C1', 'Egresos', formato_subtitulo)
    worksheet2.write('D1', 'Flujo Neto', formato_subtitulo)
    
    # Datos diarios
    fecha_actual = fecha_inicio_dt
    fila = 2
    
    while fecha_actual <= fecha_fin_dt:
        ingresos_dia = Factura.objects.filter(
            tipo='venta',
            estado='pagada',
            fecha__date=fecha_actual
        ).aggregate(total=Sum('total'))
        
        egresos_dia = Pago.objects.filter(
            proveedor__isnull=False,
            fecha__date=fecha_actual
        ).aggregate(total=Sum('monto_total'))
        
        gastos_dia = Gasto.objects.filter(
            fecha__date=fecha_actual
        ).aggregate(total=Sum('monto'))
        
        total_ingresos_dia = ingresos_dia['total'] or 0
        total_egresos_dia = (egresos_dia['total'] or 0) + (gastos_dia['total'] or 0)
        flujo_dia = total_ingresos_dia - total_egresos_dia
        
        worksheet2.write(fila, 0, fecha_actual, formato_fecha)
        worksheet2.write(fila, 1, total_ingresos_dia, formato_moneda)
        worksheet2.write(fila, 2, total_egresos_dia, formato_moneda)
        worksheet2.write(fila, 3, flujo_dia, formato_moneda)
        
        fecha_actual += timedelta(days=1)
        fila += 1
    
    workbook.close()
    output.seek(0)
    
    # Crear respuesta HTTP
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="flujo_caja_{fecha_inicio}_{fecha_fin}.xlsx"'
    
    return response


@login_required
def reporte_rentabilidad_productos(request):
    """Reporte de rentabilidad por productos"""
    
    # Parámetros de filtro
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Fechas por defecto (último mes)
    hoy = datetime.now().date()
    if not fecha_inicio:
        fecha_inicio = (hoy - timedelta(days=30)).strftime('%Y-%m-%d')
    if not fecha_fin:
        fecha_fin = hoy.strftime('%Y-%m-%d')
    
    try:
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    except ValueError:
        fecha_inicio_dt = (hoy - timedelta(days=30)).date()
        fecha_fin_dt = hoy
    
    # Obtener productos con sus ventas y rentabilidad
    productos_rentabilidad = []
    
    for producto in Producto.objects.all():
        # Ventas del producto en el período
        ventas_producto = Factura.objects.filter(
            tipo='venta',
            estado='pagada',
            fecha__date__gte=fecha_inicio_dt,
            fecha__date__lte=fecha_fin_dt,
            detalles__producto=producto
        ).aggregate(
            total_ventas=Sum('detalles__subtotal'),
            cantidad_vendida=Sum('detalles__cantidad'),
            cantidad_facturas=Count('id', distinct=True)
        )
        
        total_ventas = ventas_producto['total_ventas'] or 0
        cantidad_vendida = ventas_producto['cantidad_vendida'] or 0
        cantidad_facturas = ventas_producto['cantidad_facturas'] or 0
        
        # Calcular rentabilidad (precio_venta - costo)
        if cantidad_vendida > 0:
            precio_promedio_venta = total_ventas / cantidad_vendida
            margen_bruto = precio_promedio_venta - producto.costo
            porcentaje_rentabilidad = (margen_bruto / precio_promedio_venta) * 100 if precio_promedio_venta > 0 else 0
        else:
            margen_bruto = 0
            porcentaje_rentabilidad = 0
        
        productos_rentabilidad.append({
            'producto': producto,
            'total_ventas': total_ventas,
            'cantidad_vendida': cantidad_vendida,
            'cantidad_facturas': cantidad_facturas,
            'precio_promedio_venta': total_ventas / cantidad_vendida if cantidad_vendida > 0 else 0,
            'margen_bruto': margen_bruto,
            'porcentaje_rentabilidad': porcentaje_rentabilidad
        })
    
    # Ordenar por rentabilidad
    productos_rentabilidad.sort(key=lambda x: x['porcentaje_rentabilidad'], reverse=True)
    
    # Top 10 productos más rentables
    top_rentables = productos_rentabilidad[:10]
    
    # Productos con menor rentabilidad
    menos_rentables = [p for p in productos_rentabilidad if p['cantidad_vendida'] > 0][-10:]
    
    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'productos_rentabilidad': productos_rentabilidad,
        'top_rentables': top_rentables,
        'menos_rentables': menos_rentables,
        'titulo': 'Reporte de Rentabilidad por Productos'
    }
    
    return render(request, 'reporte_rentabilidad_productos.html', context)


@login_required
def reporte_tendencias_ventas(request):
    """Reporte de tendencias de ventas"""
    
    # Parámetros de filtro
    periodo = request.GET.get('periodo', '30')  # días
    tipo_analisis = request.GET.get('tipo_analisis', 'diario')  # diario, semanal, mensual
    
    try:
        periodo = int(periodo)
    except ValueError:
        periodo = 30
    
    # Fechas
    fecha_fin = datetime.now().date()
    fecha_inicio = fecha_fin - timedelta(days=periodo)
    
    # Datos para gráficos
    tendencias = []
    fecha_actual = fecha_inicio
    
    while fecha_actual <= fecha_fin:
        # Ventas del día
        ventas_dia = Factura.objects.filter(
            tipo='venta',
            estado='pagada',
            fecha__date=fecha_actual
        ).aggregate(
            total_ventas=Sum('total'),
            cantidad_facturas=Count('id')
        )
        
        # Productos más vendidos del día
        productos_dia = Factura.objects.filter(
            tipo='venta',
            estado='pagada',
            fecha__date=fecha_actual
        ).values('detalles__producto__nombre').annotate(
            cantidad=Sum('detalles__cantidad')
        ).order_by('-cantidad')[:5]
        
        tendencias.append({
            'fecha': fecha_actual,
            'total_ventas': ventas_dia['total_ventas'] or 0,
            'cantidad_facturas': ventas_dia['cantidad_facturas'] or 0,
            'productos_destacados': list(productos_dia)
        })
        
        fecha_actual += timedelta(days=1)
    
    # Estadísticas generales
    total_periodo = sum(t['total_ventas'] for t in tendencias)
    promedio_diario = total_periodo / len(tendencias) if tendencias else 0
    
    # Días con más ventas
    dias_mas_ventas = sorted(tendencias, key=lambda x: x['total_ventas'], reverse=True)[:5]
    
    # Días con menos ventas
    dias_menos_ventas = sorted(tendencias, key=lambda x: x['total_ventas'])[:5]
    
    # Productos más vendidos en el período
    productos_mas_vendidos = Factura.objects.filter(
        tipo='venta',
        estado='pagada',
        fecha__date__gte=fecha_inicio,
        fecha__date__lte=fecha_fin
    ).values('detalles__producto__nombre').annotate(
        cantidad_total=Sum('detalles__cantidad'),
        total_ventas=Sum('detalles__subtotal')
    ).order_by('-cantidad_total')[:10]
    
    context = {
        'periodo': periodo,
        'tipo_analisis': tipo_analisis,
        'tendencias': tendencias,
        'total_periodo': total_periodo,
        'promedio_diario': promedio_diario,
        'dias_mas_ventas': dias_mas_ventas,
        'dias_menos_ventas': dias_menos_ventas,
        'productos_mas_vendidos': productos_mas_vendidos,
        'titulo': 'Reporte de Tendencias de Ventas'
    }
    
    return render(request, 'reporte_tendencias_ventas.html', context)


@login_required
def reporte_analisis_clientes(request):
    """Reporte de análisis de clientes"""
    
    # Parámetros de filtro
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    tipo_cliente = request.GET.get('tipo_cliente', 'todos')  # todos, frecuentes, nuevos
    
    # Fechas por defecto (último mes)
    hoy = datetime.now().date()
    if not fecha_inicio:
        fecha_inicio = (hoy - timedelta(days=30)).strftime('%Y-%m-%d')
    if not fecha_fin:
        fecha_fin = hoy.strftime('%Y-%m-%d')
    
    try:
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    except ValueError:
        fecha_inicio_dt = (hoy - timedelta(days=30)).date()
        fecha_fin_dt = hoy
    
    # Análisis de clientes
    clientes_analisis = []
    
    for cliente in Cliente.objects.all():
        # Compras del cliente en el período
        compras_cliente = Factura.objects.filter(
            tipo='venta',
            cliente=cliente,
            fecha__date__gte=fecha_inicio_dt,
            fecha__date__lte=fecha_fin_dt
        ).aggregate(
            total_compras=Sum('total'),
            cantidad_facturas=Count('id'),
            promedio_compra=Avg('total')
        )
        
        # Pagos del cliente
        pagos_cliente = Pago.objects.filter(
            cliente=cliente,
            fecha__date__gte=fecha_inicio_dt,
            fecha__date__lte=fecha_fin_dt
        ).aggregate(
            total_pagado=Sum('monto_total')
        )
        
        total_compras = compras_cliente['total_compras'] or 0
        cantidad_facturas = compras_cliente['cantidad_facturas'] or 0
        promedio_compra = compras_cliente['promedio_compra'] or 0
        total_pagado = pagos_cliente['total_pagado'] or 0
        
        # Calcular saldo pendiente
        saldo_pendiente = total_compras - total_pagado
        
        # Frecuencia de compra (días entre compras)
        if cantidad_facturas > 1:
            primera_compra = Factura.objects.filter(
                tipo='venta',
                cliente=cliente,
                fecha__date__gte=fecha_inicio_dt,
                fecha__date__lte=fecha_fin_dt
            ).order_by('fecha').first()
            
            ultima_compra = Factura.objects.filter(
                tipo='venta',
                cliente=cliente,
                fecha__date__gte=fecha_inicio_dt,
                fecha__date__lte=fecha_fin_dt
            ).order_by('-fecha').first()
            
            if primera_compra and ultima_compra:
                dias_entre_compras = (ultima_compra.fecha - primera_compra.fecha).days
                frecuencia_compra = dias_entre_compras / (cantidad_facturas - 1) if cantidad_facturas > 1 else 0
            else:
                frecuencia_compra = 0
        else:
            frecuencia_compra = 0
        
        clientes_analisis.append({
            'cliente': cliente,
            'total_compras': total_compras,
            'cantidad_facturas': cantidad_facturas,
            'promedio_compra': promedio_compra,
            'total_pagado': total_pagado,
            'saldo_pendiente': saldo_pendiente,
            'frecuencia_compra': frecuencia_compra
        })
    
    # Filtrar por tipo de cliente
    if tipo_cliente == 'frecuentes':
        clientes_analisis = [c for c in clientes_analisis if c['cantidad_facturas'] >= 3]
    elif tipo_cliente == 'nuevos':
        clientes_analisis = [c for c in clientes_analisis if c['cantidad_facturas'] == 1]
    
    # Ordenar por total de compras
    clientes_analisis.sort(key=lambda x: x['total_compras'], reverse=True)
    
    # Top 10 clientes
    top_clientes = clientes_analisis[:10]
    
    # Clientes con saldo pendiente
    clientes_pendientes = [c for c in clientes_analisis if c['saldo_pendiente'] > 0]
    clientes_pendientes.sort(key=lambda x: x['saldo_pendiente'], reverse=True)
    
    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'tipo_cliente': tipo_cliente,
        'clientes_analisis': clientes_analisis,
        'top_clientes': top_clientes,
        'clientes_pendientes': clientes_pendientes,
        'titulo': 'Reporte de Análisis de Clientes'
    }
    
    return render(request, 'reporte_analisis_clientes.html', context)


@login_required
def reporte_eficiencia_operativa(request):
    """Reporte de eficiencia operativa"""
    
    # Parámetros de filtro
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Fechas por defecto (último mes)
    hoy = datetime.now().date()
    if not fecha_inicio:
        fecha_inicio = (hoy - timedelta(days=30)).strftime('%Y-%m-%d')
    if not fecha_fin:
        fecha_fin = hoy.strftime('%Y-%m-%d')
    
    try:
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    except ValueError:
        fecha_inicio_dt = (hoy - timedelta(days=30)).date()
        fecha_fin_dt = hoy
    
    # Métricas de eficiencia
    
    # 1. Rotación de inventario
    productos_rotacion = []
    for producto in Producto.objects.all():
        # Ventas del período
        ventas_periodo = Factura.objects.filter(
            tipo='venta',
            estado='pagada',
            fecha__date__gte=fecha_inicio_dt,
            fecha__date__lte=fecha_fin_dt,
            detalles__producto=producto
        ).aggregate(
            cantidad_vendida=Sum('detalles__cantidad')
        )['cantidad_vendida'] or 0
        
        # Stock promedio (simplificado como stock actual)
        stock_promedio = producto.stock
        
        # Rotación = ventas / stock promedio
        rotacion = ventas_periodo / stock_promedio if stock_promedio > 0 else 0
        
        productos_rotacion.append({
            'producto': producto,
            'ventas_periodo': ventas_periodo,
            'stock_promedio': stock_promedio,
            'rotacion': rotacion
        })
    
    # Ordenar por rotación
    productos_rotacion.sort(key=lambda x: x['rotacion'], reverse=True)
    
    # 2. Eficiencia en cobranzas
    facturas_periodo = Factura.objects.filter(
        tipo='venta',
        fecha__date__gte=fecha_inicio_dt,
        fecha__date__lte=fecha_fin_dt
    )
    
    total_facturas = facturas_periodo.count()
    facturas_pagadas = facturas_periodo.filter(estado='pagada').count()
    facturas_pendientes = facturas_periodo.filter(estado='pendiente').count()
    
    eficiencia_cobranzas = (facturas_pagadas / total_facturas * 100) if total_facturas > 0 else 0
    
    # 3. Análisis de gastos por categoría
    gastos_categoria = Gasto.objects.filter(
        fecha__date__gte=fecha_inicio_dt,
        fecha__date__lte=fecha_fin_dt
    ).values('categoria').annotate(
        total=Sum('monto'),
        cantidad=Count('id')
    ).order_by('-total')
    
    # 4. Productos con stock bajo
    productos_stock_bajo = Producto.objects.filter(
        stock__lt=F('stock_minimo')
    ).exclude(stock=0)
    
    # 5. Productos agotados
    productos_agotados = Producto.objects.filter(stock=0)
    
    # 6. Tendencias de ventas por día de la semana
    ventas_por_dia = []
    for i in range(7):
        dia_semana = fecha_inicio_dt + timedelta(days=i)
        ventas_dia = Factura.objects.filter(
            tipo='venta',
            estado='pagada',
            fecha__date=dia_semana
        ).aggregate(
            total_ventas=Sum('total'),
            cantidad_facturas=Count('id')
        )
        
        ventas_por_dia.append({
            'dia': dia_semana.strftime('%A'),
            'total_ventas': ventas_dia['total_ventas'] or 0,
            'cantidad_facturas': ventas_dia['cantidad_facturas'] or 0
        })
    
    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'productos_rotacion': productos_rotacion,
        'eficiencia_cobranzas': eficiencia_cobranzas,
        'total_facturas': total_facturas,
        'facturas_pagadas': facturas_pagadas,
        'facturas_pendientes': facturas_pendientes,
        'gastos_categoria': gastos_categoria,
        'productos_stock_bajo': productos_stock_bajo,
        'productos_agotados': productos_agotados,
        'ventas_por_dia': ventas_por_dia,
        'titulo': 'Reporte de Eficiencia Operativa'
    }
    
    return render(request, 'reporte_eficiencia_operativa.html', context)
