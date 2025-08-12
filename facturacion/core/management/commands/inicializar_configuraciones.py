from django.core.management.base import BaseCommand
from core.models import ConfiguracionSistema

class Command(BaseCommand):
    help = 'Inicializar configuraciones del sistema con valores por defecto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Resetear todas las configuraciones existentes',
        )

    def handle(self, *args, **options):
        self.stdout.write('Inicializando configuraciones del sistema...')
        
        # Configuraciones por defecto
        configuraciones_por_defecto = {
            'general': [
                ('nombre_empresa', 'Avícola CVA', 'Nombre de la empresa'),
                ('moneda', 'Gs.', 'Símbolo de moneda'),
                ('pais', 'Paraguay', 'País de la empresa'),
            ],
            'alertas': [
                ('frecuencia_alertas', '24', 'Frecuencia de alertas en horas'),
                ('dias_factura_vencida', '30', 'Días para considerar factura vencida'),
                ('alertas_stock_bajo', 'true', 'Habilitar alertas de stock bajo'),
                ('alertas_productos_agotados', 'true', 'Habilitar alertas de productos agotados'),
                ('alertas_facturas_vencidas', 'true', 'Habilitar alertas de facturas vencidas'),
            ],
            'email': [
                ('email_notificaciones', 'true', 'Habilitar notificaciones por email'),
                ('email_frecuencia', '24', 'Frecuencia de emails en horas'),
                ('email_destinatarios', 'admin@avicolacva.com', 'Emails destinatarios (separados por comas)'),
            ],
            'stock': [
                ('stock_minimo_default', '10', 'Stock mínimo por defecto'),
                ('alertas_stock_critico', 'true', 'Alertas de stock crítico'),
                ('stock_critico_porcentaje', '20', 'Porcentaje para stock crítico'),
            ],
            'facturacion': [
                ('iva_default', '10', 'IVA por defecto (%)'),
                ('numero_factura_inicial', '1', 'Número inicial de facturas'),
                ('formato_factura', 'FAC-{numero}', 'Formato de número de factura'),
            ]
        }
        
        # Resetear si se solicita
        if options['reset']:
            self.stdout.write('Reseteando configuraciones existentes...')
            ConfiguracionSistema.objects.all().delete()
        
        # Crear configuraciones
        total_creadas = 0
        total_actualizadas = 0
        
        for categoria, configs in configuraciones_por_defecto.items():
            self.stdout.write(f'  Configurando categoría: {categoria}')
            
            for clave, valor_por_defecto, descripcion in configs:
                config, created = ConfiguracionSistema.objects.get_or_create(
                    clave=clave,
                    defaults={
                        'valor': valor_por_defecto,
                        'descripcion': descripcion,
                        'categoria': categoria,
                    }
                )
                
                if created:
                    self.stdout.write(f'    ✓ Creada: {clave} = {valor_por_defecto}')
                    total_creadas += 1
                else:
                    if options['reset']:
                        config.valor = valor_por_defecto
                        config.descripcion = descripcion
                        config.categoria = categoria
                        config.save()
                        self.stdout.write(f'    ✓ Actualizada: {clave} = {valor_por_defecto}')
                        total_actualizadas += 1
                    else:
                        self.stdout.write(f'    - Existe: {clave} = {config.valor}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nConfiguraciones inicializadas: {total_creadas} creadas, {total_actualizadas} actualizadas'
            )
        ) 