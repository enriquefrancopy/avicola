from .models import PermisoUsuario


class PermisosMiddleware:
    """
    Carga los permisos del usuario en cada request.
    Si el usuario es superusuario tiene todos los permisos; de lo contrario
    se obtienen desde PermisoUsuario y se exponen en request.usuario_permisos.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        permisos_dict = {}

        if request.user.is_authenticated:
            if request.user.is_superuser:
                # Superusuarios: todos los permisos habilitados
                permisos_dict = {
                    modulo: {
                        "ver": True,
                        "crear": True,
                        "editar": True,
                        "eliminar": True,
                    }
                    for modulo, _ in PermisoUsuario.MODULO_CHOICES
                }
            else:
                # Crear permisos por defecto si no existen
                if not PermisoUsuario.objects.filter(usuario=request.user).exists():
                    PermisoUsuario.crear_permisos_por_defecto(request.user)

                # Cargar permisos del usuario
                for permiso in PermisoUsuario.objects.filter(usuario=request.user):
                    permisos_dict[permiso.modulo] = {
                        "ver": permiso.puede_ver,
                        "crear": permiso.puede_crear,
                        "editar": permiso.puede_editar,
                        "eliminar": permiso.puede_eliminar,
                    }

        # Disponible para vistas y templates
        request.usuario_permisos = permisos_dict

        return self.get_response(request)
