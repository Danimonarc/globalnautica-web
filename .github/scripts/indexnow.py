"""Avisa a Bing y otros buscadores (IndexNow) de las páginas que han cambiado.

    python .github/scripts/indexnow.py [COMMIT_ANTERIOR] [--dry-run]

Con un commit anterior, avisa solo de las páginas cambiadas desde entonces; sin él (o
si no se puede comparar), de todas las del sitemap.xml. Nunca falla: si el servicio no
responde, lo escribe en el registro y termina bien, para no detener la publicación.
Google no usa IndexNow: para Google vale el sitemap enviado en Search Console.
"""
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOST = "www.globalnautica.com"
SITE = f"https://{HOST}/"
KEY = "d5e2c2ee363eb2463d86370c2a3326f9"  # igual que el nombre y el contenido de <clave>.txt en la raíz
ENDPOINT = "https://api.indexnow.org/indexnow"
NO_PAGINAS = ("_src/", ".github/", "publicar/")


def todas_las_urls():
    return re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))


def urls_cambiadas(antes):
    """URL de las páginas cuyo HTML ha cambiado entre `antes` y HEAD."""
    out = subprocess.run(["git", "diff", "--name-only", antes, "HEAD"], cwd=ROOT, capture_output=True, text=True)
    if out.returncode != 0:
        return None
    publicas = set(todas_las_urls())
    urls = []
    for f in out.stdout.split():
        if f.startswith(NO_PAGINAS) or not f.endswith("index.html"):
            continue
        carpeta = f[: -len("index.html")]
        url = SITE + carpeta
        if url in publicas:
            urls.append(url)
    return sorted(set(urls))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    antes = args[0] if args else ""
    urls = None
    if antes and not set(antes) <= {"0"}:
        urls = urls_cambiadas(antes)
    if urls is None:
        urls = todas_las_urls()
    if not urls:
        print("IndexNow: ninguna página ha cambiado, no se avisa.")
        return
    print(f"IndexNow: {len(urls)} URL")
    for u in urls:
        print("  ", u)
    if "--dry-run" in sys.argv:
        return
    cuerpo = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"{SITE}{KEY}.txt", "urlList": urls}).encode()
    req = urllib.request.Request(ENDPOINT, cuerpo, {"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            print(f"IndexNow: respuesta {r.status}")
    except Exception as e:  # el aviso es opcional: nunca debe detener la publicación
        print(f"IndexNow: no se pudo avisar ({e}); la publicación sigue adelante.")


if __name__ == "__main__":
    main()
