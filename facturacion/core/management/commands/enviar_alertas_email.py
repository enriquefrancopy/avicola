from django.core.management.base import BaseCommand
from django.db.models import F
from datetime import datetime, timedelta
from core.models import Producto, Factura
from core.views import obtener_alertas_stock, enviar_email_alertas

class Command(BaseCommand):
    help = 'Enviar alertas del sistema por email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--destinatarios',
            type=str,
            help='Lista de emails separados por comas',
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Modo de prueba (no envía emails reales)',
        )

    def handle(self, *args, **options):
        self.stdout.write('Iniciando envío de alertas por email...')
        
        # Obtener alertas
        alertas = obtener_alertas_stock(None)
        
        if alertas['total_alertas'] == 0:
            self.stdout.write(
                self.style.SUCCESS('No hay alertas pendientes para enviar.')
            )
            return
        
        # Configurar destinatarios
        destinatarios = None
        if options['destinatarios']:
            destinatarios = [email.strip() for email in options['destinatarios'].split(',')]
        
        # Modo de prueba
        if options['test']:
            self.stdout.write('MODO PRUEBA - No se enviarán emails reales')
            self.stdout.write(f'Alertas encontradas: {alertas["total_alertas"]}')
            self.stdout.write(f'Destinatarios: {destinatarios or "Por defecto"}')
            return
        
        # Enviar email
        if enviar_email_alertas(alertas, destinatarios):
            self.stdout.write(
                self.style.SUCCESS(
                    f'Email de alertas enviado correctamente. {alertas["total_alertas"]} alertas incluidas.'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR('Error al enviar el email de alertas.')
            ) 