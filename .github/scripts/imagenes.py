"""Genera las variantes WebP de las imágenes de assets/img/ y el logo recortado de la cabecera.

    pip install pillow
    python .github/scripts/imagenes.py

- Cada .jpg/.png tiene un .webp al lado (lossless si el PNG tiene transparencia). build.py los
  sirve con <picture> y deja el JPG/PNG como respaldo.
- logo-vela.jpg/.webp: la zona del logo que se ve en la cabecera (el símbolo de la vela),
  para no descargar el logo entero (598×110) solo para enseñar 36×44 píxeles.
Las imágenes para compartir (compartir.jpg y compartir-en.jpg) se generan con compartir.html:
ver el README.
"""
from pathlib import Path

from PIL import Image

IMG = Path(__file__).resolve().parents[2] / "assets" / "img"
SIN_WEBP = {"compartir.jpg", "compartir-en.jpg", "logo-original.jpg"}  # las redes sociales piden JPG
VELA = (0, 0, 90, 110)  # 36×44 px de la cabecera, a la escala 44/110 del logo original


def webp(origen):
    im = Image.open(origen)
    destino = origen.with_suffix(".webp")
    if im.mode == "RGBA":
        im.save(destino, "WEBP", lossless=True, method=6)
    else:
        im.convert("RGB").save(destino, "WEBP", quality=82, method=6)
    print(f"{origen.name:24} {origen.stat().st_size / 1024:6.1f} KB → {destino.name:24} {destino.stat().st_size / 1024:6.1f} KB")


def main():
    vela = Image.open(IMG / "logo-original.jpg").convert("RGB").crop(VELA)
    vela.save(IMG / "logo-vela.jpg", quality=95)
    for f in sorted(IMG.iterdir()):
        if f.suffix.lower() in (".jpg", ".jpeg", ".png") and f.name not in SIN_WEBP:
            webp(f)


if __name__ == "__main__":
    main()
