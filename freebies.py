"""freebies.py - free printable coloring pages from the Nick Colorful books: printable PDFs + web previews + pins.

    python freebies.py      # -> src/free/*.pdf, src/img/free/*.jpg, D:/ProjectAssets/DripDrop/free_printable_pins/*.jpg

Each freebie is one real page from a published book. The /free/ page offers the PDF and links the full book on
Amazon (Associates tag, #ad). build.py renders the page from FREEBIES.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
PINS = Path(r"D:/ProjectAssets/DripDrop/free_printable_pins")
F = r"C:/Windows/Fonts/"
PET = r"D:/Data_Recovery/0_Projects/ContentPipeline/coloring_books/pet_memorial/pages_print/"
DINO = r"D:/Data_Recovery/0_Projects/ContentPipeline/coloring_books/dino_4_8/pages_print/"
DANNY = r"D:/ProjectAssets/DripDrop/dino_books/danny/pages_print/"
DANIELA = r"D:/ProjectAssets/DripDrop/dino_books/daniela/pages_print/"

# asin=None until the book is live; the page then links an ISBN search instead of the product page
BOOKS = [
    dict(key="pet-memorial", title="Pet Memorial Coloring Book", sub="A keepsake for the loss of a dog or cat",
         asin=None, isbn="9798140646486", audience="Adults",
         pages=[("angel-dog", PET + "p04.png", "Angel dog"), ("angel-cat", PET + "p29.png", "Angel cat")]),
    dict(key="big-dinosaur", title="Big Dinosaur Coloring Book", sub="50 big, jumbo pictures for ages 4-8",
         asin="B0HMPQ2JKQ", isbn=None, audience="Kids 4-8",
         pages=[("hatching-dino", DINO + "p04.png", "Hatching baby dino"),
                ("birthday-dino", DINO + "p12.png", "Birthday dino")]),
    dict(key="danny-the-dino", title="Danny the Dino", sub="A dinosaur story & coloring book for ages 3-7",
         asin="B0HMSKKWCJ", isbn=None, audience="Kids 3-7",
         pages=[("danny-christmas", DANNY + "p18.png", "Danny's Christmas"),
                ("danny-birthday", DANNY + "p11.png", "Danny's birthday party")]),
    dict(key="daniela-the-dino", title="Daniela the Dino", sub="A dinosaur story & coloring book for ages 3-7",
         asin="B0HMR64RQZ", isbn=None, audience="Kids 3-7",
         pages=[("daniela-christmas", DANIELA + "p18.png", "Daniela's Christmas"),
                ("daniela-birthday", DANIELA + "p13.png", "Daniela's birthday")]),
]
INK, PAPER, GOLD, CREAM = (18, 18, 20), (244, 239, 228), (212, 175, 90), (236, 230, 216)


def font(name, size):
    return ImageFont.truetype(F + name, size)


def centered(d, y, text, f, fill, W):
    d.text(((W - d.textlength(text, font=f)) / 2, y), text, font=f, fill=fill)


def printable_pdf(src: str, book: dict, label: str, out: Path) -> None:
    """Letter page at 300 dpi: the art, plus a small credit line. Personal-use freebie."""
    W, H = 2550, 3300
    page = Image.new("L", (W, H), 255)
    art = Image.open(src).convert("L")
    art.thumbnail((W - 300, H - 520))
    page.paste(art, ((W - art.width) // 2, 180))
    d = ImageDraw.Draw(page)
    centered(d, H - 250, f"{label} - free printable from \u201c{book['title']}\u201d by Nick Colorful", font("arial.ttf", 46), 90, W)
    centered(d, H - 180, "Free for personal use \u00b7 more free pages: clairmont425.github.io/dripdrop/free", font("arial.ttf", 40), 120, W)
    page.save(out, "PDF", resolution=300)


def preview(src: str, out: Path) -> None:
    im = Image.open(src).convert("L")
    im.thumbnail((900, 900))
    im.convert("RGB").save(out, quality=82)


def pin(src: str, book: dict, label: str, out: Path) -> None:
    W, H = 1000, 1500
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    centered(d, 70, "FREE PRINTABLE COLORING PAGE", font("arialbd.ttf", 34), GOLD, W)
    size = 68
    while d.textlength(label.upper(), font=font("ariblk.ttf", size)) > W - 80:   # shrink long titles to fit
        size -= 2
    centered(d, 120 + (68 - size) // 2, label.upper(), font("ariblk.ttf", size), INK, W)
    card = Image.new("RGB", (860, 860), "white")
    art = Image.open(src).convert("RGB")
    art.thumbnail((800, 800))
    card.paste(art, ((860 - art.width) // 2, (860 - art.height) // 2))
    shadow = Image.new("RGB", (860, 860), (215, 208, 192))
    img.paste(shadow, (78, 252))
    img.paste(card, (70, 240))
    d.rectangle([0, 1150, W, H], fill=INK)
    d.line([(0, 1150), (W, 1150)], fill=GOLD, width=4)
    centered(d, 1195, "DOWNLOAD IT FREE", font("arialbd.ttf", 60), CREAM, W)
    centered(d, 1278, f"from \u201c{book['title']}\u201d \u00b7 {book['audience']}", font("arial.ttf", 34), (190, 184, 172), W)
    centered(d, 1345, "tap the pin \u00b7 DripDrop", font("arial.ttf", 32), GOLD, W)
    centered(d, 1420, "AI-assisted illustration \u00b7 full book on Amazon (#ad)", font("arial.ttf", 24), (130, 126, 118), W)
    img.save(out, quality=90)


def main() -> None:
    (ROOT / "src" / "free").mkdir(parents=True, exist_ok=True)
    (ROOT / "src" / "img" / "free").mkdir(parents=True, exist_ok=True)
    PINS.mkdir(parents=True, exist_ok=True)
    n = 0
    for b in BOOKS:
        for slug, src, label in b["pages"]:
            printable_pdf(src, b, label, ROOT / "src" / "free" / f"{slug}.pdf")
            preview(src, ROOT / "src" / "img" / "free" / f"{slug}.jpg")
            pin(src, b, label, PINS / f"{slug}.jpg")
            n += 1
    print(f"{n} freebies -> src/free, src/img/free, {PINS}")


if __name__ == "__main__":
    main()
