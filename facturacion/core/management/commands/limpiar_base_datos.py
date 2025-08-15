from django.core.management.base import BaseCommand
from django.db import connection
from core.models import *

class Command(BaseCommand):
    help = 'Limpia completamente la base de datos eliminando todos los datos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirmar que realmente quieres limpiar la base de datos',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  ADVERTENCIA: Esto eliminará TODOS los datos de la base de datos.\n'
                    'Para confirmar, ejecuta: python manage.py limpiar_base_datos --confirm'
                )
            )
            return

        self.stdout.write('🧹 Iniciando limpieza de la base de datos...')

        # Lista de modelos en orden de eliminación (respetando dependencias)
        modelos_a_eliminar = [
            MovimientoCaja,
            PagoFactura,
            Pago,
            DetalleFactura,
            Factura,
            Gasto,
            Denominacion,
            Caja,
            Notificacion,
            Producto,
            Cliente,
            Proveedor,
            ConfiguracionSistema,
        ]

        for modelo in modelos_a_eliminar:
            try:
                count = modelo.objects.count()
                modelo.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {modelo.__name__}: {count} registros eliminados')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error eliminando {modelo.__name__}: {e}')
                )

        # Resetear secuencias de ID
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence")
            self.stdout.write(self.style.SUCCESS('✅ Secuencias de ID reseteadas'))

        self.stdout.write(
            self.style.SUCCESS(
                '🎉 ¡Base de datos limpiada completamente!\n'
                'Ahora puedes cargar datos nuevos sin conflictos.'
            )
        )
