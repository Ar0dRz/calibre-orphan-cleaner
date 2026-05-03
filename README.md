# 📚 calibre-orphan-cleaner

Script en Python para limpiar registros huérfanos de una biblioteca de [Calibre](https://calibre-ebook.com/), es decir, entradas en la base de datos que ya no tienen un archivo físico correspondiente en disco.

## ¿Para qué sirve?

Cuando eliminas archivos de la carpeta de tu biblioteca de Calibre directamente (sin usar la interfaz de Calibre), la base de datos `metadata.db` conserva los registros de esos libros aunque los archivos ya no existan. Esto genera inconsistencias, advertencias y entradas fantasma en tu biblioteca.

Este script detecta y elimina esos registros de forma segura, con backup automático y confirmación antes de borrar.

---

## Scripts incluidos

| Script | Descripción |
|--------|-------------|
| `calibre_clean.py` | Limpieza básica: elimina registros huérfanos de la base de datos |
| `calibre_clean_full.py` | Limpieza completa: incluye también la eliminación de carpetas vacías que quedaron en disco |

---

## Requisitos

- Python 3.6+
- Calibre instalado (se usa `calibredb` del CLI incluido en Calibre)
- La biblioteca de Calibre debe ser accesible localmente

### Verificar que `calibredb` está disponible

```bash
calibredb --version
```

Si no lo reconoce, agrégalo al PATH según tu sistema:

**macOS:**
```bash
export PATH="/Applications/calibre.app/Contents/MacOS:$PATH"
```

**Linux:**
```bash
# Calibre normalmente lo instala en:
export PATH="$HOME/calibre:$PATH"
```

---

## Uso

### 1. Clona el repositorio

```bash
git clone https://github.com/Ar0dRz/calibre-orphan-cleaner.git
cd calibre-orphan-cleaner
```

### 2. Edita la ruta de tu biblioteca

En el script que vayas a usar, modifica la variable `LIB_PATH`:

```python
LIB_PATH = "/ruta/a/tu/Biblioteca de calibre"
```

Ejemplos:
- macOS: `/Users/tunombre/Biblioteca de calibre`
- Linux: `/home/tunombre/Calibre Library`
- Windows: `C:\Users\tunombre\Calibre Library`

### 3. Cierra Calibre

> ⚠️ **Importante:** Cierra la aplicación Calibre antes de ejecutar el script. No deben acceder a `metadata.db` simultáneamente.

### 4. Ejecuta el script

```bash
# Limpieza básica
python3 calibre_clean.py

# Limpieza completa (incluye carpetas vacías)
python3 calibre_clean_full.py
```

---

## ¿Qué hace el script paso a paso?

1. **Crea un backup automático** de `metadata.db` con timestamp antes de modificar nada
2. **Detecta los registros huérfanos** cruzando la base de datos contra el sistema de archivos
3. **Lista los títulos afectados** para que puedas revisarlos
4. **Solicita confirmación explícita** antes de eliminar cualquier cosa
5. **Elimina los registros** en lotes usando `calibredb remove`
6. *(Solo `calibre_clean_full.py`)* **Elimina las carpetas vacías** que quedaron en disco

---

## Ejemplo de salida

```
✅ Backup creado: /Users/tuusuario/Biblioteca de calibre/metadata.db.bak_20260503_134710

📚 Registros huérfanos encontrados: 544
  [404] Derecho Civil Garfias
  [803] Mario Bunge - Qué es Filosofar Científicamente
  ...

⚠️  Se eliminarán 544 registros de la base de datos.
¿Continuar? (escribe 'si' para confirmar): si

✅ Eliminados IDs: 404, 405, 406, ...
✅ Eliminados IDs: 462, 463, 464, ...
...

🎉 Limpieza completada.
```

---

## Notas de seguridad

- El backup de `metadata.db` se crea **siempre**, antes de cualquier operación
- El script **nunca borra archivos físicos** de tu disco, solo registros de la base de datos
- `calibre_clean_full.py` solo elimina carpetas que estén **completamente vacías**
- Si algo sale mal, puedes restaurar el backup:

```bash
cp "/ruta/biblioteca/metadata.db.bak_TIMESTAMP" "/ruta/biblioteca/metadata.db"
```

---

## Probado en

- macOS Sequoia 15 (MacBook Air, Homebrew Python)
- Calibre 7.x

---

## Licencia

[MIT](LICENSE) — úsalo, modifícalo y compártelo libremente.

---

## Contribuciones

PRs y issues bienvenidos. Si lo usaste en Linux o Windows y funcionó (o no), abre un issue para documentarlo.
