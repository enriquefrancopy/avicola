from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import Caja


class Command(BaseCommand):
    help = 'Crear caja activa para el día actual'

    def handle(self, *args, **options):
        fecha_actual = timezone.now().date()
        
        # Verificar si ya existe una caja para hoy
        caja_existente = Caja.objects.filter(fecha=fecha_actual).first()
        
        if caja_existente:
            self.stdout.write(
                self.style.WARNING(
                    f'Ya existe una caja para {fecha_actual}'
                )
            )
            self.stdout.write(f'Estado: {"ABIERTA" if not caja_existente.cerrada else "CERRADA"}')
            return
        
        # Obtener el primer usuario disponible
        usuario = User.objects.first()
        if not usuario:
            self.stdout.write(
                self.style.ERROR('No hay usuarios en el sistema')
            )
            return
        
        # Crear nueva caja
        nueva_caja = Caja.objects.create(
            fecha=fecha_actual,
            saldo_inicial=0,
            usuario_apertura=usuario,
            cerrada=False
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Caja creada exitosamente para {fecha_actual}'
            )
        )
        self.stdout.write(f'ID: {nueva_caja.id}')
        self.stdout.write(f'Usuario: {usuario.username}')
        self.stdout.write(f'Saldo inicial: Gs. {nueva_caja.saldo_inicial:,}')
        
        # Verificar que se puede obtener
        caja_activa = Caja.obtener_caja_activa()
        if caja_activa:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Caja activa detectada: {caja_activa.fecha} - {"ABIERTA" if not caja_activa.cerrada else "CERRADA"}'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR('No se pudo detectar la caja activa')
            )
