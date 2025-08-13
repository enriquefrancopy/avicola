from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import date
from .models import Caja, Denominacion, MovimientoCaja, Gasto

@login_required
def caja_abrir(request):
    """Abrir caja del día con denominaciones"""
    
    # Verificar si ya existe una caja para hoy
    caja_existente = Caja.objects.filter(fecha=date.today()).first()
    if caja_existente:
        messages.warning(request, 'Ya existe una caja abierta para hoy.')
        return redirect('caja_ver', caja_id=caja_existente.id)
    
    if request.method == 'POST':
        try:
            # Crear la caja
            caja = Caja.objects.create(
                fecha=date.today(),
                saldo_inicial=0,  # Se calculará automáticamente
                usuario_apertura=request.user
            )
            
            # Procesar denominaciones
            denominaciones_creadas = []
            total_calculado = 0
            
            for valor in Denominacion.VALOR_CHOICES:
                cantidad = request.POST.get(f'denominacion_{valor[0]}', 0)
                try:
                    cantidad = int(cantidad)
                    if cantidad > 0:
                        denominacion = Denominacion.objects.create(
                            caja=caja,
                            valor=valor[0],
                            cantidad=cantidad
                        )
                        denominaciones_creadas.append(denominacion)
                        total_calculado += valor[0] * cantidad
                except ValueError:
                    continue
            
            # Calcular saldo inicial basado en denominaciones
            caja.calcular_saldo_inicial_denominaciones()
            caja.save()
            
            messages.success(request, f'Caja abierta con saldo inicial de Gs. {caja.saldo_inicial:,}')
            return redirect('caja_ver', caja_id=caja.id)
            
        except Exception as e:
            messages.error(request, f'Error al abrir la caja: {str(e)}')
    
    # Obtener el último saldo de cierre
    ultimo_saldo = Caja.obtener_ultimo_saldo_cierre()
    
    # Preparar denominaciones para el formulario
    denominaciones = []
    for valor, label in Denominacion.VALOR_CHOICES:
        denominaciones.append({
            'valor': valor,
            'label': label,
            'cantidad': 0
        })
    
    context = {
        'fecha_actual': date.today(),
        'denominaciones': denominaciones,
        'ultimo_saldo': ultimo_saldo,
    }
    return render(request, 'caja_abrir.html', context)

@login_required
def caja_ver(request, caja_id):
    """Ver detalles de una caja"""
    caja = get_object_or_404(Caja, id=caja_id)
    
    # Obtener movimientos
    movimientos = caja.movimientos.select_related('usuario').order_by('-fecha')
    
    # Obtener gastos
    gastos = caja.gastos.select_related('usuario').order_by('-fecha')
    
    # Obtener denominaciones
    denominaciones = caja.denominaciones.all().order_by('-valor')
    
    # Calcular totales
    total_ingresos = movimientos.filter(tipo='ingreso').aggregate(total=Sum('monto'))['total'] or 0
    total_egresos = movimientos.filter(tipo='egreso').aggregate(total=Sum('monto'))['total'] or 0
    total_gastos = gastos.aggregate(total=Sum('monto'))['total'] or 0
    
    # Agrupar movimientos por categoría
    movimientos_por_categoria = movimientos.values('categoria').annotate(
        total=Sum('monto'),
        cantidad=Count('id')
    ).order_by('-total')
    
    context = {
        'caja': caja,
        'movimientos': movimientos,
        'gastos': gastos,
        'denominaciones': denominaciones,
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'total_gastos': total_gastos,
        'movimientos_por_categoria': movimientos_por_categoria,
    }
    
    return render(request, 'caja_ver.html', context)

@login_required
def caja_cerrar(request, caja_id):
    """Cerrar caja con arqueo"""
    caja = get_object_or_404(Caja, id=caja_id)
    
    if caja.cerrada:
        messages.warning(request, 'Esta caja ya está cerrada.')
        return redirect('caja_ver', caja_id=caja.id)
    
    if request.method == 'POST':
        saldo_real = request.POST.get('saldo_real', 0)
        observaciones = request.POST.get('observaciones', '')
        
        try:
            saldo_real = int(saldo_real)
            caja.cerrar_caja(saldo_real, request.user, observaciones)
            messages.success(request, 'Caja cerrada exitosamente.')
            return redirect('caja_ver', caja_id=caja.id)
        except ValueError:
            messages.error(request, 'El saldo real debe ser un número válido.')
    
    # Calcular saldo final esperado
    caja.calcular_saldo_final()
    
    context = {
        'caja': caja,
    }
    
    return render(request, 'caja_cerrar.html', context)

@login_required
def caja_list(request):
    """Listar todas las cajas"""
    cajas = Caja.objects.all().order_by('-fecha')
    
    context = {
        'cajas': cajas,
    }
    return render(request, 'caja_list.html', context)
