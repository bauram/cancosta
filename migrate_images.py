#!/usr/bin/env python3
"""
migrate_images.py

Escanea un proyecto web clonado (HTML + CSS), detecta todas las imágenes
que se siguen sirviendo desde un dominio EXTERNO (típicamente el CDN del
sitio original: Webflow, Squarespace, WordPress...), las descarga a una
carpeta local dentro del proyecto y reescribe el HTML/CSS para que apunten
a la copia local en vez de al dominio externo.

Es idempotente: se puede volver a ejecutar sobre el mismo proyecto sin
re-descargar nada que ya esté migrado ni duplicar referencias. El estado
se guarda en <images-dir>/.cdn-map.json (URL original -> nombre de archivo
local), así que no se debe borrar esa carpeta a mano entre ejecuciones si
se quiere conservar la idempotencia.

Fuera de alcance a propósito: no toca fuentes (woff/woff2/ttf/otf/eot),
scripts, ni ninguna URL que no tenga pinta de imagen por su extensión.
Tampoco crea ni gestiona ningún repositorio Git — solo deja los archivos
listos en la carpeta del proyecto para que el flujo normal de
add/commit/push se encargue de subirlos.

Uso:
    python3 migrate_images.py <carpeta_proyecto> [--images-dir images] [--dry-run]

Salida: resumen con cuántas imágenes se detectaron, cuántas se
descargaron en esta ejecución, cuántas ya estaban migradas de antes, y
el detalle de cualquier descarga fallida (URL + motivo).
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

IMAGE_EXT_PATTERN = r"png|jpe?g|gif|svg|webp|ico|avif|bmp"

# Cualquier URL absoluta http(s) que termine (antes de un posible ?query)
# en una extensión de imagen conocida. Cubre de una vez src="", data-src="",
# poster="", href="" sueltos a imágenes, y también el contenido de srcset
# (que se separa aparte, pero cada URL individual también cae aquí).
URL_PATTERN = re.compile(
    r"https?://[^\s\"'()]+?\.(?:" + IMAGE_EXT_PATTERN + r")(?:\?[^\s\"'()]*)?",
    re.IGNORECASE,
)

HTML_EXTENSIONS = {".html", ".htm"}
CSS_EXTENSIONS = {".css"}

USER_AGENT = (
    "Mozilla/5.0 (compatible; clone-web-cdn/1.0; +migracion de imagenes a local)"
)


def find_project_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        # No bajar a carpetas típicas que no deben tocarse
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "images")]
        for name in filenames:
            ext = os.path.splitext(name)[1].lower()
            if ext in HTML_EXTENSIONS or ext in CSS_EXTENSIONS:
                yield os.path.join(dirpath, name)


def extract_urls(text: str):
    return set(URL_PATTERN.findall(text))


def local_filename_for(url: str, used_names: dict) -> str:
    """Deriva el nombre de archivo local a partir de la URL, decodificando
    %XX, y evita colisiones si dos URLs distintas terminan con el mismo
    nombre de archivo (añade un sufijo corto basado en la propia URL)."""
    path = urllib.parse.urlparse(url).path
    name = urllib.parse.unquote(os.path.basename(path))
    if not name:
        name = "imagen"

    if name not in used_names:
        used_names[name] = url
        return name

    if used_names[name] == url:
        return name

    # Colisión real: dos URLs distintas que darían el mismo nombre de
    # archivo. Desambigua con un sufijo corto y estable derivado de la URL.
    import hashlib

    suffix = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
    base, ext = os.path.splitext(name)
    new_name = f"{base}-{suffix}{ext}"
    used_names[new_name] = url
    return new_name


def download(url: str, dest_path: str):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
        with open(dest_path, "wb") as f:
            f.write(data)
        return True, ""
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return False, str(e.reason)
    except Exception as e:  # noqa: BLE001 - queremos capturar cualquier fallo de red
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("proyecto", help="Ruta a la carpeta raíz del proyecto clonado")
    parser.add_argument("--images-dir", default="images", help="Nombre de la subcarpeta de destino dentro del proyecto (por defecto: images)")
    parser.add_argument("--dry-run", action="store_true", help="No descarga ni escribe nada, solo muestra qué haría")
    args = parser.parse_args()

    root = os.path.abspath(args.proyecto)
    if not os.path.isdir(root):
        print(f"Error: '{root}' no es una carpeta válida.", file=sys.stderr)
        sys.exit(1)

    images_dir = os.path.join(root, args.images_dir)
    map_path = os.path.join(images_dir, ".cdn-map.json")

    cdn_map = {}
    if os.path.isfile(map_path):
        with open(map_path, "r", encoding="utf-8") as f:
            cdn_map = json.load(f)

    files = list(find_project_files(root))
    if not files:
        print("No se encontraron archivos .html/.htm/.css en el proyecto.")
        return

    # --- Paso 1: detectar todas las URLs externas de imagen presentes hoy ---
    file_contents = {}
    detected = set()
    for path in files:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        file_contents[path] = content
        detected |= extract_urls(content)

    if not detected:
        print("No se detectó ninguna URL de imagen externa: el proyecto ya está migrado (o nunca dependió de un CDN externo).")
        return

    # --- Paso 2: descargar lo que falte ---
    used_names = {}
    for name, url in cdn_map.items():
        used_names[name] = url

    newly_downloaded = []
    already_migrated = []
    failed = []

    if not args.dry_run:
        os.makedirs(images_dir, exist_ok=True)

    for url in sorted(detected):
        existing_name = None
        for name, mapped_url in cdn_map.items():
            if mapped_url == url:
                existing_name = name
                break

        if existing_name and os.path.isfile(os.path.join(images_dir, existing_name)):
            already_migrated.append(url)
            continue

        filename = local_filename_for(url, used_names)
        dest = os.path.join(images_dir, filename)

        if args.dry_run:
            newly_downloaded.append((url, filename))
            continue

        ok, error = download(url, dest)
        if ok:
            cdn_map[filename] = url
            newly_downloaded.append((url, filename))
        else:
            failed.append((url, error))

    if not args.dry_run:
        with open(map_path, "w", encoding="utf-8") as f:
            json.dump(cdn_map, f, indent=2, ensure_ascii=False, sort_keys=True)

    # --- Paso 3: relinkar en todos los archivos, usando el mapa completo ---
    url_to_filename = {v: k for k, v in cdn_map.items()}
    files_changed = 0

    for path, content in file_contents.items():
        new_content = content
        for url, filename in url_to_filename.items():
            if url not in new_content:
                continue
            rel = os.path.relpath(images_dir, start=os.path.dirname(path))
            rel_url = rel.replace(os.sep, "/") + "/" + filename
            new_content = new_content.replace(url, rel_url)

        if new_content != content and not args.dry_run:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
            files_changed += 1
        elif new_content != content:
            files_changed += 1

    # --- Resumen ---
    print(f"Detectadas: {len(detected)} imagen(es) externa(s) en {len(files)} archivo(s) escaneados.")
    print(f"Ya migradas de antes: {len(already_migrated)}")
    print(f"Descargadas en esta ejecución: {len(newly_downloaded)}")
    if newly_downloaded:
        for url, filename in newly_downloaded:
            print(f"  - {filename}  <-  {url}")
    print(f"Archivos relinkados: {files_changed}" + (" (dry-run, no se escribió nada)" if args.dry_run else ""))

    if failed:
        print(f"\nFALLARON {len(failed)} descarga(s) (el resto del proceso se completó igual):")
        for url, error in failed:
            print(f"  - {url}  ->  {error}")
        print("Esas URLs externas se han dejado tal cual en el HTML/CSS (no se relinkaron) para no dejar imágenes rotas apuntando a un archivo local inexistente.")


if __name__ == "__main__":
    main()
