from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Productos
    path('productos/', views.productos_list, name='productos_list'),
    path('productos/agregar/', views.producto_crear, name='producto_crear'),
    path('productos/<int:pk>/editar/', views.producto_editar, name='producto_editar'),
    path('productos/<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),
    path('productos/<int:pk>/reactivar/', views.producto_reactivar, name='producto_reactivar'),
    path('productos/<int:pk>/ajustar-stock/', views.producto_ajustar_stock, name='producto_ajustar_stock'),
    
    # Proveedores
    path('proveedores/', views.proveedores_list, name='proveedores_list'),
    path('proveedores/agregar/', views.proveedor_crear, name='proveedor_crear'),
    path('proveedores/<int:pk>/editar/', views.proveedor_editar, name='proveedor_editar'),
    path('proveedores/<int:pk>/eliminar/', views.proveedor_eliminar, name='proveedor_eliminar'),
    path('proveedores/<int:pk>/reactivar/', views.proveedor_reactivar, name='proveedor_reactivar'),
    
    # Facturas
    path('facturas/', views.factura_list, name='factura_list'),
    path('facturas/crear/', views.factura_crear, name='factura_crear'),
    path('facturas/<int:pk>/', views.factura_ver, name='factura_ver'),
    path('facturas/<int:pk>/editar/', views.factura_editar, name='factura_editar'),
    path('facturas/<int:pk>/eliminar/', views.factura_eliminar, name='factura_eliminar'),
    path('facturas/<int:pk>/anular/', views.factura_anular, name='factura_anular'),
    path('facturas/<int:pk>/pagos/', views.factura_pagos, name='factura_pagos'),
    path('facturas/<int:pk>/recalcular/', views.recalcular_totales_factura, name='recalcular_totales_factura'),
    
    # Stock
    path('stock/movimientos/', views.stock_movimientos, name='stock_movimientos'),
    
    # Pagos
    path('facturas/<int:pk>/pagos/', views.factura_pagos, name='factura_pagos'),
    path('pagos/', views.pagos_dashboard, name='pagos_dashboard'),
    path('pagos/clientes/', views.pagos_clientes_list, name='pagos_clientes_list'),
    path('pagos/proveedores/', views.pagos_proveedores_list, name='pagos_proveedores_list'),
    path('pagos/crear/<int:factura_id>/', views.pago_crear, name='pago_crear'),
    path('pagos/multiple/crear/', views.pago_multiple_crear, name='pago_multiple_crear'),
    path('pagos/<int:pago_id>/asignar/', views.pago_asignar_facturas, name='pago_asignar_facturas'),
    path('pagos/<int:pago_id>/ver/', views.pago_ver, name='pago_ver'),
    path('asignaciones/<int:pk>/eliminar/', views.asignacion_eliminar, name='asignacion_eliminar'),
    
    # API endpoints para AJAX
    path('api/productos/get/', views.get_producto_info, name='get_producto_info'),
    path('api/facturas/total/', views.calcular_total_factura, name='calcular_total_factura'),
    path('api/proveedores/buscar/', views.buscar_proveedores, name='buscar_proveedores'),
    path('api/proveedores/crear/', views.proveedor_crear_ajax, name='proveedor_crear_ajax'),
    path('api/clientes/buscar/', views.buscar_clientes, name='buscar_clientes'),
    path('api/clientes/crear/', views.cliente_crear_ajax, name='cliente_crear_ajax'),
    path('api/productos/buscar/', views.buscar_productos, name='buscar_productos'),
    path('api/dashboard/data/', views.dashboard_data, name='dashboard_data'),

    # Exportaciones a Excel
    path('exportar/facturas/excel/', views.exportar_facturas_excel, name='exportar_facturas_excel'),
    path('exportar/productos/excel/', views.exportar_productos_excel, name='exportar_productos_excel'),
    path('exportar/proveedores/excel/', views.exportar_proveedores_excel, name='exportar_proveedores_excel'),
    path('exportar/detalles-facturas/excel/', views.exportar_detalles_facturas_excel, name='exportar_detalles_facturas_excel'),
    
    # Sistema de Alertas
    path('notificaciones/', views.notificaciones_list, name='notificaciones_list'),
    path('notificaciones/<int:pk>/marcar-leida/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    path('api/notificaciones/', views.obtener_notificaciones_ajax, name='obtener_notificaciones_ajax'),
    
    # Sistema de Email
    path('enviar-alertas-email/', views.enviar_alertas_email, name='enviar_alertas_email'),
    
    # Panel de Configuración
    path('configuracion/', views.configuracion_panel, name='configuracion_panel'),
    path('configuracion/<int:pk>/editar/', views.configuracion_editar, name='configuracion_editar'),
    path('configuracion/guardar-ajax/', views.configuracion_guardar_ajax, name='configuracion_guardar_ajax'),
    path('configuracion/resetear/', views.configuracion_resetear, name='configuracion_resetear'),
    path('configuracion/temas/', views.configuracion_temas, name='configuracion_temas'),
    
    # Reportes Avanzados
    path('reportes/', views.reportes_dashboard, name='reportes_dashboard'),
    path('reportes/ventas/', views.reporte_ventas_detallado, name='reporte_ventas_detallado'),
    path('reportes/productos/', views.reporte_productos_analisis, name='reporte_productos_analisis'),
    path('reportes/clientes-proveedores/', views.reporte_clientes_proveedores, name='reporte_clientes_proveedores'),
    path('reportes/pagos-proveedores/', views.reporte_pagos_proveedores, name='reporte_pagos_proveedores'),
    
    # Módulo de Pagos a Proveedores
    path('pagos-proveedores/', views.pagos_proveedores_dashboard, name='pagos_proveedores_dashboard'),
    path('pagos-proveedores/crear/', views.pago_proveedor_crear, name='pago_proveedor_crear'),
    path('pagos-proveedores/<int:pago_id>/ver/', views.pago_proveedor_ver, name='pago_proveedor_ver'),
    path('pagos-proveedores/<int:pago_id>/asignar/', views.pago_proveedor_asignar, name='pago_proveedor_asignar'),
    path('pagos-proveedores/<int:pago_id>/eliminar/', views.pago_proveedor_eliminar, name='pago_proveedor_eliminar'),
    path('pagos-proveedores/vencidas/', views.pagos_proveedores_vencidas, name='pagos_proveedores_vencidas'),
    path('asignacion-proveedor/<int:asignacion_id>/eliminar/', views.asignacion_proveedor_eliminar, name='asignacion_proveedor_eliminar'),

    # MÓDULO DE CONTROL DE CAJA
    path('caja/', views.caja_list, name='caja_list'),
    path('caja/abrir/', views.caja_abrir, name='caja_abrir'),
    path('caja/<int:caja_id>/', views.caja_ver, name='caja_ver'),
    path('caja/<int:caja_id>/cerrar/', views.caja_cerrar, name='caja_cerrar'),
    path('caja/<int:caja_id>/gasto/crear/', views.gasto_crear, name='gasto_crear'),
    path('caja/<int:caja_id>/movimiento/crear/', views.movimiento_crear, name='movimiento_crear'),
    path('gasto/<int:gasto_id>/editar/', views.gasto_editar, name='gasto_editar'),
    path('gasto/<int:gasto_id>/eliminar/', views.gasto_eliminar, name='gasto_eliminar'),
    path('caja/reporte/', views.reporte_caja, name='reporte_caja'),
]
