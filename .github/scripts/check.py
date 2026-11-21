"""Comprobaciones antes de publicar. Termina con error (código 1) si algo falla.

    python .github/scripts/check.py

1. El HTML guardado en el repositorio es el que genera `python build.py` (nadie ha editado
   _src/ sin regenerar, ni hay páginas sobrantes).
2. Ningún enlace interno roto (páginas, imágenes, CSS, JS y anclas #…).
3. Todos los datos estructurados (JSON-LD) son JSON válido.
4. Cada página indexable tiene título, descripción y URL canónica, sin repetirse entre páginas.
5. Las parejas hreflang (español/inglés) existen y se enlazan en los dos sentidos.
6. El sha256 del script en línea de la cabecera coincide con el de la política de seguridad
   de .htaccess (si no, el navegador bloquearía ese script).
Solo usa la biblioteca estándar de Python.
"""
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
SITE = "https://www.globalnautica.com/"
IGNORAR = {".git", "_src", ".github", "publicar", "node_modules"}
errores = []


def error(donde, mensaje):
    errores.append(f"{donde}: {mensaje}")


def paginas(base):
    """Páginas HTML generadas de un árbol: */index.html y 404.html (sin el código fuente)."""
    out = []
    for f in sorted(base.rglob("*.html")):
        rel = f.relative_to(base)
        if rel.parts[0] in IGNORAR:
            continue
        out.append(rel)
    return out


class Pagina(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.enlaces, self.ids, self.metas, self.links, self.json_ld, self.scripts = [], set(), {}, [], [], []
        self.title, self._en, self._buf = "", None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for k in ("href", "src"):
            if tag != "link" and k in a:
                self.enlaces.append(a[k])
            elif tag == "link" and k == "href" and a.get("rel") == "stylesheet":
                self.enlaces.append(a[k])
        if tag in ("img", "source") and a.get("srcset"):
            self.enlaces.append(a["srcset"].split()[0])
        if tag == "link" and a.get("rel") in ("canonical", "alternate"):
            self.links.append(a)
        if tag == "meta":
            self.metas[a.get("name") or a.get("property")] = a.get("content")
        if tag == "title":
            self._en = "title"
        if tag == "script":
            self._en = "ld" if a.get("type") == "application/ld+json" else ("src" if "src" in a else "inline")
        self._buf = []

    def handle_data(self, data):
        self._buf.append(data)

    def handle_endtag(self, tag):
        texto = "".join(self._buf)
        if tag == "title":
            self.title = texto.strip()
        elif tag == "script" and self._en == "ld":
            self.json_ld.append(texto)
        elif tag == "script" and self._en == "inline":
            self.scripts.append(texto)
        self._en = None


def leer(ruta):
    p = Pagina()
    p.feed(ruta.read_text(encoding="utf-8"))
    return p


def comprobar_regenerado():
    """1. El HTML del repositorio coincide con el que genera build.py."""
    with tempfile.TemporaryDirectory() as tmp:
        copia = Path(tmp) / "web"
        shutil.copytree(ROOT, copia, ignore=shutil.ignore_patterns(".git", "publicar", "node_modules"))
        env = {**os.environ, "NOINDEX": "1"}
        env.pop("DRAFTS", None)
        env.pop("GUIDES", None)
        r = subprocess.run([sys.executable, "build.py"], cwd=copia, env=env, capture_output=True, text=True)
        if r.returncode != 0:
            error("build.py", "falla al generar la web:\n" + (r.stderr or r.stdout)[-600:])
            return
        repo, gen = set(paginas(ROOT)), set(paginas(copia))
        for f in sorted(repo - gen):
            error(str(f), "está en el repositorio pero build.py ya no la genera (borrarla)")
        for f in sorted(gen - repo):
            error(str(f), "build.py la genera pero no está en el repositorio (falta ejecutar build.py y guardar el resultado)")
        quitar = lambda t: re.sub(r"[ \t]*<lastmod>[^<]*</lastmod>\n?", "", t)  # lastmod depende del historial de git
        for f in sorted(repo & gen) + [Path("sitemap.xml")]:
            a, b = (ROOT / f).read_text(encoding="utf-8"), (copia / f).read_text(encoding="utf-8")
            if f.name == "sitemap.xml":
                a, b = quitar(a), quitar(b)
            if a != b:
                error(str(f), "no coincide con lo que genera build.py (hay que ejecutar `python build.py` y guardar el resultado)")


def comprobar_enlaces(datos):
    """2. Enlaces internos."""
    for rel, p in datos.items():
        for href in p.enlaces:
            if re.match(r"^(mailto:|tel:|data:|javascript:|https?://(?!www\.globalnautica\.com))", href):
                continue
            href = href.replace(SITE, "/") if href.startswith(SITE) else href
            u = urlsplit(href)
            if not u.path:
                destino = rel  # solo ancla (#contenido)
            else:
                ruta = unquote(u.path)
                base = ROOT if ruta.startswith("/") else (ROOT / rel).parent
                destino = (base / ruta.lstrip("/")).resolve()
                if ruta.endswith("/") or destino.is_dir():
                    destino = destino / "index.html"
                if not destino.exists():
                    error(str(rel), f"enlace roto → {href}")
                    continue
                destino = destino.relative_to(ROOT)
            if u.fragment and destino.suffix == ".html" and destino in datos and u.fragment not in datos[destino].ids:
                error(str(rel), f"el ancla #{u.fragment} no existe en {destino}")


def comprobar_metadatos(datos):
    """3. JSON-LD; 4. metadatos; 5. hreflang."""
    titulos, descripciones, canonicas = {}, {}, {}
    for rel, p in datos.items():
        for i, bloque in enumerate(p.json_ld, 1):
            try:
                json.loads(bloque)
            except ValueError as e:
                error(str(rel), f"el bloque JSON-LD {i} no es JSON válido ({e})")
        if "noindex" in (p.metas.get("robots") or "") and not any(l.get("rel") == "canonical" for l in p.links):
            pass  # las páginas sin canonical (404) no se comprueban más
        canon = next((l["href"] for l in p.links if l.get("rel") == "canonical"), None)
        if canon is None:
            if rel.name != "404.html":
                error(str(rel), "falta <link rel=\"canonical\">")
            continue
        canonicas[canon] = rel
        if not p.title:
            error(str(rel), "falta el <title>")
        if not p.metas.get("description"):
            error(str(rel), "falta la meta description")
        if not p.metas.get("og:image"):
            error(str(rel), "falta og:image")
        for valor, tabla, nombre in ((p.title, titulos, "título"), (p.metas.get("description"), descripciones, "descripción")):
            if valor in tabla:
                error(str(rel), f"el {nombre} está repetido en {tabla[valor]}")
            tabla[valor] = rel
    for rel, p in datos.items():
        canon = next((l["href"] for l in p.links if l.get("rel") == "canonical"), None)
        for l in p.links:
            if l.get("rel") != "alternate" or l.get("hreflang") in (None, "x-default") or l["href"] == canon:
                continue
            otro = canonicas.get(l["href"])
            if otro is None:
                error(str(rel), f"hreflang {l['hreflang']} apunta a una página que no existe: {l['href']}")
                continue
            vuelta = [x.get("href") for x in datos[otro].links if x.get("rel") == "alternate" and x.get("hreflang") not in (None, "x-default")]
            if canon not in vuelta:
                error(str(rel), f"hreflang sin reciprocidad: {otro} no enlaza de vuelta a esta página")


def comprobar_csp(datos):
    """6. Huella del script en línea frente a la política de .htaccess."""
    ht = (ROOT / ".htaccess").read_text(encoding="utf-8")
    permitidas = set(re.findall(r"'sha256-([A-Za-z0-9+/=]+)'", ht))
    for rel, p in datos.items():
        for js in p.scripts:
            huella = base64.b64encode(hashlib.sha256(js.encode("utf-8")).digest()).decode()
            if huella not in permitidas:
                error(str(rel), f"el script en línea no está en la política de .htaccess; hay que poner 'sha256-{huella}'")


def main():
    datos = {rel: leer(ROOT / rel) for rel in paginas(ROOT)}
    if not datos:
        error("repositorio", "no hay páginas HTML generadas")
    comprobar_regenerado()
    comprobar_enlaces(datos)
    comprobar_metadatos(datos)
    comprobar_csp(datos)
    if errores:
        print(f"✗ {len(errores)} problema(s):")
        for e in errores:
            print("  -", e)
        sys.exit(1)
    print(f"✓ Todo correcto: {len(datos)} páginas, enlaces, JSON-LD, metadatos, hreflang y política de seguridad.")


if __name__ == "__main__":
    main()
