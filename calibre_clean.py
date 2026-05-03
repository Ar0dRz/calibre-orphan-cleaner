#!/usr/bin/env python3
"""
calibre_clean.py
────────────────
Elimina registros huérfanos de una biblioteca de Calibre:
entradas en metadata.db cuyos archivos ya no existen en disco.

Uso:
    1. Edita la variable LIB_PATH con la ruta a tu biblioteca.
    2. Cierra la aplicación Calibre.
    3. Ejecuta: python3 calibre_clean.py

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
        print("   Nada que limpiar. La biblioteca está sincronizada.")
        os.remove(backup_path)
        print(f"   Backup eliminado (no era necesario).")
        return

    for book_id, title in huerfanos:
        print(f"  [{book_id}] {title}")

    # 4. Confirmación explícita antes de borrar
    print(f"\n⚠️  Se eliminarán {len(huerfanos)} registros de la base de datos.")
    confirm = input("¿Continuar? (escribe 'si' para confirmar): ").strip().lower()

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
        print(f"   Backup disponible en: {backup_path}")
    else:
        print("\n🎉 Limpieza completada.")
        print(f"   Backup disponible en: {backup_path}")
        print("   Puedes eliminarlo cuando confirmes que Calibre funciona bien.")


if __name__ == "__main__":
    main()
