# Avícola CVA

Sistema de gestión para facturación, inventario y control de clientes/proveedores en una empresa avícola.

## Características principales
- Gestión de facturas (creación, listado, PDF, anulación)
- Gestión de pagos de facturas
- Control de clientes y proveedores
- Inventario y movimientos de stock
- Dashboard con métricas y gráficos
- Autenticación de usuarios

## Requisitos
- Python 3.10+
- Django 4+
- (Opcional) Entorno virtual (recomendado)

## Instalación
1. Clona el repositorio:
   ```bash
   git clone <URL-del-repo>
   cd AvicolaCVA/facturacion
   ```
2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # En Windows
   source venv/bin/activate  # En Linux/Mac
   ```
3. Instala las dependencias:
   ```bash
   pip install -r ../requirements.txt
   ```
4. Aplica las migraciones:
   ```bash
   python manage.py migrate
   ```
5. (Opcional) Carga datos de prueba:
   ```bash
   python manage.py shell < core/scripts/cargar_datos_prueba.py
   ```
6. Ejecuta el servidor:
   ```bash
   python manage.py runserver
   ```

## Estructura del proyecto
- `core/` - Lógica principal, modelos, scripts y comandos personalizados
- `templates/` - Plantillas HTML
- `static/` - Archivos estáticos (CSS, JS, imágenes)
- `media/` - Archivos subidos por usuarios
- `config/` - Configuración de Django (settings, urls, wsgi, asgi)

## Personalización
- Edita `config/settings.py` para ajustar la base de datos, idioma, zona horaria, etc.
- Cambia el `SECRET_KEY` antes de usar en producción.

## Contacto
Para soporte o sugerencias, contacta a: [Tu Nombre o Email]

---

> Proyecto generado y asistido con IA. ¡Contribuciones y mejoras son bienvenidas! 