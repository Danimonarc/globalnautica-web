"""Genera las páginas de la web a partir de los fragmentos de _src/.

Cada archivo de _src/ contiene solo el contenido de <main> y una cabecera
de metadatos entre <!-- -->. Este script le añade la plantilla común
(cabecera, pie, SEO, hreflang) y escribe el HTML final en su carpeta.

    python build.py

Marcadores disponibles en los fragmentos:
    {{R}}     prefijo relativo hasta la raíz del sitio ("", "../", "../../")
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "_src"
SITE = "https://www.globalnautica.com/"

# Mientras la web sea una propuesta alojada fuera de globalnautica.com,
# no queremos que Google la indexe. Poner a False al publicar en el dominio real.
NOINDEX = True

T = {
    "es": {
        "skip": "Saltar al contenido",
        "menu": "Abrir menú",
        "home_label": "Global Nautica, inicio",
        "nav": [("nosotros", "Quiénes somos"), ("servicios", "Servicios"), ("recursos", "Recursos"), ("contacto", "Contacto")],
        "services": [("fiscalidad-nautica/", "Fiscalidad náutica"), ("gestoria-nautica/", "Gestoría náutica"), ("servicios-tecnicos/", "Servicios técnicos")],
        "home": "",
        "switch": ("EN", "English", "en"),
        "tag": "Asesoría náutica integral en la Costa del Sol desde 1999.",
        "footer_services": "Servicios",
        "footer_company": "Empresa",
        "legal": "Aviso legal y privacidad",
        "funding": "Global Nautica ha recibido una ayuda de la Unión Europea con cargo al Fondo NextGenerationEU, en el marco del Plan de Recuperación, Transformación y Resiliencia, para la adquisición de vehículo eléctrico enchufable dentro del Programa de incentivos a la movilidad eficiente y sostenible (Programa MOVES III Andalucía) del Ministerio para la Transición Ecológica y el Reto Demográfico, gestionado por la Junta de Andalucía, a través de la Agencia Andaluza de la Energía.",
        "locale": "es_ES",
    },
    "en": {
        "skip": "Skip to content",
        "menu": "Open menu",
        "home_label": "Global Nautica, home",
        "nav": [("about", "About us"), ("services", "Services"), ("resources", "Resources"), ("contact", "Contact")],
        "services": [("en/yacht-tax-vat-spain/", "Yacht tax & VAT"), ("en/yacht-registration-spain/", "Yacht registration"), ("en/marine-surveyor-costa-del-sol/", "Surveys & technical")],
        "home": "en/",
        "switch": ("ES", "Español", "es"),
        "tag": "Full-service nautical consultancy on the Costa del Sol since 1999.",
        "footer_services": "Services",
        "footer_company": "Company",
        "legal": "Legal notice (Spanish)",
        "funding": "Global Nautica has received European Union funding from the NextGenerationEU Fund, under the Recovery, Transformation and Resilience Plan, for the purchase of a plug-in electric vehicle within the MOVES III Andalucía programme of the Spanish Ministry for the Ecological Transition and the Demographic Challenge, managed by the Junta de Andalucía through the Andalusian Energy Agency.",
        "locale": "en_GB",
    },
}

PHONE_SVG = '<svg aria-hidden="true" viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M6.6 10.8a15.2 15.2 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>'

BUSINESS = {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "@id": SITE + "#empresa",
    "name": "Global Nautica",
    "legalName": "Global Nautica Marine SL",
    "foundingDate": "1999",
    "url": SITE,
    "logo": SITE + "assets/img/logo-original.jpg",
    "image": SITE + "assets/img/cabos-cubierta.jpg",
    "email": "info@globalnautica.com",
    "telephone": "+34952808606",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "Avda. del Carmen nº9, Edif. Puertosol, 1º Of. 27",
        "postalCode": "29680",
        "addressLocality": "Estepona",
        "addressRegion": "Málaga",
        "addressCountry": "ES",
    },
    "geo": {"@type": "GeoCoordinates", "latitude": 36.4170574, "longitude": -5.1562526},
    "areaServed": ["Costa del Sol", "Andalucía", "España"],
    "knowsLanguage": ["es", "en"],
}


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"<!--(.*?)-->\s*", text, re.S)
    meta = {}
    for line in m.group(1).strip().splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    meta["body"] = text[m.end():]
    return meta


def rel(depth):
    return "../" * depth


def depth_of(path):
    return path.count("/")


def link(r, target):
    """Enlace relativo a una ruta del sitio; la raíz se convierte en './'."""
    return (r + target) or "./"


def layout(p):
    t = T[p["lang"]]
    path = p["path"]
    r = rel(depth_of(path))
    is_home = path == t["home"]
    home = link(r, t["home"])
    anchor = (lambda a: "#" + a) if is_home else (lambda a: home + "#" + a)

    canonical = SITE + path
    alt_lang = t["switch"][2]
    alternates = [(p["lang"], canonical)]
    if "alt" in p:
        alternates.append((alt_lang, SITE + p["alt"]))
    hreflang = "\n".join(f'  <link rel="alternate" hreflang="{lg}" href="{u}">' for lg, u in alternates)
    es_url = dict(alternates).get("es")
    if es_url:
        hreflang += f'\n  <link rel="alternate" hreflang="x-default" href="{es_url}">'

    schema = [BUSINESS]
    if p.get("service"):
        schema.append({
            "@context": "https://schema.org",
            "@type": "Service",
            "name": p["service"],
            "serviceType": p["service"],
            "provider": {"@id": SITE + "#empresa"},
            "areaServed": ["Costa del Sol", "España"],
            "url": canonical,
        })
    if not is_home:
        schema.append({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Global Nautica", "item": SITE + t["home"]},
                {"@type": "ListItem", "position": 2, "name": p.get("service") or p["title"], "item": canonical},
            ],
        })
    ld = "\n".join(
        f'  <script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schema
    )

    nav = "\n".join(f'          <li><a href="{anchor(a)}">{label}</a></li>' for a, label in t["nav"])
    switch_href = link(r, p["alt"]) if "alt" in p else link(r, T[alt_lang]["home"])
    switch = (
        f'<a class="lang-switch" href="{switch_href}" hreflang="{alt_lang}" lang="{alt_lang}" '
        f'title="{t["switch"][1]}">{t["switch"][0]}</a>'
    )
    services = "\n".join(f'          <li><a href="{link(r, u)}">{label}</a></li>' for u, label in t["services"])
    company = "\n".join(f'          <li><a href="{anchor(a)}">{label}</a></li>' for a, label in t["nav"] if a not in ("servicios", "services"))
    robots = '  <meta name="robots" content="noindex">\n' if NOINDEX else ""
    image = SITE + p.get("image", "assets/img/cabos-cubierta.jpg")
    body = p["body"].replace("{{R}}", r)

    return f"""<!doctype html>
<html lang="{p['lang']}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{p['title']}</title>
  <meta name="description" content="{p['description']}">
{robots}  <link rel="canonical" href="{canonical}">
{hreflang}
  <meta name="theme-color" content="#0b2a5e">
  <link rel="icon" href="{r}assets/img/favicon.svg" type="image/svg+xml">

  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Global Nautica">
  <meta property="og:locale" content="{t['locale']}">
  <meta property="og:title" content="{p['title']}">
  <meta property="og:description" content="{p['description']}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{image}">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{r}assets/css/styles.css">
  <script>document.documentElement.classList.add("js");</script>
{ld}
</head>
<body>
  <a class="skip-link" href="#contenido">{t['skip']}</a>

  <!-- Archivo generado por build.py a partir de _src/. No editar a mano. -->
  <header class="site-header" data-header>
    <div class="container header-inner">
      <a href="{home if not is_home else '#inicio'}" class="brand" aria-label="{t['home_label']}">
        <span class="brand-mark"><img src="{r}assets/img/logo-original.jpg" alt="" width="598" height="110"></span>
        <span class="brand-name">Global Nautica</span>
      </a>

      <button class="nav-toggle" aria-expanded="false" aria-controls="main-nav" data-nav-toggle>
        <span class="sr-only">{t['menu']}</span>
        <span class="nav-toggle-bar"></span>
      </button>

      <nav id="main-nav" class="main-nav" data-nav>
        <ul>
{nav}
        </ul>
        {switch}
        <a class="btn btn-small btn-brass" href="tel:+34952808606">
          {PHONE_SVG}
          952 808 606
        </a>
      </nav>
    </div>
  </header>

  <main id="contenido">
{body.rstrip()}
  </main>

  <footer class="site-footer">
    <div class="container footer-grid">
      <div>
        <a href="{home}" class="brand brand-footer">
          <span class="brand-mark"><img src="{r}assets/img/logo-original.jpg" alt="" width="598" height="110"></span>
          <span class="brand-name">Global Nautica</span>
        </a>
        <p class="footer-tag">{t['tag']}</p>
      </div>
      <nav aria-label="{t['footer_services']}">
        <p class="footer-title">{t['footer_services']}</p>
        <ul class="footer-links">
{services}
        </ul>
      </nav>
      <nav aria-label="{t['footer_company']}">
        <p class="footer-title">{t['footer_company']}</p>
        <ul class="footer-links">
{company}
          <li><a href="{r}aviso-legal.html">{t['legal']}</a></li>
        </ul>
      </nav>
      <div class="footer-contact">
        <a href="tel:+34952808606">+34 952 808 606</a><br>
        <a href="tel:+34637742113">+34 637 742 113</a><br>
        <a href="mailto:info@globalnautica.com">info@globalnautica.com</a><br>
        Avda. del Carmen 9, Edif. Puertosol<br>
        29680 Estepona (Málaga)
      </div>
    </div>

    <div class="container funding">
      <img src="{r}assets/img/logos-moves-iii.png" alt="Ministerio para la Transición Ecológica, IDAE, MOVES III, Junta de Andalucía, Agencia Andaluza de la Energía" width="944" height="63" loading="lazy">
      <p>{t['funding']}</p>
    </div>

    <div class="container footer-bottom">
      <span>© <span data-year>2026</span> Global Nautica Marine SL · Estepona (Málaga), España</span>
      {switch}
    </div>
  </footer>

  <script src="{r}assets/js/main.js" defer></script>
</body>
</html>
"""


def sitemap(pages):
    rows = []
    for p in pages:
        alts = [(p["lang"], SITE + p["path"])]
        if "alt" in p:
            alts.append(("en" if p["lang"] == "es" else "es", SITE + p["alt"]))
        links = "".join(
            f'\n    <xhtml:link rel="alternate" hreflang="{lg}" href="{u}"/>' for lg, u in alts
        )
        rows.append(f"  <url>\n    <loc>{SITE + p['path']}</loc>{links}\n  </url>")
    rows.append(f"  <url>\n    <loc>{SITE}aviso-legal.html</loc>\n  </url>")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(rows) + "\n</urlset>\n"
    )


def main():
    pages = [parse(f) for f in sorted(SRC.rglob("*.html"))]
    for p in pages:
        out = ROOT / p["path"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(layout(p), encoding="utf-8", newline="\n")
        print("  ", out.relative_to(ROOT))
    (ROOT / "sitemap.xml").write_text(sitemap(pages), encoding="utf-8", newline="\n")
    print("   sitemap.xml")


if __name__ == "__main__":
    main()
