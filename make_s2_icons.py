from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "icons"
SOURCE = Path("/Users/aleksandragolyb/.codex/generated_images/01a1e044-593b-7611-abfd-b62b45c4c73d/exec-83caf68b-8bf9-41a0-9035-6edfdc77da42.png")
OUT.mkdir(exist_ok=True)

src = Image.open(SOURCE).convert("RGB")
w, h = src.size
assert w == h and w % 3 == 0, src.size
cell = w // 3
objects = ["A", "B", "C"]
materials = ["Gel", "Clay", "Glass"]
paper = (247, 244, 238)
ink = (44, 52, 43)
font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
font = ImageFont.truetype(font_path, 15)

icons = {}
for row, obj in enumerate(objects):
    for col, material in enumerate(materials, 1):
        # Source is intentionally a strict 3×3 composition. Each exact cell is
        # upsampled rather than re-framed so all object margins remain equal.
        crop = src.crop(((col - 1) * cell, row * cell, col * cell, (row + 1) * cell))
        icon = crop.resize((1024, 1024), Image.Resampling.LANCZOS)
        path = OUT / f"s2_{obj}{col}.png"
        icon.save(path, "PNG", optimize=True)
        icons[(row, col - 1)] = icon

# 3 × 3 review sheet. Preview bitmap is exactly 180 px, clipped to 40 px corners.
sheet = Image.new("RGB", (900, 810), paper)
draw = ImageDraw.Draw(sheet)
for row, obj in enumerate(objects):
    for col, material in enumerate(materials):
        x, y = 60 + col * 300, 38 + row * 270
        preview = icons[(row, col)].resize((180, 180), Image.Resampling.LANCZOS)
        mask = Image.new("L", (180, 180), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, 179, 179), radius=40, fill=255)
        sheet.paste(preview, (x, y), mask)
        label = f"{obj}{col + 1} · {material}"
        width = draw.textbbox((0, 0), label, font=font)[2]
        draw.text((x + (180 - width) / 2, y + 198), label, fill=ink, font=font)
sheet.save(OUT / "s2_sheet.png", "PNG", optimize=True)

# This is a literal resampling proof: the 40px column contains the final 40px pixels.
strip = Image.new("RGB", (420, 9 * 210), paper)
draw = ImageDraw.Draw(strip)
for n, (row, col) in enumerate([(r, c) for r in range(3) for c in range(3)]):
    y = n * 210
    name = f"{objects[row]}{col + 1}"
    draw.text((14, y + 95), name, fill=ink, font=font)
    x = 55
    for size in (180, 80, 40):
        rendered = icons[(row, col)].resize((size, size), Image.Resampling.LANCZOS)
        strip.paste(rendered, (x, y + (190 - size) // 2))
        label = str(size)
        lw = draw.textbbox((0, 0), label, font=font)[2]
        draw.text((x + (size - lw) / 2, y + 192), label, fill=ink, font=font)
        x += size + 18
strip.save(OUT / "s2_small.png", "PNG", optimize=True)

for file in sorted(OUT.glob("s2_*.png")):
    with Image.open(file) as check:
        print(f"{file.name}: {check.size}")
