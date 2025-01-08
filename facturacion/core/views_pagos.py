from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Pago, Factura, Caja


@login_required
def pagos_dashboard(request):
    """Dashboard principal del módulo de pagos"""
    # Facturas pendientes
    facturas_pendientes_clientes = Factura.objects.filter(
        tipo='venta', 
        estado='pendiente'
    ).select_related('cliente').order_by('-fecha')[:5]
    
    facturas_pendientes_proveedores = Factura.objects.filter(
        tipo='compra', 
        estado='pendiente'
    ).select_related('proveedor').order_by('-fecha')[:5]
    
    # Caja activa
    caja_activa = Caja.obtener_caja_activa()
    
    context = {
        'facturas_pendientes_clientes': facturas_pendientes_clientes,
        'facturas_pendientes_proveedores': facturas_pendientes_proveedores,
        'caja_activa': caja_activa,
    }
    
    return render(request, 'pagos_dashboard.html', context)


@login_required
def pagos_clientes_list(request):
    """Lista de pagos de clientes (facturas de venta)"""
    # Obtener facturas de venta con pagos
    facturas_venta = Factura.objects.filter(
        tipo='venta'
    ).select_related('cliente').prefetch_related('pagos_facturas').order_by('-fecha')
    
    # Filtros
    q = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    desde = request.GET.get('desde', '')
    hasta = request.GET.get('hasta', '')
    
    if q:
        facturas_venta = facturas_venta.filter(
            Q(cliente__nombre__icontains=q) | 
            Q(numero__icontains=q) |
            Q(cliente__ruc__icontains=q)
        )
    
    if estado:
        facturas_venta = facturas_venta.filter(estado=estado)
    
    if desde:
        facturas_venta = facturas_venta.filter(fecha__date__gte=desde)
    
    if hasta:
        facturas_venta = facturas_venta.filter(fecha__date__lte=hasta)
    
    # Paginación
    paginator = Paginator(facturas_venta, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'facturas': page_obj,
        'tipo': 'venta',
        'titulo': 'Pagos de Clientes',
        'subtitulo': 'Facturas de Venta - Gestión de Cobros',
    }
    
    return render(request, 'pagos_list.html', context)


@login_required
def pagos_proveedores_list(request):
    """Lista de pagos a proveedores (facturas de compra)"""
    # Obtener facturas de compra con pagos
    facturas_compra = Factura.objects.filter(
        tipo='compra'
    ).select_related('proveedor').prefetch_related('pagos_facturas').order_by('-fecha')
    
    # Filtros
    q = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    desde = request.GET.get('desde', '')
    hasta = request.GET.get('hasta', '')
    
    if q:
        facturas_compra = facturas_compra.filter(
            Q(proveedor__nombre__icontains=q) | 
            Q(numero__icontains=q) |
            Q(proveedor__ruc__icontains=q)
        )
    
    if estado:
        facturas_compra = facturas_compra.filter(estado=estado)
    
    if desde:
        facturas_compra = facturas_compra.filter(fecha__date__gte=desde)
    
    if hasta:
        facturas_compra = facturas_compra.filter(fecha__date__lte=hasta)
    
    # Paginación
    paginator = Paginator(facturas_compra, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'facturas': page_obj,
        'tipo': 'compra',
        'titulo': 'Pagos a Proveedores',
        'subtitulo': 'Facturas de Compra - Gestión de Pagos',
    }
    
    return render(request, 'pagos_list.html', context)
