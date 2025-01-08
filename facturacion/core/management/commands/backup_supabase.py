from django.core.management.base import BaseCommand
from django.core.management import call_command
import tempfile
import os


class Command(BaseCommand):
    help = "Copia todos los datos de la base local (default) a Supabase (supabase)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING(
            "Iniciando backup: copiando datos de 'default' a 'supabase'..."
        ))

        # 1) Volcar datos de la BD local (default) a un archivo JSON temporal (UTF-8)
        with tempfile.NamedTemporaryFile(
            mode="w+", suffix=".json", encoding="utf-8", delete=False
        ) as tmp_file:
            tmp_name = tmp_file.name
            self.stdout.write(f"Generando dump temporal: {tmp_name}")

            call_command(
                "dumpdata",
                database="default",
                natural_foreign=True,
                natural_primary=True,
                exclude=["contenttypes", "auth.Permission"],
                stdout=tmp_file,
            )

        # 2) Cargar ese JSON en la BD supabase
        try:
            self.stdout.write("Cargando datos en base 'supabase' (esto puede tardar)...")
            call_command("loaddata", tmp_name, database="supabase")
        finally:
            # 3) Borrar archivo temporal
            if os.path.exists(tmp_name):
                os.remove(tmp_name)

        self.stdout.write(self.style.SUCCESS(
            "Backup completado: datos sincronizados de 'default' a 'supabase'."
        ))
