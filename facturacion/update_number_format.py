#!/usr/bin/env python
"""
Script para actualizar el formato de números en todos los templates
Cambia intcomma por intcomma_dot y agrega la carga del filtro personalizado
"""

import os
import re

def update_template_file(file_path):
    """Actualiza un archivo de template individual"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Agregar custom_filters a la carga de humanize si no está presente
        if '{% load humanize %}' in content and '{% load humanize custom_filters %}' not in content:
            content = content.replace('{% load humanize %}', '{% load humanize custom_filters %}')
        
        # Reemplazar intcomma por intcomma_dot
        content = re.sub(r'\|intcomma\b', '|intcomma_dot', content)
        
        # Solo escribir si hubo cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Actualizado: {file_path}")
            return True
        else:
            print(f"⏭️  Sin cambios: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error en {file_path}: {e}")
        return False

def main():
    """Función principal"""
    templates_dir = "templates"
    updated_count = 0
    total_count = 0
    
    print("🔄 Iniciando actualización del formato de números...")
    print(f"📁 Buscando archivos en: {os.path.abspath(templates_dir)}")
    
    if not os.path.exists(templates_dir):
        print(f"❌ El directorio {templates_dir} no existe!")
        return
    
    # Recorrer todos los archivos .html en el directorio templates
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                total_count += 1
                print(f"📄 Procesando: {file_path}")
                if update_template_file(file_path):
                    updated_count += 1
    
    print(f"\n📊 Resumen:")
    print(f"   Total de archivos procesados: {total_count}")
    print(f"   Archivos actualizados: {updated_count}")
    print(f"   Archivos sin cambios: {total_count - updated_count}")
    print("\n✅ Proceso completado!")

if __name__ == "__main__":
    main() 