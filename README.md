# Global Nautica: propuesta de rediseño web

Propuesta de nuevo diseño para [www.globalnautica.com](http://www.globalnautica.com), pensada para iterar sobre ella.
Es una web estática (HTML + CSS + JS, sin dependencias ni build) que se puede alojar en cualquier hosting, incluido el actual de IONOS (1&1).

## Verla en local

```powershell
python -m http.server 8080
```

Después abre <http://localhost:8080>. En Windows también puedes hacer doble clic en `serve.bat`.

## Estructura y cómo editar

Las páginas se **generan** con `build.py`: el contenido de cada página está en `_src/` y la cabecera, el pie y las etiquetas SEO son comunes.

1. Edita el contenido en `_src/` (HTML normal con unos metadatos arriba: título, descripción, URL y su equivalente en el otro idioma).
2. Ejecuta `python build.py`.
3. No edites a mano los `index.html` generados: se sobrescriben.

```
_src/                         Contenido de cada página (esto es lo que se edita)
  index.html                  Portada en español
  fiscalidad-nautica.html     -> /fiscalidad-nautica/
  gestoria-nautica.html       -> /gestoria-nautica/
  servicios-tecnicos.html     -> /servicios-tecnicos/
  en/                         Versión en inglés (/en/, /en/yacht-tax-vat-spain/...)
build.py                      Genera las páginas, el sitemap.xml y las etiquetas hreflang
aviso-legal.html              Aviso legal (editado a mano)
.htaccess                     Redirecciones 301 para el hosting de IONOS (https, www y URLs antiguas)
robots.txt, sitemap.xml       Para los buscadores
assets/                       CSS, JS e imágenes
```

## SEO

Ya hecho en el código:
- Una página por servicio, con texto propio, preguntas frecuentes y botón de contacto.
- Versión en inglés, con `hreflang` entre cada pareja de páginas.
- Títulos y descripciones orientados a búsquedas reales (gestoría náutica Estepona, IEDMT, importación temporal, yacht registration Spain, marine surveyor Costa del Sol...).
- Datos estructurados schema.org: empresa local, servicios y ruta de navegación (breadcrumbs).
- URL canónica, `sitemap.xml` y `robots.txt`.
- `.htaccess` que fuerza `https://www` y redirige (301) las páginas antiguas (`2.html`, `5.html`...) a las nuevas.

**Mientras sea una propuesta**, todas las páginas llevan `noindex`. Para publicar en globalnautica.com, pon `NOINDEX = False` en `build.py` y vuelve a ejecutarlo.

Lo que hay que hacer fuera del código:
- [ ] **Google Business Profile**: crear o reclamar la ficha de Global Nautica en Estepona, con categoría, fotos, horario y web, y pedir reseñas a los clientes.
- [ ] **globalnautica.es**: en el panel de IONOS, redirigir el dominio (301) a `https://www.globalnautica.com` en lugar de mantener la página de "visite globalnautica.com".
- [ ] **Google Search Console**: dar de alta el dominio y enviar `sitemap.xml`.
- [ ] **Directorios** (Iberinform, elEconomista, etc.): corregir la web (.com) y la actividad (aparece el CNAE 8553, de autoescuelas).
- [ ] **Yachting Pages** y directorios náuticos: darse de alta.

## Qué cambia respecto a la web actual

| Web actual | Propuesta |
|---|---|
| Plantilla de 1&1 Editor Web con maquetación en tablas y `<font>` | HTML semántico y CSS moderno |
| No se adapta al móvil | Responsive, con menú móvil |
| Siete páginas sueltas con poco contenido cada una | Portada-resumen y una página completa por servicio, en español e inglés |
| Servicios con una lista y poco más | Cada servicio explicado, con preguntas frecuentes y botón de contacto |
| No hay llamadas a la acción | Botones de llamar, email y WhatsApp siempre a mano |
| Sin SEO estructurado | Título, descripción y Open Graph mejorados, y datos `schema.org` de empresa local |
| La nota del MOVES III aparece en "Enlaces" | Se mueve al pie, donde suele ir la publicidad obligatoria de las ayudas |
| Google Maps solo como imagen enlazada | El mapa se carga al pulsar un botón (sin cookies de terceros hasta entonces) |

**Identidad:** se mantiene el azul marino del logo y el sello de la vela. Se añade un acento latón/cabo sacado de las fotos y se usan las tipografías Fraunces (titulares) e Inter (texto).

## Pendiente o para decidir

- [ ] **Fotos:** las actuales son pequeñas (510 px). Harían falta fotos propias en alta resolución: oficina, puerto de Estepona, equipo, barcos de clientes.
- [ ] **Logo:** solo existe en JPG de 598×110. Pedir el original en vectorial (SVG/AI/PDF).
- [ ] **Aviso legal:** cita la LOPD 15/1999, que está derogada. Hay que actualizarlo a RGPD + LOPDGDD 3/2018 y añadir política de privacidad y de cookies.
- [ ] **WhatsApp:** el botón usa el móvil +34 637 742 113. Confirmar que ese número tiene WhatsApp.
- [ ] **Atención en inglés:** las páginas de servicio dicen "Atención en español e inglés". Confirmar que es así.
- [ ] **Textos de las páginas de servicio:** revisar las explicaciones fiscales y administrativas (IEDMT, importación temporal, Lista 6ª/7ª, ITB). Están redactadas de forma general, pero conviene que las valide alguien del oficio.
- [ ] **Guías prácticas:** publicar artículos sobre lo que preguntan los clientes (cuánto cuesta matricular un barco, renovar la importación temporal...).
- [ ] **Formulario de contacto:** ahora mismo es `mailto:`. Se podría usar Formspree, Netlify Forms o un PHP en el hosting.
- [ ] **Bloque "Cómo trabajamos":** el texto es nuevo, no viene de la web actual. Validarlo con la empresa.
- [ ] **Contenido nuevo:** testimonios, logos de marinas o clientes, preguntas frecuentes (IEDMT, importación temporal...).
