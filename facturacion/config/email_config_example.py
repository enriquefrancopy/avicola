# ============================================================================
# CONFIGURACIÓN DE EMAIL - EJEMPLO
# ============================================================================
# 
# Para configurar el envío de emails, sigue estos pasos:
#
# 1. COPIA este archivo y renómbralo como 'email_config.py'
# 2. MODIFICA las siguientes configuraciones:
#
# ============================================================================

# Configuración para Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# IMPORTANTE: Usar contraseña de aplicación, NO la contraseña normal
EMAIL_HOST_USER = 'tu-email@gmail.com'  # Tu email de Gmail
EMAIL_HOST_PASSWORD = 'tu-password-app'  # Contraseña de aplicación

# Configuración de notificaciones
EMAIL_NOTIFICATIONS_ENABLED = True
EMAIL_FROM_ADDRESS = 'Avícola CVA <tu-email@gmail.com>'
EMAIL_ADMIN_ADDRESS = 'admin@avicolacva.com'  # Email del administrador

# Frecuencia de notificaciones (en horas)
EMAIL_ALERT_FREQUENCY = 24  # Enviar alertas cada 24 horas

# ============================================================================
# INSTRUCCIONES PARA GMAIL:
# ============================================================================
#
# 1. Ve a tu cuenta de Google
# 2. Activa la verificación en dos pasos
# 3. Ve a "Seguridad" > "Contraseñas de aplicación"
# 4. Genera una nueva contraseña para "Django"
# 5. Usa esa contraseña en EMAIL_HOST_PASSWORD
#
# ============================================================================
#
# INSTRUCCIONES PARA OUTLOOK/HOTMAIL:
# ============================================================================
#
# EMAIL_HOST = 'smtp-mail.outlook.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'tu-email@outlook.com'
# EMAIL_HOST_PASSWORD = 'tu-password'
#
# ============================================================================
#
# INSTRUCCIONES PARA YAHOO:
# ============================================================================
#
# EMAIL_HOST = 'smtp.mail.yahoo.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'tu-email@yahoo.com'
# EMAIL_HOST_PASSWORD = 'tu-password-app'
#
# ============================================================================ 