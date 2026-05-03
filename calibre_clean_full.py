#!/usr/bin/env python3
"""
calibre_clean_full.py
──────────────────────
Limpieza completa de una biblioteca de Calibre:
  1. Elimina registros huérfanos de metadata.db
     (entradas cuyos archivos ya no existen en disco)
  2. Elimina las carpetas vacías que quedaron en disco
     tras eliminar los archivos manualmente

Uso:
    1. Edita la variable LIB_PATH con la ruta a tu biblioteca.
    2. Cierra la aplicación Calibre.
    3. Ejecuta: python3 calibre_clean_full.py

Requisitos:
    - Python 3.6+
    - calibredb disponible en PATH (incluido con la instalación de Calibre)

Autor: https://github.com/david_nieto01
Licencia: MIT
"""

import os
import sqlite3
import subprocess
import shutil
from datetime import datetime

# ── CONFIGURA ESTO ────────────────────────────────────────────────────────────
LIB_PATH = "/ruta/a/tu/Biblioteca de calibre"
# Ejemplos:
#   macOS:   "/Users/tunombre/Biblioteca de calibre"
#   Linux:   "/home/tunombre/Calibre Library"
#   Windows: r"C:\Users\tunombre\Calibre Library"
# ──────────────────────────────────────────────────────────────────────────────

CHUNK_SIZE = 50  # Número de IDs por lote al llamar a calibredb

# Carpetas del nivel raíz que Calibre usa internamente y NO deben tocarse
CALIBRE_SYSTEM_DIRS = {"metadata.db", "metadata_db_prefs_backup.json", ".caltrash"}


def main():
    db_path = os.path.join(LIB_PATH, "metadata.db")

    if not os.path.exists(db_path):
        print(f"❌ No se encontró metadata.db en: {LIB_PATH}")
        print("   Verifica que LIB_PATH apunte a tu biblioteca de Calibre.")
        return

    # 1. Backup automático antes de tocar nada
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(LIB_PATH, f"metadata.db.bak_{timestamp}")
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup creado: {backup_path}")

    # 2. Leer registros de la base de datos
    db = sqlite3.connect(db_path)
    books = db.execute("SELECT id, title, path FROM books").fetchall()
    db.close()

    # 3. Detectar huérfanos (registros sin carpeta en disco)
    huerfanos = []
    for book_id, title, rel_path in books:
        full_path = os.path.join(LIB_PATH, rel_path)
        if not os.path.exists(full_path):
            huerfanos.append((book_id, title))

    print(f"\n📚 Registros huérfanos encontrados: {len(huerfanos)}")

    if not huerfanos:
        print("   Nada que limpiar en la base de datos.")
    else:
        for book_id, title in huerfanos:
            print(f"  [{book_id}] {title}")

        # 4. Confirmación para eliminar registros de la DB
        print(f"\n⚠️  Se eliminarán {len(huerfanos)} registros de la base de datos.")
        confirm = input("¿Continuar con la limpieza de la base de datos? (escribe 'si'): ").strip().lower()

        if confirm != "si":
            print("Cancelado. No se modificó nada.")
            print(f"Puedes eliminar el backup manualmente: {backup_path}")
            return

        # 5. Eliminar registros en lotes usando calibredb
        ids = [str(b[0]) for b in huerfanos]
        errores = False

        for i in range(0, len(ids), CHUNK_SIZE):
            chunk = ids[i:i + CHUNK_SIZE]
            cmd = ["calibredb", "remove", "--with-library", LIB_PATH] + chunk
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Eliminados IDs: {', '.join(chunk)}")
            else:
                print(f"❌ Error en lote {i // CHUNK_SIZE + 1}: {result.stderr.strip()}")
                errores = True

        if errores:
            print("\n⚠️  Hubo errores en algunos lotes. Revisa los mensajes anteriores.")
        else:
            print("\n✅ Base de datos limpia.")

    # 6. Detectar y eliminar carpetas vacías en la biblioteca
    print("\n🗂️  Buscando carpetas vacías en disco...")

    carpetas_vacias = []
    for entry in os.scandir(LIB_PATH):
        if not entry.is_dir():
            continue
        if entry.name in CALIBRE_SYSTEM_DIRS:
            continue
        # Una carpeta de libro en Calibre puede tener subcarpetas (por autor)
        # Revisamos si la carpeta (y sus subdirectorios) está completamente vacía
        contenido = list(os.walk(entry.path))
        archivos_totales = sum(len(files) for _, _, files in contenido)
        if archivos_totales == 0:
            carpetas_vacias.append(entry.path)

    print(f"   Carpetas vacías encontradas: {len(carpetas_vacias)}")

    if carpetas_vacias:
        for carpeta in carpetas_vacias:
            print(f"  📁 {carpeta}")

        confirm2 = input("\n¿Eliminar estas carpetas vacías? (escribe 'si'): ").strip().lower()

        if confirm2 == "si":
            eliminadas = 0
            for carpeta in carpetas_vacias:
                try:
                    shutil.rmtree(carpeta)
                    print(f"  🗑️  Eliminada: {carpeta}")
                    eliminadas += 1
                except Exception as e:
                    print(f"  ❌ Error eliminando {carpeta}: {e}")
            print(f"\n✅ {eliminadas} carpetas eliminadas.")
        else:
            print("   Carpetas conservadas. No se eliminó nada en disco.")

    print(f"\n🎉 Proceso completado.")
    print(f"   Backup disponible en: {backup_path}")
    print("   Puedes eliminarlo cuando confirmes que Calibre funciona bien.")


if __name__ == "__main__":
    main()
