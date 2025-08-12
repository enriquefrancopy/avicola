from django.core.management.base import BaseCommand
from core.models import Factura

class Command(BaseCommand):
    help = 'Actualiza el estado de todas las facturas basado en sus pagos realizados'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando actualización de estados de facturas...')
        
        facturas = Factura.objects.all()
        actualizadas = 0
        
        for factura in facturas:
            estado_anterior = factura.estado
            factura.actualizar_estado()
            
            if estado_anterior != factura.estado:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Factura #{factura.id} ({factura.numero}): '
                        f'{estado_anterior} → {factura.estado} '
                        f'(Saldo: Gs. {factura.saldo_pendiente:,})'
                    )
                )
                actualizadas += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nActualización completada. {actualizadas} facturas actualizadas de {facturas.count()} total.'
            )
        ) 