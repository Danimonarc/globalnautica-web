# Global Nautica: web

Web de Global Nautica, publicada en **<https://www.globalnautica.com>** (hosting de IONOS).
Es una web estática (HTML + CSS + JS, sin dependencias) generada con `build.py`.

| Dónde | Para qué | Indexada en Google |
|---|---|---|
| <https://www.globalnautica.com> | Web real, en el hosting de IONOS. Se actualiza sola al cambiar `main`. | Sí |
| <https://danimonarc.github.io/globalnautica-web/> | Copia de previsualización en GitHub Pages | No (`noindex`) |

**Para cambiar algo de la web:** se edita en `_src/`, se ejecuta `python build.py`, se abre una PR y, al aceptarla en `main`, se publica sola en www.globalnautica.com en un par de minutos (ver [Publicación en IONOS](#publicación-en-ionos)).

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
  consultoria-nautica.html    -> /consultoria-nautica/
  aviso-legal.html            -> /aviso-legal/ (aviso legal, privacidad y cookies)
  guias/                      Guías (artículos) en español -> /guias/...
  en/                         Versión en inglés (/en/, /en/guides/...)
build.py                      Genera las páginas, el sitemap.xml y las etiquetas hreflang
.htaccess                     Redirecciones 301 para el hosting de IONOS (https, www y URLs antiguas)
.github/workflows/            Publicación automática en IONOS (publicar-ionos.yml)
robots.txt, sitemap.xml       Para los buscadores
assets/                       CSS, JS e imágenes
```

## Cómo añadir una guía (artículo)

> Las guías están publicadas (`SHOW_GUIDES = True` en `build.py`). Para ocultarlas todas, ponlo a `False` y ejecuta `python build.py`: dejan de generarse y se quitan sus enlaces (en los fragmentos van entre `<!-- guides -->` y `<!-- /guides -->`).

1. Copia un archivo de `_src/guias/` (o de `_src/en/guides/` para inglés) y cambia los metadatos de arriba:

   ```
   lang: es
   type: article
   path: guias/mi-nueva-guia/                  URL de la guía
   alt: en/guides/my-new-guide/                su versión en el otro idioma
   date: 2026-11-15                            fecha de publicación o actualización
   order: 1                                    opcional: orden entre guías de la misma fecha
   category: Fiscalidad                        etiqueta que se muestra en la tarjeta
   topic_service: fiscalidad-nautica/          página de servicio relacionada
   headline: Título visible (H1)
   summary: Entradilla y texto de la tarjeta
   title: Título para Google (unos 60 caracteres)
   description: Descripción para Google (unos 155 caracteres)
   ```

2. Escribe solo el texto del artículo (párrafos, `<h2>`, listas, preguntas frecuentes...). La cabecera, el contacto lateral, las guías relacionadas, los datos estructurados y el tiempo de lectura los añade `build.py`.
3. Ejecuta `python build.py`. La guía aparece sola en el índice de guías, en la portada (si es de las tres más recientes) y en el `sitemap.xml`.

## Publicación en IONOS

### Cómo funciona

Cada vez que se actualiza `main` (al aceptar una PR o al hacer commit directamente en
`main`), el workflow de GitHub Actions `.github/workflows/publicar-ionos.yml`:

1. genera la web con `NOINDEX=0 python build.py` (sin `noindex`);
2. comprueba que ninguna página lleva `noindex` y, si alguna lo lleva, se para sin publicar;
3. separa los archivos que van al servidor (deja fuera `_src/`, `build.py`, `README.md`,
   `serve.bat` y los archivos de git);
4. los sube por SFTP a la carpeta `/globalnautica-web` del espacio web de IONOS, dejándola
   idéntica a la web generada: lo que ya no exista en la web se borra del servidor.

También se puede lanzar a mano: **Actions → Publicar en IONOS → Run workflow** (rama `main`).
Cada ejecución queda registrada en la pestaña **Actions**, con la lista de archivos subidos.

### Configuración actual

| Pieza | Dónde | Valor |
|---|---|---|
| Carpeta de la web | IONOS → Hosting → Espacio web | `/globalnautica-web` (solo contiene la web; no guardar nada más ahí) |
| Destino del dominio | IONOS → Dominios y SSL → globalnautica.com → ⋮ → Ajustar destino | Espacio web → `/globalnautica-web` |
| Destino de www | IONOS → Dominios y SSL → globalnautica.com → ⋮ → Administrar subdominios → www | Espacio web → `/globalnautica-web` |
| Usuario SFTP | IONOS → Hosting → SFTP y SSH | Usuario dedicado a GitHub |
| Secretos | GitHub → Settings → Secrets and variables → Actions | `IONOS_SFTP_HOST`, `IONOS_SFTP_USER`, `IONOS_SFTP_PASSWORD`, `IONOS_SFTP_DIR` (`/globalnautica-web`) |
| Certificado SSL | IONOS → Dominios y SSL | Activo (imprescindible: `.htaccess` redirige todo a `https://www`) |
| Correo | IONOS | Sin cambios. Publicar la web no toca DNS ni MX |

Los secretos se guardan cifrados en GitHub, no en el repositorio, y no se pueden volver a
leer: para cambiar uno se edita y se pega el valor nuevo. Si faltara alguno, el workflow
termina sin publicar nada (aviso «Faltan los secretos de IONOS»). Por seguridad, el
workflow se niega a publicar si `IONOS_SFTP_DIR` es la raíz `/`.

En la raíz del espacio web hay también otras carpetas de IONOS que no hay que tocar:
`logs` y `wsb5150211301` (la web anterior, hecha con el constructor de IONOS).

### Volver a la web anterior

Si algo fallara, en **Dominios y SSL → globalnautica.com → ⋮ → Ajustar destino** (y lo
mismo en el subdominio www) se puede volver a apuntar el dominio a la web anterior, que
sigue intacta. Para deshacer solo un cambio concreto basta con revertir su PR en GitHub:
al actualizarse `main`, la versión anterior se vuelve a publicar sola.

### Si una publicación sale en rojo

En **Actions → Publicar en IONOS**, abrir la ejecución fallida y mirar el paso en rojo:

- **Subir a IONOS por SFTP:** casi siempre es un secreto mal copiado (servidor, usuario o
  contraseña) o una contraseña cambiada en IONOS. Se corrige el secreto y se pulsa
  **Re-run jobs**.
- **Generar la web sin noindex:** `build.py` ha fallado o alguna página lleva `noindex`.
  Probar en local con `NOINDEX=0 python build.py`.

### Generar en local

- `python build.py` genera la copia de previsualización, con `noindex` (es la que se guarda
  en el repositorio y sirve GitHub Pages).
- `NOINDEX=0 python build.py` genera la versión del dominio real, como hace el workflow.
  No hace falta subirla a mano.

## SEO

Ya hecho en el código:
- Una página por servicio, con texto propio, preguntas frecuentes y botón de contacto.
- Versión en inglés, con `hreflang` entre cada pareja de páginas.
- Títulos y descripciones orientados a búsquedas reales (consultoría náutica Estepona, IEDMT, importación temporal, nautical consultancy Spain...).
- Datos estructurados schema.org: empresa local, servicios y ruta de navegación (breadcrumbs).
- URL canónica, `sitemap.xml` y `robots.txt`.
- `.htaccess` que fuerza `https://www` y redirige (301) las páginas antiguas (`2.html`, `5.html`...) a las nuevas.

Las páginas que se guardan en el repositorio (y la copia de GitHub Pages) llevan `noindex` para que Google no las confunda con la web real. La versión publicada en www.globalnautica.com se genera sin `noindex` (ver [Publicación en IONOS](#publicación-en-ionos)).

Lo que hay que hacer fuera del código:
- [ ] **Google Business Profile**: crear o reclamar la ficha de Global Nautica en Estepona, con categoría, fotos, horario y web, y pedir reseñas a los clientes.
- [ ] **globalnautica.es**: en IONOS, **Dominios y SSL → globalnautica.es → Configurar redirección de dominio**, con redirección 301 a `https://www.globalnautica.com`, en lugar de mantener la página de "visite globalnautica.com".
- [ ] **Google Search Console**: dar de alta el dominio y enviar `https://www.globalnautica.com/sitemap.xml`.
- [ ] **Directorios** (Iberinform, elEconomista, etc.): corregir la web (.com) y la actividad (aparece el CNAE 8553, de autoescuelas).
- [ ] **Yachting Pages** y directorios náuticos: darse de alta.

## Qué cambia respecto a la web anterior

| Web anterior | Web nueva |
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
- [x] **Aviso legal:** actualizado a RGPD + LOPDGDD 3/2018, con política de privacidad y de cookies.
- [ ] **WhatsApp:** el botón usa el móvil +34 637 742 113. Confirmar que ese número tiene WhatsApp.
- [ ] **Atención en inglés:** las páginas de servicio dicen "Atención en español e inglés". Confirmar que es así.
- [ ] **Textos de las páginas de servicio:** revisar las explicaciones fiscales y administrativas (IEDMT, importación temporal, Lista 6ª/7ª, ITB). Están redactadas de forma general, pero conviene que las valide alguien del oficio.
- [x] **Guías prácticas:** publicadas 6 guías en español y 6 en inglés (matriculación, importación temporal, bandera extranjera, compraventa, Lista 6ª/7ª). Conviene que alguien del oficio revise las cifras y plazos, y actualizar la fecha (`date:`) cuando cambie algo.
- [ ] **Más guías:** seguir añadiendo artículos sobre lo que preguntan los clientes.
- [ ] **Workflow de publicación:** GitHub avisa de que `actions/checkout@v4` y `actions/setup-python@v5` usan Node.js 20, que está obsoleto. Funciona, pero conviene subirlos a `actions/checkout@v5` y `actions/setup-python@v6` en `.github/workflows/publicar-ionos.yml`.
- [ ] **Formulario de contacto:** ahora mismo es `mailto:`. Se podría usar Formspree, Netlify Forms o un PHP en el hosting.
- [ ] **Bloque "Cómo trabajamos":** el texto es nuevo, no viene de la web actual. Validarlo con la empresa.
- [ ] **Contenido nuevo:** testimonios, logos de marinas o clientes, preguntas frecuentes (IEDMT, importación temporal...).
