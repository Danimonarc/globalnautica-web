# Global Nautica: propuesta de rediseño web

Propuesta de nuevo diseño para [www.globalnautica.com](http://www.globalnautica.com), pensada para iterar sobre ella.
Es una web estática (HTML + CSS + JS, sin dependencias ni build) que se puede alojar en cualquier hosting, incluido el actual de IONOS (1&1).

## Verla en local

```powershell
python -m http.server 8080
```

Después abre <http://localhost:8080>. En Windows también puedes hacer doble clic en `serve.bat`.

## Estructura

```
index.html            Página principal (one-page): hero, quiénes somos, servicios, cómo trabajamos, enlaces, contacto
aviso-legal.html      Aviso legal (texto original, pendiente de actualizar)
assets/css/styles.css Estilos (las variables de color y tipografía están arriba, en :root)
assets/js/main.js     Menú móvil, pestañas de servicios, mapa bajo demanda, animaciones
assets/img/           Imágenes reutilizadas de la web actual
```

## Qué cambia respecto a la web actual

| Web actual | Propuesta |
|---|---|
| Plantilla de 1&1 Editor Web con maquetación en tablas y `<font>` | HTML semántico y CSS moderno |
| No se adapta al móvil | Responsive, con menú móvil |
| Siete páginas sueltas con poco contenido cada una | Una sola página con anclas: todo a uno o dos scrolls |
| Los servicios están repartidos en tres subpáginas | Tres pestañas (Fiscal / Administrativa / Técnica) con todos los servicios |
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
- [ ] **Versión en inglés:** buena parte de la clientela de la Costa del Sol es extranjera.
- [ ] **Formulario de contacto:** ahora mismo es `mailto:`. Se podría usar Formspree, Netlify Forms o un PHP en el hosting.
- [ ] **Bloque "Cómo trabajamos":** el texto es nuevo, no viene de la web actual. Validarlo con la empresa.
- [ ] **Contenido nuevo:** testimonios, logos de marinas o clientes, preguntas frecuentes (IEDMT, importación temporal...).
