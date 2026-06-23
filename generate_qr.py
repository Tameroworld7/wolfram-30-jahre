from pathlib import Path

from PIL import Image, ImageDraw
from reportlab.graphics import renderSVG
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.lib.colors import black, white


folder = Path(__file__).resolve().parent
website_url = (folder / "website-url.txt").read_text(encoding="utf-8").strip()

# Eine großzügige Ruhezone sorgt dafür, dass Kameras den sehr datenreichen
# QR-Code auch auf einer gedruckten Karte zuverlässig erkennen können.
canvas_size = 1200
quiet_zone = 64
code_size = canvas_size - (quiet_zone * 2)

code = QrCodeWidget(
    website_url,
    barLevel="M",
    barFillColor=black,
    barWidth=code_size,
    barHeight=code_size,
    x=quiet_zone,
    y=quiet_zone,
)

drawing = Drawing(canvas_size, canvas_size)
drawing.add(Rect(0, 0, canvas_size, canvas_size, fillColor=white, strokeColor=None))
drawing.add(code)

renderSVG.drawToFile(drawing, str(folder / "wolfram-dankesbotschaft-qr.svg"))

# Zusätzlich entsteht eine verlustfreie PNG-Version. Jedes QR-Modul bekommt
# exakt zehn Bildpunkte; dadurch bleiben die Kanten auch beim Druck scharf.
code.qr.make()
module_count = code.qr.getModuleCount()
module_pixels = 10
quiet_modules = 4
image_modules = module_count + (quiet_modules * 2)
image = Image.new("RGB", (image_modules * module_pixels,) * 2, color=(255, 255, 255))
draw = ImageDraw.Draw(image)

for row in range(module_count):
    for column in range(module_count):
        if code.qr.isDark(row, column):
            left = (column + quiet_modules) * module_pixels
            top = (row + quiet_modules) * module_pixels
            draw.rectangle(
                (left, top, left + module_pixels - 1, top + module_pixels - 1),
                fill=(0, 0, 0),
            )

image.save(folder / "wolfram-dankesbotschaft-qr.png", optimize=True)

# Reduzierte SVG speziell für CAD-Importe: nur ein zusammengesetzter Pfad,
# keine Schriften, Bilder, Filter oder ReportLab-Metadaten. Die vier Module
# breite Ruhezone bleibt über die viewBox erhalten.
path_parts = []
for row in range(module_count):
    for column in range(module_count):
        if code.qr.isDark(row, column):
            x = column + quiet_modules
            y = row + quiet_modules
            path_parts.append(f"M{x} {y}h1v1h-1z")

cad_svg = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<svg xmlns="http://www.w3.org/2000/svg" '
    'width="20mm" height="20mm" '
    f'viewBox="0 0 {image_modules} {image_modules}">\n'
    f'  <path d="{"".join(path_parts)}" fill="#000000"/>\n'
    '</svg>\n'
)
(folder / "wolfram-dankesbotschaft-qr-catia.svg").write_text(
    cad_svg,
    encoding="utf-8",
)

print(
    f"QR-Code erstellt: {website_url}, "
    f"{module_count} × {module_count} Module"
)
