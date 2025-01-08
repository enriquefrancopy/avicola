import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-here'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # Para formateo de números y fechas
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.PermisosMiddleware',  # Middleware de permisos
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.alertas_globales',
                'core.context_processors.configuracion_global',
                'core.context_processors.permisos_usuario',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database  

DATABASES = {
    # Base local rápida
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'avicola',
        'USER': 'postgres',
        'PASSWORD': 'master',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    # Copia online en Supabase (ajusta USER/PASSWORD/NAME/PORT si hace falta)
    'supabase': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres.dnzajyskdadltngemzsg',
        'PASSWORD': 'SJhFYJqD7GDetrBr',
        'HOST': 'aws-0-us-west-2.pooler.supabase.com',
        'PORT': '6543',
        'OPTIONS': {
            'sslmode': 'require',
        },
    },
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URL
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Configuración de sesiones
SESSION_COOKIE_AGE = 1209600  # 14 días en segundos (máximo tiempo de sesión)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # False significa que la sesión no expira al cerrar el navegador
SESSION_SAVE_EVERY_REQUEST = True  # Guardar la sesión en cada request para mantenerla activa

# ============================================================================
# CONFIGURACIÓN DE EMAIL
# ============================================================================

# Configuración de Email (Gmail)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-email@gmail.com'  # Cambiar por tu email
EMAIL_HOST_PASSWORD = 'tu-password-app'  # Cambiar por tu contraseña de aplicación

# Configuración de notificaciones por email
EMAIL_NOTIFICATIONS_ENABLED = True
EMAIL_FROM_ADDRESS = 'Avícola CVA <noreply@avicolacva.com>'
EMAIL_ADMIN_ADDRESS = 'admin@avicolacva.com'  # Email del administrador

# Frecuencia de notificaciones (en horas)
EMAIL_ALERT_FREQUENCY = 24  # Enviar alertas cada 24 horas
