# 📧 Sistema de Notificaciones por Email - Avícola CVA

## 🎯 Descripción

El sistema de notificaciones por email permite recibir alertas automáticas sobre:
- 📦 Productos con stock bajo
- ❌ Productos agotados  
- 💰 Facturas vencidas
- 📊 Reportes diarios de alertas

## ⚙️ Configuración

### 1. Configurar Email (Gmail)

1. **Activar verificación en dos pasos** en tu cuenta de Google
2. **Generar contraseña de aplicación**:
   - Ve a Google Account > Seguridad
   - "Contraseñas de aplicación" > "Django"
   - Copia la contraseña generada

3. **Editar configuración** en `config/settings.py`:
```python
EMAIL_HOST_USER = 'tu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu-password-app'  # Contraseña de aplicación
EMAIL_ADMIN_ADDRESS = 'admin@avicolacva.com'
```

### 2. Configurar Email (Outlook/Hotmail)

```python
EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-email@outlook.com'
EMAIL_HOST_PASSWORD = 'tu-password'
```

### 3. Configurar Email (Yahoo)

```python
EMAIL_HOST = 'smtp.mail.yahoo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-email@yahoo.com'
EMAIL_HOST_PASSWORD = 'tu-password-app'
```

## 🚀 Uso

### Envío Manual

1. **Desde el Dashboard**: Botón "Enviar Email" en la sección de alertas
2. **Comando directo**:
```bash
python manage.py enviar_alertas_email
```

### Envío Automático

Configurar cron job para envío automático:

```bash
# Enviar alertas diarias a las 8:00 AM
0 8 * * * cd /ruta/al/proyecto && python manage.py enviar_alertas_email

# Enviar alertas cada 12 horas
0 */12 * * * cd /ruta/al/proyecto && python manage.py enviar_alertas_email
```

### Opciones del Comando

```bash
# Modo de prueba (no envía emails reales)
python manage.py enviar_alertas_email --test

# Enviar a emails específicos
python manage.py enviar_alertas_email --destinatarios="admin@empresa.com,gerente@empresa.com"

# Combinar opciones
python manage.py enviar_alertas_email --test --destinatarios="test@email.com"
```

## 📧 Tipos de Email

### 1. Reporte Diario de Alertas
- **Plantilla**: `emails/alertas_diarias.html`
- **Contenido**: Resumen de todas las alertas del sistema
- **Frecuencia**: Configurable (por defecto 24 horas)

### 2. Alerta de Stock Bajo
- **Plantilla**: `emails/stock_bajo.html`
- **Contenido**: Producto específico con stock bajo
- **Trigger**: Cuando stock ≤ stock mínimo

### 3. Alerta de Producto Agotado
- **Plantilla**: `emails/producto_agotado.html`
- **Contenido**: Producto con stock = 0
- **Trigger**: Cuando stock = 0

### 4. Alerta de Factura Vencida
- **Plantilla**: `emails/factura_vencida.html`
- **Contenido**: Factura pendiente > 30 días
- **Trigger**: Cuando factura está vencida

## 🎨 Personalización

### Modificar Plantillas

Las plantillas están en `templates/emails/`:
- `base_email.html` - Plantilla base con estilos
- `alertas_diarias.html` - Reporte completo
- `stock_bajo.html` - Alerta específica de stock
- `producto_agotado.html` - Alerta de producto agotado
- `factura_vencida.html` - Alerta de factura vencida

### Modificar Estilos

Editar CSS en `base_email.html`:
```css
.email-container {
    background-color: #ffffff;
    border-radius: 8px;
    padding: 30px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
```

## 🔧 Configuración Avanzada

### Frecuencia de Alertas

En `settings.py`:
```python
EMAIL_ALERT_FREQUENCY = 24  # Horas entre alertas
```

### Múltiples Destinatarios

```python
EMAIL_ADMIN_ADDRESS = 'admin@empresa.com'
# O usar lista:
EMAIL_ADMIN_ADDRESS = ['admin@empresa.com', 'gerente@empresa.com']
```

### Deshabilitar Notificaciones

```python
EMAIL_NOTIFICATIONS_ENABLED = False
```

## 🐛 Solución de Problemas

### Error: "Authentication failed"

1. Verificar que la verificación en dos pasos esté activada
2. Usar contraseña de aplicación, no la contraseña normal
3. Verificar que el email y contraseña sean correctos

### Error: "Connection refused"

1. Verificar configuración SMTP
2. Verificar puerto (587 para TLS, 465 para SSL)
3. Verificar firewall/antivirus

### Emails no llegan

1. Verificar carpeta de spam
2. Verificar configuración de destinatarios
3. Usar modo de prueba para verificar: `--test`

## 📋 Checklist de Configuración

- [ ] Verificación en dos pasos activada
- [ ] Contraseña de aplicación generada
- [ ] Configuración SMTP correcta
- [ ] Email de prueba enviado
- [ ] Cron job configurado (opcional)
- [ ] Plantillas personalizadas (opcional)

## 📞 Soporte

Para problemas con el sistema de email:
1. Revisar logs del servidor
2. Usar modo de prueba: `--test`
3. Verificar configuración SMTP
4. Contactar al administrador del sistema 