# ⚙️ Panel de Configuración del Sistema - Avícola CVA

## 🎯 Descripción

El Panel de Configuración permite gestionar todos los parámetros del sistema desde una interfaz web intuitiva, sin necesidad de editar archivos de código. Incluye configuraciones para:

- **Configuración General** (empresa, moneda, país)
- **Sistema de Alertas** (frecuencia, umbrales, tipos)
- **Notificaciones por Email** (SMTP, destinatarios, frecuencia)
- **Gestión de Stock** (mínimos, porcentajes críticos)
- **Facturación** (IVA, formato de números, secuencia)

## 🚀 Acceso

### Desde la Interfaz Web
1. **Menú Lateral**: Administración → Configuración
2. **URL Directa**: `/configuracion/`
3. **Dashboard**: Enlace en la sección de administración

### Desde la Línea de Comandos
```bash
# Inicializar configuraciones por defecto
python manage.py inicializar_configuraciones

# Resetear todas las configuraciones
python manage.py inicializar_configuraciones --reset
```

## 📋 Categorías de Configuración

### 🏢 **Configuración General**
- **nombre_empresa**: Nombre que aparece en el sistema
- **moneda**: Símbolo de moneda (Gs., $, etc.)
- **pais**: País de la empresa

### 🔔 **Sistema de Alertas**
- **frecuencia_alertas**: Horas entre verificaciones (24)
- **dias_factura_vencida**: Días para considerar vencida (30)
- **alertas_stock_bajo**: Habilitar alertas de stock bajo (true/false)
- **alertas_productos_agotados**: Alertas de productos sin stock (true/false)
- **alertas_facturas_vencidas**: Alertas de facturas vencidas (true/false)

### 📧 **Notificaciones por Email**
- **email_notificaciones**: Habilitar emails automáticos (true/false)
- **email_frecuencia**: Frecuencia de emails en horas (24)
- **email_destinatarios**: Lista de emails separados por comas

### 📦 **Gestión de Stock**
- **stock_minimo_default**: Stock mínimo por defecto para productos (10)
- **alertas_stock_critico**: Habilitar alertas críticas (true/false)
- **stock_critico_porcentaje**: Porcentaje para stock crítico (20%)

### 🧾 **Facturación**
- **iva_default**: IVA por defecto en porcentaje (10%)
- **numero_factura_inicial**: Número inicial de facturas (1)
- **formato_factura**: Formato de numeración (FAC-{numero})

## 🎨 Interfaz de Usuario

### Panel Principal
- **Vista por Categorías**: Organizadas en tarjetas con iconos
- **Edición Inline**: Cambiar valores directamente en la tabla
- **Guardado Automático**: Botón de confirmación para cada cambio
- **Notificaciones Toast**: Feedback inmediato de las acciones

### Edición Individual
- **Formulario Detallado**: Edición completa con descripción
- **Información Técnica**: ID, fechas de creación/actualización
- **Validación**: Campos requeridos y formatos

### Funciones Avanzadas
- **Resetear Configuraciones**: Volver a valores por defecto
- **Búsqueda y Filtros**: Encontrar configuraciones rápidamente
- **Exportar/Importar**: Backup y restauración de configuraciones

## 🔧 Uso del Sistema

### Edición Rápida
1. **Acceder al Panel**: Menú → Configuración
2. **Seleccionar Categoría**: Hacer clic en la tarjeta deseada
3. **Editar Valor**: Cambiar el valor en el campo de texto
4. **Guardar**: Presionar Enter o hacer clic en el botón ✓
5. **Confirmar**: Ver notificación de éxito

### Edición Detallada
1. **Acceder al Panel**: Menú → Configuración
2. **Hacer Clic en Editar**: Botón de lápiz en la fila deseada
3. **Modificar Campos**: Valor y descripción
4. **Guardar Cambios**: Botón "Guardar Cambios"
5. **Volver al Panel**: Enlace "Volver"

### Resetear Configuraciones
1. **Acceder al Panel**: Menú → Configuración
2. **Hacer Clic en Resetear**: Botón en el header
3. **Confirmar Acción**: Diálogo de confirmación
4. **Esperar Proceso**: Reset automático de todas las configuraciones

## 💾 Persistencia de Datos

### Base de Datos
- **Modelo**: `ConfiguracionSistema`
- **Tabla**: `core_configuracionsistema`
- **Campos**: clave, valor, descripción, categoría, activo, fechas

### Caché
- **Almacenamiento**: Valores en memoria para acceso rápido
- **Invalidación**: Al modificar configuraciones
- **Persistencia**: Entre reinicios del servidor

## 🔒 Seguridad

### Acceso
- **Autenticación Requerida**: Solo usuarios logueados
- **Permisos**: Acceso completo para administradores
- **Auditoría**: Log de cambios en configuraciones

### Validación
- **Tipos de Datos**: Validación según el tipo de configuración
- **Rangos**: Valores mínimos y máximos permitidos
- **Formato**: Validación de formatos específicos

## 🐛 Solución de Problemas

### Configuración No Se Guarda
1. **Verificar Permisos**: Usuario debe estar autenticado
2. **Revisar Consola**: Errores JavaScript en el navegador
3. **Verificar Servidor**: Logs de Django para errores

### Valores No Se Aplican
1. **Reiniciar Servidor**: Para aplicar cambios críticos
2. **Limpiar Caché**: Borrar caché del navegador
3. **Verificar Base de Datos**: Confirmar que se guardó correctamente

### Error de Acceso
1. **Verificar Login**: Usuario debe estar logueado
2. **Revisar URLs**: Confirmar rutas correctas
3. **Verificar Migraciones**: Base de datos actualizada

## 📊 Monitoreo

### Logs del Sistema
- **Cambios de Configuración**: Quién, cuándo, qué cambió
- **Errores de Validación**: Problemas con valores
- **Accesos al Panel**: Auditoría de uso

### Métricas
- **Configuraciones Más Editadas**: Análisis de uso
- **Frecuencia de Cambios**: Patrones de modificación
- **Errores Comunes**: Problemas frecuentes

## 🔄 Integración

### Con Otros Módulos
- **Sistema de Alertas**: Usa configuraciones de frecuencia
- **Email**: Configuraciones SMTP y destinatarios
- **Facturación**: IVA y formato de números
- **Stock**: Umbrales mínimos y críticos

### API
- **Endpoint**: `/api/configuracion/`
- **Métodos**: GET, POST, PUT, DELETE
- **Formato**: JSON
- **Autenticación**: Token o sesión

## 📈 Mejoras Futuras

### Funcionalidades Planificadas
- **Configuraciones por Usuario**: Personalización individual
- **Historial de Cambios**: Versiones de configuraciones
- **Importar/Exportar**: Backup y restauración
- **Validación Avanzada**: Reglas de negocio complejas
- **Notificaciones**: Alertas de cambios críticos

### Optimizaciones
- **Caché Inteligente**: Invalidación selectiva
- **Validación en Tiempo Real**: Feedback inmediato
- **Interfaz Responsiva**: Mejor experiencia móvil
- **Búsqueda Avanzada**: Filtros y ordenamiento

## 📞 Soporte

Para problemas con el panel de configuración:
1. **Revisar Logs**: Consola del navegador y servidor
2. **Verificar Base de Datos**: Estado de las configuraciones
3. **Probar Comandos**: Usar comandos de gestión
4. **Contactar Administrador**: Para problemas complejos 