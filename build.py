"""Genera las páginas de la web a partir de los fragmentos de _src/.

Cada archivo de _src/ contiene solo el contenido de <main> y una cabecera
de metadatos entre <!-- -->. Este script le añade la plantilla común
(cabecera, pie, SEO, hreflang) y escribe el HTML final en su carpeta.

    python build.py

Marcadores disponibles en los fragmentos:
    {{R}}              prefijo relativo hasta la raíz del sitio ("", "../", "../../")
    {{GUIDES}}         tarjetas de todas las guías del idioma de la página
    {{GUIDES_LATEST}}  tarjetas de las tres guías más recientes

Los artículos (type: article) solo contienen el texto: la cabecera, el
contacto lateral y las guías relacionadas los añade article_body().
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
        "lang_group": "Idioma",
        "suggest": ("Esta página también está disponible en español.", "Ver en español", "Cerrar"),
        "country": "España",
        "funding_alt": "Ministerio para la Transición Ecológica y el Reto Demográfico, IDAE, MOVES III, Junta de Andalucía, Agencia Andaluza de la Energía",
        "tag": "Asesoría náutica integral en la Costa del Sol desde 1999.",
        "footer_services": "Servicios",
        "footer_company": "Empresa",
        "legal": [("aviso-legal/", "Aviso legal"), ("aviso-legal/#privacidad", "Privacidad"), ("aviso-legal/#cookies", "Cookies")],
        "funding": "Global Nautica ha recibido una ayuda de la Unión Europea con cargo al Fondo NextGenerationEU, en el marco del Plan de Recuperación, Transformación y Resiliencia, para la adquisición de vehículo eléctrico enchufable dentro del Programa de incentivos a la movilidad eficiente y sostenible (Programa MOVES III Andalucía) del Ministerio para la Transición Ecológica y el Reto Demográfico, gestionado por la Junta de Andalucía, a través de la Agencia Andaluza de la Energía.",
        "locale": "es_ES",
        "guides": ("guias/", "Guías"),
        "months": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                   "septiembre", "octubre", "noviembre", "diciembre"],
        "date_fmt": "{d} de {m} de {y}",
        "a": {
            "home": "Inicio",
            "updated": "Actualizado el",
            "read": "min de lectura",
            "author": "Equipo de Global Nautica",
            "read_more": "Leer guía",
            "disclaimer": "Esta guía tiene carácter informativo y general, y refleja la normativa a la fecha de actualización. Cada caso requiere un estudio individual: consúltenos antes de tomar decisiones.",
            "side_eyebrow": "¿Le ayudamos?",
            "side_title": "Estudiamos su caso",
            "side_text": "Desde 1999 resolvemos estas gestiones en Estepona para clientes de toda España.",
            "subject": "Consulta desde la guía",
            "service_label": "Servicio relacionado",
            "more": "Más guías",
            "more_title": "Siga leyendo",
            "cta_title": "¿Tiene dudas sobre su caso?",
            "cta_text": "Teléfono, email o WhatsApp. También puede visitarnos en el edificio Puertosol, en Estepona.",
            "email_btn": "Escribir un email",
        },
    },
    "en": {
        "skip": "Skip to content",
        "menu": "Open menu",
        "home_label": "Global Nautica, home",
        "nav": [("about", "About us"), ("services", "Services"), ("resources", "Resources"), ("contact", "Contact")],
        "services": [("en/yacht-tax-vat-spain/", "Yacht tax & VAT"), ("en/yacht-registration-spain/", "Yacht registration"), ("en/marine-surveyor-costa-del-sol/", "Surveys & technical")],
        "home": "en/",
        "switch": ("ES", "Español", "es"),
        "lang_group": "Language",
        "suggest": ("This page is also available in English.", "View in English", "Close"),
        "country": "Spain",
        "funding_alt": "Spanish Ministry for the Ecological Transition, IDAE, MOVES III, Junta de Andalucía, Andalusian Energy Agency",
        "tag": "Full-service nautical consultancy on the Costa del Sol since 1999.",
        "footer_services": "Services",
        "footer_company": "Company",
        "legal": [("en/legal-notice/", "Legal notice"), ("en/legal-notice/#privacy", "Privacy"), ("en/legal-notice/#cookies", "Cookies")],
        "funding": "Global Nautica has received European Union funding from the NextGenerationEU Fund, under the Recovery, Transformation and Resilience Plan, for the purchase of a plug-in electric vehicle within the MOVES III Andalucía programme of the Spanish Ministry for the Ecological Transition and the Demographic Challenge, managed by the Junta de Andalucía through the Andalusian Energy Agency.",
        "locale": "en_GB",
        "guides": ("en/guides/", "Guides"),
        "months": ["January", "February", "March", "April", "May", "June", "July", "August",
                   "September", "October", "November", "December"],
        "date_fmt": "{d} {m} {y}",
        "a": {
            "home": "Home",
            "updated": "Updated",
            "read": "min read",
            "author": "Global Nautica team",
            "read_more": "Read guide",
            "disclaimer": "This guide is general information and reflects the rules in force on the date it was updated. Every case needs individual advice: talk to us before making decisions.",
            "side_eyebrow": "Need help?",
            "side_title": "We'll review your case",
            "side_text": "Since 1999 we have handled these procedures from Estepona for owners from all over the world.",
            "subject": "Enquiry from the guide",
            "service_label": "Related service",
            "more": "More guides",
            "more_title": "Keep reading",
            "cta_title": "Questions about your case?",
            "cta_text": "Phone, email or WhatsApp. You are also welcome at our office in the Puertosol building, Estepona.",
            "email_btn": "Send an email",
        },
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


def fmt_date(iso, lang):
    t = T[lang]
    y, m, d = (int(x) for x in iso.split("-"))
    return t["date_fmt"].format(d=d, m=t["months"][m - 1], y=y)


def reading_minutes(html):
    words = len(re.sub(r"<[^>]+>", " ", html).split())
    return max(3, round(words / 200))


def guides_of(pages, lang):
    """Artículos de un idioma, del más reciente al más antiguo."""
    arts = [g for g in pages if g.get("type") == "article" and g["lang"] == lang]
    # Más recientes primero; a igual fecha, por el campo opcional "order" (1 = primero)
    arts.sort(key=lambda g: int(g.get("order", 99)))
    return sorted(arts, key=lambda g: g["date"], reverse=True)


def guide_cards(guides, r, lang):
    a = T[lang]["a"]
    cards = []
    for g in guides:
        cards.append(
            f'          <a class="guide-card" href="{link(r, g["path"])}">\n'
            f'            <span class="guide-cat">{g["category"]}</span>\n'
            f'            <h3>{g["headline"]}</h3>\n'
            f'            <p>{g["summary"]}</p>\n'
            f'            <span class="guide-meta">{reading_minutes(g["body"])} {a["read"]} · {a["read_more"]} →</span>\n'
            f'          </a>'
        )
    return '        <div class="guides-grid">\n' + "\n".join(cards) + "\n        </div>"


def article_body(p, pages, r):
    """Envuelve el texto de un artículo con su cabecera, contacto lateral y guías relacionadas."""
    lang = p["lang"]
    t = T[lang]
    a = t["a"]
    guides_path, guides_label = t["guides"]
    service_label = dict(t["services"]).get(p.get("topic_service", ""), "")
    service_link = (
        f'\n          <a class="side-service" href="{link(r, p["topic_service"])}">{a["service_label"]}: <strong>{service_label}</strong> →</a>'
        if service_label else ""
    )
    others = [g for g in guides_of(pages, lang) if g["path"] != p["path"]][:3]
    subject = a["subject"].replace(" ", "%20")
    return f"""    <section class="page-hero article-hero">
      <div class="container">
        <nav class="breadcrumb" aria-label="{'Ruta' if lang == 'es' else 'Breadcrumb'}"><a href="{link(r, t['home'])}">{a['home']}</a> <span aria-hidden="true">/</span> <a href="{link(r, guides_path)}">{guides_label}</a> <span aria-hidden="true">/</span> <span>{p['category']}</span></nav>
        <p class="eyebrow">{p['category']}</p>
        <h1>{p['headline']}</h1>
        <p class="lead">{p['summary']}</p>
        <p class="article-meta">{a['updated']} <time datetime="{p['date']}">{fmt_date(p['date'], lang)}</time> · {reading_minutes(p['body'])} {a['read']} · {a['author']}</p>
      </div>
    </section>

    <section class="section">
      <div class="container article-grid">
        <article class="prose">
{p['body'].rstrip()}
          <p class="article-disclaimer">{a['disclaimer']}</p>
        </article>

        <aside class="side-card" aria-label="{a['side_eyebrow']}">
          <p class="eyebrow">{a['side_eyebrow']}</p>
          <p class="side-title">{a['side_title']}</p>
          <p>{a['side_text']}</p>
          <a class="btn btn-brass" href="mailto:info@globalnautica.com?subject={subject}">{a['email_btn']}</a>
          <a class="btn btn-ghost-dark" href="https://wa.me/34637742113" target="_blank" rel="noopener">WhatsApp</a>
          <a class="btn btn-ghost-dark" href="tel:+34952808606">+34 952 808 606</a>{service_link}
        </aside>
      </div>
    </section>

    <section class="section section-tint">
      <div class="container">
        <header class="section-head">
          <p class="eyebrow">{a['more']}</p>
          <h2>{a['more_title']}</h2>
        </header>
{guide_cards(others, r, lang)}
      </div>
    </section>

    <section class="cta-band">
      <div class="container cta-inner">
        <div>
          <h2>{a['cta_title']}</h2>
          <p>{a['cta_text']}</p>
        </div>
        <div class="cta-actions">
          <a class="btn btn-brass" href="tel:+34952808606">+34 952 808 606</a>
          <a class="btn btn-ghost" href="mailto:info@globalnautica.com">info@globalnautica.com</a>
        </div>
      </div>
    </section>
"""


def layout(p, pages):
    t = T[p["lang"]]
    path = p["path"]
    r = rel(depth_of(path))
    is_article = p.get("type") == "article"
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
    if is_article:
        schema.append({
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": p["headline"],
            "description": p["description"],
            "inLanguage": p["lang"],
            "datePublished": p["date"],
            "dateModified": p.get("modified", p["date"]),
            "author": {"@type": "Organization", "name": "Global Nautica", "url": SITE},
            "publisher": {"@id": SITE + "#empresa"},
            "mainEntityOfPage": canonical,
            "image": SITE + p.get("image", "assets/img/cabos-cubierta.jpg"),
        })
    if not is_home:
        crumbs = [("Global Nautica", SITE + t["home"])]
        if is_article:
            crumbs.append((t["guides"][1], SITE + t["guides"][0]))
        crumbs.append((p.get("headline") or p.get("service") or p["title"], canonical))
        schema.append({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i, "name": name, "item": url}
                for i, (name, url) in enumerate(crumbs, 1)
            ],
        })
    ld = "\n".join(
        f'  <script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schema
    )

    guides_li = f'          <li><a href="{link(r, t["guides"][0])}">{t["guides"][1]}</a></li>'
    nav_items = [f'          <li><a href="{anchor(a)}">{label}</a></li>' for a, label in t["nav"]]
    nav_items.insert(2, guides_li)  # Quiénes somos, Servicios, Guías, Recursos, Contacto
    nav = "\n".join(nav_items)
    switch_href = link(r, p["alt"]) if "alt" in p else link(r, T[alt_lang]["home"])
    # Selector ES | EN: el idioma actual marcado y el otro enlazando a la página equivalente
    hrefs = {p["lang"]: link(r, path), alt_lang: switch_href}
    lang_names = {"es": "Español", "en": "English"}
    links = []
    for lg in ("es", "en"):
        state = ' aria-current="true"' if lg == p["lang"] else f' title="{lang_names[lg]}"'
        links.append(f'<a href="{hrefs[lg]}" hreflang="{lg}" lang="{lg}"{state}>{lg.upper()}</a>')
    switch = f'<div class="lang-select" role="group" aria-label="{t["lang_group"]}">{"".join(links)}</div>'

    # Aviso para quien tiene el navegador en el otro idioma (lo muestra main.js)
    other = T[alt_lang]["suggest"]
    suggest = f"""<div class="lang-suggest" data-lang-suggest="{alt_lang}" lang="{alt_lang}" hidden>
    <div class="container lang-suggest-inner">
      <span>{other[0]}</span>
      <a class="btn btn-small btn-brass" href="{switch_href}" hreflang="{alt_lang}">{other[1]}</a>
      <button type="button" class="lang-suggest-close" data-lang-suggest-close aria-label="{other[2]}">×</button>
    </div>
  </div>"""
    services = "\n".join(f'          <li><a href="{link(r, u)}">{label}</a></li>' for u, label in t["services"]) + "\n" + guides_li
    company = "\n".join(f'          <li><a href="{anchor(a)}">{label}</a></li>' for a, label in t["nav"] if a not in ("servicios", "services"))
    legal = "\n".join(f'          <li><a href="{link(r, u)}">{label}</a></li>' for u, label in t["legal"])
    legal_inline = " · ".join(f'<a href="{link(r, u)}">{label}</a>' for u, label in t["legal"])
    robots = '  <meta name="robots" content="noindex">\n' if NOINDEX else ""
    image = SITE + p.get("image", "assets/img/cabos-cubierta.jpg")
    if is_article:
        body = article_body(p, pages, r)
    else:
        guides = guides_of(pages, p["lang"])
        body = (p["body"]
                .replace("{{GUIDES}}", guide_cards(guides, r, p["lang"]))
                .replace("{{GUIDES_LATEST}}", guide_cards(guides[:3], r, p["lang"])))
    body = body.replace("{{R}}", r)
    og_type = "article" if is_article else "website"

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

  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="Global Nautica">
  <meta property="og:locale" content="{t['locale']}">
  <meta property="og:title" content="{p['title']}">
  <meta property="og:description" content="{p['description']}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{image}">

  <link rel="stylesheet" href="{r}assets/css/fonts.css">
  <link rel="stylesheet" href="{r}assets/css/styles.css">
  <script>document.documentElement.classList.add("js");</script>
{ld}
</head>
<body>
  <a class="skip-link" href="#contenido">{t['skip']}</a>
  {suggest}

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
{legal}
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
      <img src="{r}assets/img/logos-moves-iii.png" alt="{t['funding_alt']}" width="944" height="63" loading="lazy">
      <p>{t['funding']}</p>
    </div>

    <div class="container footer-bottom">
      <span>© <span data-year>2026</span> Global Nautica Marine SL · Estepona (Málaga), {t['country']}</span>
      <span class="footer-legal">{legal_inline}</span>
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
        out.write_text(layout(p, pages), encoding="utf-8", newline="\n")
        print("  ", out.relative_to(ROOT))
    (ROOT / "sitemap.xml").write_text(sitemap(pages), encoding="utf-8", newline="\n")
    print("   sitemap.xml")


if __name__ == "__main__":
    main()
