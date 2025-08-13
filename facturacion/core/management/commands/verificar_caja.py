from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import Caja


class Command(BaseCommand):
    help = 'Verificar y crear caja activa para el día actual'

    def handle(self, *args, **options):
        fecha_actual = timezone.now().date()
        
        # Verificar si existe una caja para hoy
        caja_existente = Caja.objects.filter(fecha=fecha_actual).first()
        
        if caja_existente:
            if caja_existente.cerrada:
                self.stdout.write(
                    self.style.WARNING(
                        f'Caja para {fecha_actual} existe pero está CERRADA'
                    )
                )
                self.stdout.write(f'Usuario que cerró: {caja_existente.usuario_cierre}')
                self.stdout.write(f'Fecha de cierre: {caja_existente.fecha_cierre}')
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Caja para {fecha_actual} existe y está ABIERTA'
                    )
                )
                self.stdout.write(f'Usuario que abrió: {caja_existente.usuario_apertura}')
                self.stdout.write(f'Saldo inicial: Gs. {caja_existente.saldo_inicial:,}')
        else:
            self.stdout.write(
                self.style.ERROR(
                    f'No existe caja para {fecha_actual}'
                )
            )
            
            # Preguntar si crear una nueva caja
            crear = input('\n¿Desea crear una nueva caja para hoy? (s/n): ').lower()
            
            if crear in ['s', 'si', 'sí', 'y', 'yes']:
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
        
        # Mostrar todas las cajas del último mes
        self.stdout.write('\n' + '='*50)
        self.stdout.write('CAJAS DEL ÚLTIMO MES:')
        self.stdout.write('='*50)
        
        fecha_inicio = fecha_actual.replace(day=1)
        cajas_recientes = Caja.objects.filter(
            fecha__gte=fecha_inicio
        ).order_by('-fecha')
        
        for caja in cajas_recientes:
            estado = 'ABIERTA' if not caja.cerrada else 'CERRADA'
            color = self.style.SUCCESS if not caja.cerrada else self.style.WARNING
            
            self.stdout.write(
                color(
                    f'{caja.fecha.strftime("%d/%m/%Y")} - {estado} - '
                    f'Usuario: {caja.usuario_apertura.username} - '
                    f'Saldo: Gs. {caja.saldo_inicial:,}'
                )
            )
