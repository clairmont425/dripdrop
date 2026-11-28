"""build.py - DripDrop site: the Etsy shop showcase + DripDrop Picks (pet-gear buying filters with affiliate links).

    python build.py            # src/ + listings.json -> docs/ (static, relative links, GitHub Pages at /dripdrop/)

Shop data is pulled live from the Etsy API into src/listings.json (title, price, url, 2 photos per listing).
Picks rules (operator/ventures/affiliate/AMAZON_RULES.md): no Amazon imagery, no prices, the Amazon disclosure
sentence on every picks page, rel=sponsored, and the 'we have not tested these' banner. Photos on picks pages are
AI-generated generic examples of each category and are labelled as such.
"""
from __future__ import annotations

import html
import json
import os
import re
import shutil
from pathlib import Path
from urllib.parse import quote_plus

from freebies import BOOKS as FREE_BOOKS

ROOT = Path(__file__).resolve().parent
SRC, DIST = ROOT / "src", ROOT / "docs"   # GitHub Pages serves main:/docs
ENV = Path(r"C:/Users/Nico Clairmont/Projects/.env.master")
ETSY_SHOP = "https://www.etsy.com/shop/DripDropShopUS"
IG = "https://www.instagram.com/dripdropgram/"
SITE = "https://clairmont425.github.io/dripdrop/"
IMPACT_META = "<meta name='impact-site-verification' value='78c583fb-7431-465a-86ca-7bddd8836b08'>"
AMAZON_SENTENCE = "As an Amazon Associate I earn from qualifying purchases."


def amazon_tag() -> str:
    m = re.search(r"^AMAZON_ASSOC_TAG=(.+)$", ENV.read_text(encoding="utf-8"), re.M)
    if not m:
        raise SystemExit("AMAZON_ASSOC_TAG missing from .env.master")
    return m.group(1).strip()


TAG = amazon_tag()


def amazon_book(b: dict) -> str:
    """Product page once the ASIN exists; an ISBN search while a new title is still going live."""
    return f"https://www.amazon.com/dp/{b['asin']}?tag={TAG}" if b["asin"] else amazon_search(b["isbn"])


def amazon_search(term: str) -> str:
    return f"https://www.amazon.com/s?k={quote_plus(term)}&tag={TAG}"


def amazon_dp(asin: str) -> str:
    return f"https://www.amazon.com/dp/{asin}?tag={TAG}"


# ---------------------------------------------------------------- books (Nick Colorful, KDP)
# No prices shown on this page (Amazon Program Policies: a price next to a Special Link needs
# live Creators/PA-API data + a timestamp disclaimer, which this static site doesn't have).
BOOKS = [
    dict(id="big-dinosaur", title="Big Dinosaur Coloring Book", age="Ages 4-8", cover="big-dinosaur.jpg",
         blurb="50 roaring-good dinosaur designs, bold and simple for a first coloring book.",
         freebie="big-dinosaur.pdf",
         editions=[("Paperback", "B0HMPQ2JKQ"), ("Hardcover", "B0HN48F9QD")]),
    dict(id="pet-memorial", title="Pet Memorial Coloring Book", age="For adults", cover="pet-memorial.jpg",
         blurb="A gentle keepsake for the loss of a dog or cat -- rainbow bridges, paw-print wreaths and "
               "quiet gardens for a few calm, mindful minutes during grief.",
         freebie="pet-memorial.pdf", editions=[]),
    dict(id="big-space", title="Big Space Coloring Book", age="Ages 4-8", cover="big-space.jpg",
         blurb="50 big, simple astronaut, rocket and planet pictures -- smiling astronauts, friendly aliens "
               "and shooting stars for a first coloring book.",
         freebie="big-space.pdf", editions=[]),
    dict(id="construction-trucks", title="Big Construction Trucks Coloring Book", age="Toddlers 2-4",
         cover="construction-trucks.jpg",
         blurb="50 big, extra-simple truck pictures made for little hands -- dump trucks, excavators, "
               "cranes and cement mixers, one giant friendly subject per page.",
         freebie="construction-trucks.pdf", editions=[]),
]
DINO_SERIES = [("Danny the Dino", "B0HMSKKWCJ"), ("Daniela the Dino", "B0HMR64RQZ")]


# ---------------------------------------------------------------- shop data
def collections() -> dict[str, list[dict]]:
    out = {"pets": [], "holiday": [], "tiedye": [], "tees": []}
    for l in json.loads((SRC / "listings.json").read_text(encoding="utf-8")):
        t = l["title"]
        if not l.get("imgs") or re.search(r"Paddle|Umbrella", t):
            continue
        key = ("pets" if re.search(r"Pet Portrait|Custom Pet", t) else
               "holiday" if "Ugly Christmas" in t else
               "tiedye" if re.search(r"Tie[- ]Dye", t) else "tees")
        out[key].append(l)
    return out


def short(title: str) -> str:
    """Etsy titles are SEO strings; the first clause is the product name."""
    t = re.split(r"[,|]| - ", title)[0].strip()
    return re.sub(r"\s+", " ", t)


def card(l: dict, root: str) -> str:
    n = len(l["imgs"])
    alt = html.escape(short(l["title"]))
    hover = (f'<img class="b" src="{root}img/shop/{l["id"]}_1.jpg" alt="" loading="lazy">' if n > 1 else "")
    return f"""<a class="card" href="{l['url']}" target="_blank" rel="noopener">
  <div class="ph"><img class="a" src="{root}img/shop/{l['id']}_0.jpg" alt="{alt}" loading="lazy">{hover}</div>
  <div class="meta"><span class="nm">{alt}</span><span class="pr">${l['price']:.2f}</span></div>
</a>"""


# ---------------------------------------------------------------- picks content
PICKS = {
    "feeding": {
        "title": "Feeding & enrichment",
        "kicker": "Buying filter 01",
        "lede": "Bowls, stands, lick mats and puzzles. Each one is decided by one or two specs most listings bury. "
                "Here is what to check before you buy.",
        "items": [
            dict(id="slow-feeder", photo=1, name="Slow feeder bowls", call="Ridge depth + base width",
                 check=["Ridge depth that suits the snout: deep channels for big or long-nosed dogs, shallow ones "
                        "for flat-faced breeds that can't reach into deep grooves.",
                        "A wide, non-slip base - rubber feet or a weighted bottom - so the bowl doesn't skate "
                        "across the floor mid-meal.",
                        "Dishwasher-safe material (stainless steel, ceramic or BPA-free plastic). Mazes trap food in "
                        "the corners."],
                 skip="Your dog already eats slowly - a snuffle mat or scatter feeding may be more fun.",
                 term="slow feeder dog bowl"),
            dict(id="elevated-feeder", photo=2, name="Elevated feeders", call="Measure at the shoulder",
                 check=["Measure your dog standing, floor to the top of the shoulder. Stands are sized by that "
                        "number, not by breed.",
                        "Bowl capacity in cups compared with one full meal.",
                        "A wide footprint or adjustable legs, and bowls that lift out for washing."],
                 skip="Your vet has recommended a specific feeding setup - follow that instead.",
                 term="adjustable elevated dog bowl stand"),
            dict(id="lick-mat", photo=3, name="Lick mats", call="Food-grade silicone, not TPE",
                 check=["\u201c100% food-grade silicone\u201d on the listing. TPE and rubber blends are the ones that "
                        "warp on the top rack.",
                        "Suction cups or a heavy base if your dog pushes the mat around.",
                        "Groove depth: shallow for spreads, deeper for frozen fillings."],
                 skip="Your dog chews instead of licks - a lick mat isn't a chew toy.",
                 term="silicone lick mat for dogs dishwasher safe"),
            dict(id="puzzle-toy", photo=4, name="Puzzle toys", call="Level 1 \u00b7 2 \u00b7 3",
                 check=["The difficulty level - most makers rate 1 to 3 or 1 to 4. Start at level 1 for a first "
                        "puzzle, even with a smart dog.",
                        "No small parts that can be pulled off and swallowed.",
                        "Compartments you can actually get a sponge into."],
                 skip="Your dog gives up fast - start with a snuffle mat and work up.",
                 term="dog puzzle toy level 1"),
        ],
    },
    "walks": {
        "title": "Walks, grooming & the car",
        "kicker": "Buying filter 02",
        "lede": "Gear that has to survive a trail, a wet dog and a back seat. The failure points are predictable - "
                "so check them first.",
        "items": [
            dict(id="travel-bowl", photo=5, name="Collapsible travel bowls", call="Seam \u00b7 clip \u00b7 fold line",
                 check=["One-piece silicone. A glued seam where the rim meets the body is where leaks start.",
                        "A metal carabiner - plastic clips snap.",
                        "Capacity in ounces for your dog's size, and a stated wall thickness."],
                 skip="You already carry a bottle with a built-in trough.",
                 term="collapsible silicone dog bowl carabiner"),
            dict(id="water-bottle", photo=6, name="Dog water bottles", call="One dog or two?",
                 check=["Flip-out trough vs squeeze-to-fill: troughs work one-handed, squeeze bottles waste less.",
                        "A lock or button so it doesn't leak in a bag.",
                        "Capacity for your longest walk, plus a carry loop."],
                 skip="You walk two dogs at once - pick a one-handed design or skip the bottle.",
                 term="portable dog water bottle leak proof"),
            dict(id="harness", photo=7, name="No-pull harnesses", call="Chest-strap width",
                 check=["Both a front clip and a back clip, so you can switch as training improves.",
                        "A wide, padded chest strap that spreads pressure instead of concentrating it.",
                        "Four adjustment points, sized by chest girth rather than weight."],
                 skip="Pulling is new or sudden - a trainer will help more than any harness.",
                 term="no pull dog harness front clip"),
            dict(id="deshedding", photo=8, name="Deshedding brushes", call="Short \u00b7 double \u00b7 long coat",
                 check=["Match the tool to the coat: undercoat rakes for double coats, rubber curry brushes for short "
                        "coats, slicker brushes for long coats.",
                        "Tine or blade spacing listed in the description.",
                        "A release button that clears the hair in one push."],
                 skip="The coat is already matted - that's a groomer job.",
                 term="dog deshedding brush undercoat rake"),
            dict(id="seat-cover", photo=9, name="Car seat covers", call="Anchors, then straps",
                 check=["Seat anchors that tuck into the seat crease - without them, a cover slides.",
                        "Headrest straps front and back for the hammock style.",
                        "A waterproof layer with a non-slip backing, sized to your seat width."],
                 skip="Your dog rides in a crate - a crate pad is the better buy.",
                 term="dog car seat cover hammock seat anchors"),
            dict(id="vacuum-attachment", photo=10, name="Pet-hair vacuum attachments", call="Check the fitting size",
                 check=["Your hose's fitting diameter (often 32 mm or 35 mm) - it's in the manual, and adapters "
                        "exist.",
                        "A motorised turbo head for upholstery and stairs.",
                        "A tangle-free roller, so you aren't cutting hair off it every week."],
                 skip="Your vacuum already shipped with a pet tool - try it first.",
                 term="pet hair vacuum attachment turbo brush"),
        ],
    },
}


# ---------------------------------------------------------------- layout
FONTS = ("https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,800"
         "&family=Instrument+Sans:wght@400;500;600&family=Instrument+Serif:ital@0;1&display=swap")


def page(title: str, desc: str, body: str, root: str, impact: bool = False, cls: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{IMPACT_META if impact else ''}
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{root}assets/site.css">
<link rel="icon" href="{root}assets/favicon.svg">
</head>
<body class="{cls}">
<header class="top">
  <a class="logo" href="{root}index.html">Drip<span>Drop</span></a>
  <nav>
    <a href="{root}index.html#pets">Pet portraits</a>
    <a href="{root}index.html#holiday">Holiday</a>
    <a href="{root}index.html#tees">Tees</a>
    <a href="{root}picks/index.html">Picks</a>
    <a href="{root}books/index.html">Books</a>
    <a href="{root}free/index.html">Free pages</a>
    <a class="etsy" href="{ETSY_SHOP}" target="_blank" rel="noopener">Etsy shop &#8599;</a>
  </nav>
</header>
{body}
<footer class="foot">
  <div class="fl">
    <a class="logo" href="{root}index.html">Drip<span>Drop</span></a>
    <p>Made-to-order tees, sweaters and pet portraits. Every order ships through our Etsy shop.</p>
  </div>
  <div class="fr">
    <a href="{ETSY_SHOP}" target="_blank" rel="noopener">Etsy</a>
    <a href="{IG}" target="_blank" rel="noopener">Instagram</a>
    <a href="{root}picks/index.html">DripDrop Picks</a>
    <a href="{root}free/index.html">Free coloring pages</a>
    <a href="{root}disclosure.html">Affiliate disclosure</a>
    <a href="https://clairmont425.github.io/clarity-stack/dripdrop-privacy.html">Privacy</a>
  </div>
</footer>
</body>
</html>
"""


def disclosure_bar(root: str) -> str:
    return (f'<div class="adbar"><b>#ad</b> Links on this page are affiliate links: we earn a commission if you '
            f'buy, at no extra cost to you. {AMAZON_SENTENCE} <a href="{root}disclosure.html">More</a></div>')


def home(c: dict) -> str:
    root = ""
    pets = c["pets"]
    lead = next((l for l in pets if "Oversized" in l["title"]), pets[0])
    hero_imgs = [l for l in pets if l["id"] != lead["id"]][:2]
    styles = ["Howling at the Moon", "Royal", "Knight", "Hip Hop", "Renaissance", "Pop Art", "Wild Spirit"]
    marquee = "".join(f"<span>{s}</span><i>&#10022;</i>" for s in styles) * 2
    grid = lambda key, n=None: "\n".join(card(l, root) for l in c[key][:n])
    picks_cards = "\n".join(f"""<a class="pk" href="picks/{k}.html">
  <img src="img/picks/photo_{v['items'][0]['photo']:02d}.jpg" alt="" loading="lazy">
  <div><em>{v['kicker']}</em><h3>{v['title']}</h3><p>{len(v['items'])} buying filters &rarr;</p></div>
</a>""" for k, v in PICKS.items())
    body = f"""
<main>
<section class="hero">
  <div class="hl">
    <p class="kick rise" style="--d:0">Custom pet portraits &middot; made to order</p>
    <h1 class="rise" style="--d:1">Your pet.<br><em>On everything.</em></h1>
    <p class="sub rise" style="--d:2">Upload one photo of your dog or cat. We turn it into a portrait - howling at the
      moon, crowned royalty, a knight in armour - and put it on a tee, canvas, mug or blanket.</p>
    <div class="ctas rise" style="--d:3">
      <a class="btn" href="{lead['url']}" target="_blank" rel="noopener">Start with a photo &rarr;</a>
      <a class="btn ghost" href="#pets">See every style</a>
    </div>
  </div>
  <div class="hr">
    <img class="h1i" src="img/shop/{lead['id']}_0.jpg" alt="{html.escape(short(lead['title']))}">
    <img class="h2i" src="img/shop/{hero_imgs[0]['id']}_0.jpg" alt="">
    <img class="h3i" src="img/shop/{hero_imgs[1]['id']}_0.jpg" alt="">
    <span class="stamp">from<br><b>${min(l['price'] for l in pets):.2f}</b></span>
  </div>
</section>
<div class="marq"><div>{marquee}</div></div>

<section class="sec" id="pets">
  <div class="sh"><h2>Pet portraits</h2><p>Seven styles, one upload. Tees, canvas, mugs, ornaments, blankets.</p></div>
  <div class="grid">{grid('pets')}</div>
</section>

<section class="sec dark" id="holiday">
  <div class="sh"><h2>Ugly <em>(on purpose)</em> sweaters</h2><p>All-over knit print. Order by early December for Christmas.</p></div>
  <div class="rail">{grid('holiday')}</div>
</section>

<section class="sec" id="tees">
  <div class="sh"><h2>Tie-dye &amp; graphic tees</h2><p>Cyclone dyes, pocket prints and the shirts that start conversations.</p></div>
  <div class="grid">{grid('tiedye', 8)}{grid('tees')}</div>
  <p class="more"><a href="{ETSY_SHOP}" target="_blank" rel="noopener">Everything else on Etsy &rarr;</a></p>
</section>

<section class="sec picks" id="picks">
  <div class="sh"><h2>DripDrop <em>Picks</em></h2><p>Buying filters for pet people: the specs that decide whether the
    gear works. <span class="adtag">#ad &middot; affiliate links inside</span></p></div>
  <div class="pks">{picks_cards}</div>
</section>

<section class="sec" id="books">
  <div class="sh"><h2>Nick Colorful <em>coloring books</em></h2><p>Free printable samples, plus the full books on
    Amazon. <span class="adtag">#ad &middot; affiliate links inside</span></p></div>
  <a class="pk" href="books/index.html">
    <img src="img/books/{BOOKS[0]['cover']}" alt="" loading="lazy">
    <div><em>Low-content books</em><h3>{len(BOOKS)} books, free printables</h3><p>See the books &rarr;</p></div>
  </a>
</section>
</main>"""
    return page("DripDrop - custom pet portraits, tees & ugly sweaters",
                "Turn your dog or cat into a portrait on a tee, canvas or mug. Plus tie-dye, graphic tees, holiday "
                "sweaters and DripDrop Picks buying filters for pet gear.", body, root, impact=True, cls="home")


def picks_index() -> str:
    root = "../"
    cards = "\n".join(f"""<a class="pk big" href="{k}.html">
  <img src="../img/picks/photo_{v['items'][0]['photo']:02d}.jpg" alt="" loading="lazy">
  <div><em>{v['kicker']}</em><h3>{v['title']}</h3><p>{v['lede']}</p>
  <ul>{''.join(f"<li>{i['name']}</li>" for i in v['items'])}</ul></div>
</a>""" for k, v in PICKS.items())
    gift_cards = f"""<a class="pk big" href="gifts-for-dog-people.html">
  <img src="../img/picks/photo_01.jpg" alt="" loading="lazy">
  <div><em>Gift guide</em><h3>Gifts for dog people</h3><p>Our own pet portraits, plus the dog-gear
  buying filters.</p></div>
</a>
<a class="pk big" href="kitchen-gifts.html">
  <img src="../img/picks/photo_11.jpg" alt="" loading="lazy">
  <div><em>{KITCHEN_GIFTS['kicker']}</em><h3>{KITCHEN_GIFTS['title']}</h3><p>{KITCHEN_GIFTS['lede']}</p></div>
</a>
<a class="pk big" href="home-organization.html">
  <img src="../img/picks/photo_20.jpg" alt="" loading="lazy">
  <div><em>{HOME_GIFTS['kicker']}</em><h3>{HOME_GIFTS['title']}</h3><p>{HOME_GIFTS['lede']}</p></div>
</a>
<a class="pk big" href="last-minute-gifts.html">
  <img src="../img/picks/photo_15.jpg" alt="" loading="lazy">
  <div><em>Gift guide &middot; last-minute</em><h3>Last-minute gift guide</h3><p>One pick each for the
  dog person, the cook, the organizer and the creator.</p></div>
</a>"""
    body = f"""<main class="pmain">
{disclosure_bar(root)}
<section class="phero"><p class="kick">DripDrop Picks</p><h1>Buy the spec,<br><em>not the hype.</em></h1>
<p class="sub">Short buying filters for pet gear and gift guides. We haven't tested these products - each guide
tells you which two or three specs decide whether a product works, so you can judge any listing yourself.</p></section>
<div class="pks two">{cards}{gift_cards}</div>
</main>"""
    return page("DripDrop Picks - buying filters for pet gear", "The specs that decide whether pet gear works.",
                body, root, cls="pk-page")


def guide(key: str) -> str:
    root, g = "../", PICKS[key]
    items = []
    for n, it in enumerate(g["items"], 1):
        checks = "".join(f"<li>{html.escape(x)}</li>" for x in it["check"])
        items.append(f"""<article class="it" id="{it['id']}">
  <figure><img src="../img/picks/photo_{it['photo']:02d}.jpg" alt="{html.escape(it['name'])} - generic example" loading="lazy">
    <figcaption>AI-generated photo &middot; generic example, not a specific product</figcaption></figure>
  <div class="tx">
    <span class="num">{n:02d}</span>
    <h2>{html.escape(it['name'])}</h2>
    <span class="call">{html.escape(it['call'])}</span>
    <h4>What to check</h4><ul>{checks}</ul>
    <p class="skip"><b>Skip it if</b> {html.escape(it['skip'])}</p>
    <a class="btn" href="{amazon_search(it['term'])}" target="_blank" rel="sponsored nofollow noopener">Search Amazon for {html.escape(it['name'].lower())} &rarr;</a>
    <small class="ad">#ad &middot; affiliate link</small>
  </div>
</article>""")
    toc = "".join(f'<a href="#{i["id"]}">{html.escape(i["name"])}</a>' for i in g["items"])
    body = f"""<main class="pmain">
{disclosure_bar(root)}
<section class="phero"><p class="kick">{g['kicker']}</p><h1>{g['title']}</h1><p class="sub">{g['lede']}</p>
<div class="notest"><b>We have not tested these products.</b> This page is a buying filter, not a review: it tells
you which specs decide whether the gear works, so you can judge any listing - including ones we don't link.</div>
<nav class="toc">{toc}</nav></section>
{''.join(items)}
<section class="cross"><h3>While you're here</h3><p>We make custom portraits of your pet on tees, mugs and canvas.</p>
<a class="btn ghost" href="../index.html#pets">See the pet portraits &rarr;</a></section>
</main>"""
    return page(f"{g['title']} - DripDrop Picks", g["lede"], body, root, cls="pk-page")


def books_index() -> str:
    root = "../"

    def book_card(b: dict) -> str:
        buys = "".join(
            f'<a class="btn ghost small" href="{amazon_dp(asin)}" target="_blank" '
            f'rel="sponsored nofollow noopener">{html.escape(label)} on Amazon &rarr;</a>'
            for label, asin in b["editions"]
        ) or '<span class="soon">Coming soon to Amazon</span>'
        return f"""<article class="book">
  <img src="../img/books/{b['cover']}" alt="{html.escape(b['title'])} cover" loading="lazy">
  <div class="tx">
    <span class="age">{html.escape(b['age'])}</span>
    <h2>{html.escape(b['title'])}</h2>
    <p>{html.escape(b['blurb'])}</p>
    <div class="buys">{buys}</div>
    <a class="btn small" href="../freebies/{b['freebie']}" target="_blank">Free printable &middot; 3 pages &rarr;</a>
    <small class="ad">Amazon links are #ad &middot; affiliate links</small>
  </div>
</article>"""

    series = "".join(
        f'<a class="btn ghost small" href="{amazon_dp(asin)}" target="_blank" '
        f'rel="sponsored nofollow noopener">{html.escape(name)} on Amazon &rarr;</a>'
        for name, asin in DINO_SERIES
    )
    body = f"""<main class="pmain">
{disclosure_bar(root)}
<section class="phero"><p class="kick">Nick Colorful &middot; coloring books</p><h1>Printable pages,<br><em>then the full book.</em></h1>
<p class="sub">Low-content coloring books from our imprint Nick Colorful. Grab a free 3-page printable sample
of each book below, then find the full book on Amazon.</p></section>
<div class="books">{''.join(book_card(b) for b in BOOKS)}</div>
<section class="cross"><h3>Also in the Dino Friends series</h3>
<p>Danny the Dino and Daniela the Dino, same bold toddler-friendly style as Big Dinosaur Coloring Book.</p>
<div class="buys">{series}</div></section>
<section class="cross"><h3>While you're here</h3><p>We make custom portraits of your pet on tees, mugs and canvas.</p>
<a class="btn ghost" href="../index.html#pets">See the pet portraits &rarr;</a></section>
</main>"""
    return page("Nick Colorful coloring books - free printables - DripDrop",
                "Free printable sample pages from our Nick Colorful coloring books, plus links to the full "
                "books on Amazon.", body, root, cls="pk-page")


def free_page() -> str:
    root = "../"
    secs = []
    for b in FREE_BOOKS:
        cards = "".join(f"""<div class="fp" id="{slug}">
  <a href="{slug}.pdf" download><img src="../img/free/{slug}.jpg" alt="{html.escape(label)} coloring page" loading="lazy"></a>
  <div><h3>{html.escape(label)}</h3><a class="btn" href="{slug}.pdf" download>Download free PDF &darr;</a></div>
</div>""" for slug, _src, label in b["pages"])
        secs.append(f"""<section class="fbook" id="{b['key']}">
  <div class="fhead"><div><em>{html.escape(b['audience'])}</em><h2>{html.escape(b['title'])}</h2><p>{html.escape(b['sub'])}</p></div>
  <a class="btn ghost" href="{amazon_book(b)}" target="_blank" rel="sponsored nofollow noopener">Get the full book on Amazon &rarr;</a></div>
  <div class="fgrid">{cards}</div>
</section>""")
    body = f"""<main class="pmain">
{disclosure_bar(root)}
<section class="phero"><p class="kick">Free printables</p><h1>Free coloring pages,<br><em>print and go.</em></h1>
<p class="sub">Real pages from our coloring books - letter size, free for personal use. If your kid (or you) likes them,
the full books are on Amazon. Illustrations are AI-assisted and hand-picked.</p></section>
{''.join(secs)}
<section class="cross"><h3>Lost a pet recently?</h3><p>We also turn a photo of your dog or cat into a custom portrait tee or canvas.</p>
<a class="btn ghost" href="../index.html#pets">See the pet portraits &rarr;</a></section>
</main>"""
    return page("Free printable coloring pages - DripDrop", "Free printable coloring pages for kids and adults: dinosaurs, Christmas, birthdays and pet memorial pages.", body, root, cls="pk-page")


def disclosure() -> str:
    body = f"""<main class="pmain narrow"><section class="phero"><p class="kick">Disclosure</p><h1>How DripDrop makes money</h1>
<p class="sub">DripDrop sells its own made-to-order products through Etsy. On DripDrop Picks pages, some links are
affiliate links: if you buy through them, we earn a commission at no extra cost to you. Those links are marked
<b>#ad</b>. {AMAZON_SENTENCE}</p>
<p class="sub">Picks pages are buying filters, not reviews. We say on every page that we haven't tested the products,
and the photos there are AI-generated generic examples of each category, labelled as such. Prices aren't shown
because they change - check the retailer.</p></section></main>"""
    return page("Affiliate disclosure - DripDrop", "How DripDrop makes money.", body, "", cls="pk-page")


# ---------------------------------------------------------------- gift guides (Black Friday push)
# Reuses the feeding/walks criteria + existing generic photos (no new image generation needed) for
# the dog-people guide; the kitchen guide is new content and ships text-only (criteria + search
# links, same "we have not tested these" pattern as the other picks pages) rather than spend budget
# on new generic stock photos this run.
DOG_GIFT_ITEM_IDS = ["slow-feeder", "elevated-feeder", "lick-mat", "puzzle-toy", "harness",
                     "deshedding", "seat-cover"]

KITCHEN_GIFTS = {
    "kicker": "Gift guide",
    "title": "Kitchen gifts",
    "lede": "Kitchen gear is the best-paying category we carry and the easiest to get wrong as a "
            "gift. Each one is decided by a spec most listings don't put in the title - here is "
            "what to check first.",
    "items": [
        dict(id="kettle", name="Electric gooseneck kettle", call="Hold temperature, not just boil", photo=11,
             check=["A stated hold-temperature feature, not just a kill switch at boiling - that's "
                    "the difference for pour-over coffee and tea.",
                    "Gooseneck spout for a controlled pour; a wide spout is the #1 return reason.",
                    "Stainless or glass interior - avoid unlined non-stick coatings that chip with "
                    "boiling water."],
             skip="They already own a stovetop kettle they like - this is an upgrade, not a fix.",
             term="gooseneck electric kettle variable temperature"),
        dict(id="knife-set", name="Chef's knife", call="Steel type, then weight in hand", photo=12,
             check=["Steel hardness (HRC) printed in the spec sheet - 56-60 HRC holds an edge "
                    "without being brittle.",
                    "Full tang construction (the blade metal runs through the handle) for balance "
                    "and durability.",
                    "Weight and handle shape fit the cook's hand - a demo video beats a spec sheet "
                    "here if one exists."],
             skip="They already have a knife they sharpen and like - a new one won't out-perform a "
                  "sharp familiar blade.",
             term="chef knife high carbon steel full tang"),
        dict(id="cutting-board", name="End-grain cutting board", call="End-grain, then thickness", photo=13,
             check=["End-grain construction (the wood fibers face up) - it self-heals and is gentler "
                    "on knife edges than edge-grain.",
                    "At least 1.5″ thickness so it doesn't warp.",
                    "Hardwood species (maple, walnut) rather than a soft wood that dents."],
             skip="Counter space is tight - a smaller edge-grain board is the more honest gift.",
             term="end grain cutting board thick hardwood"),
        dict(id="scale", name="Kitchen scale", call="Resolution, then max capacity", photo=14,
             check=["1-gram resolution at minimum - baking recipes depend on it.",
                    "Stated max capacity that clears a full mixing bowl, not just a cup of flour.",
                    "A tare/zero button and a removable platform for easy cleaning."],
             skip="They already measure by cups and have no interest in baking by weight.",
             term="digital kitchen scale 1 gram resolution"),
        dict(id="cast-iron", name="Cast iron skillet", call="Pre-seasoned, then weight", photo=15,
             check=["Pre-seasoned from the factory, so it's usable on arrival rather than needing a "
                    "multi-session seasoning process.",
                    "Weight relative to who's lifting it - a 12″ skillet can run 8+ lbs.",
                    "A helper handle on larger sizes for a second hand when it's full and hot."],
             skip="They've said cast iron maintenance isn't for them - a carbon steel pan is the "
                  "lighter-maintenance alternative, not a reason to skip the gift.",
             term="pre seasoned cast iron skillet"),
        dict(id="thermometer", name="Instant-read meat thermometer", call="Read speed, then probe length", photo=16,
             check=["Read time under 3 seconds, stated in the spec sheet - slower ones get set down "
                    "and forgotten.",
                    "A thin probe tip (under 3mm) for accurate reads in thin cuts like chicken "
                    "breast.",
                    "Food-safe temperature range and a calibration function."],
             skip="They already run a leave-in probe thermometer - an instant-read is a different "
                  "tool, not an upgrade.",
             term="instant read meat thermometer fast"),
        dict(id="sharpener", name="Knife sharpener", call="Angle-guided, not freehand", photo=17,
             check=["A fixed-angle guide system if the recipient doesn't already freehand sharpen - "
                    "it's the difference between a usable edge and a ruined one.",
                    "Stage count (coarse/medium/fine) matched to how dull their knives actually get.",
                    "Compatible with the knife steel type they own - some systems struggle with very "
                    "hard steel."],
             skip="They already have a whetstone routine they're happy with - don't replace a habit "
                  "that's working.",
             term="angle guided knife sharpening system"),
        dict(id="storage", name="Glass food storage set", call="Lid seal, then stackability", photo=18,
             check=["A silicone-gasket lid that's actually described as leak-proof, not just "
                    "“snap-fit”.",
                    "Oven and freezer safe glass if that's how they cook - check both, not just one.",
                    "A stated stacking/nesting system so the set doesn't take over a cabinet."],
             skip="They already have a set they like - more containers without a matching lid "
                  "system just adds clutter.",
             term="glass food storage containers leak proof lids"),
        dict(id="salad-spinner", name="Salad spinner", call="Pump vs pull cord, then bowl use", photo=19,
             check=["Mechanism type - pump-top designs are quieter and easier with one hand than a "
                    "pull-cord.",
                    "A bowl that doubles as a serving bowl, so it earns counter space.",
                    "Capacity relative to household size - a 2-person spinner is too small for a "
                    "family."],
             skip="They rarely eat fresh greens - this is a single-use gadget for them.",
             term="salad spinner pump bowl"),
    ],
}


HOME_GIFTS = {
    "kicker": "Gift guide",
    "title": "Home organization gifts",
    "lede": "Storage and organizing gear looks the same across price points in a photo. These are "
            "the specs that actually decide whether it gets used after the first week.",
    "items": [
        dict(id="clear-bins", name="Stackable clear storage bins", call="Clarity, then a rated stack height",
             photo=20,
             check=["Clear (not frosted) plastic so contents are visible without opening the lid.",
                    "A stated stack-load rating, not just \"stackable\" - that's what keeps a bottom "
                    "bin from cracking.",
                    "A lid that locks or snaps on all sides, not just two tabs."],
             skip="Everything is already in matching bins from one set - mixing sizes undoes the point.",
             term="stackable clear storage bins with lids"),
        dict(id="vacuum-bags", name="Vacuum storage bags", call="Valve type, then bag thickness", photo=21,
             check=["A one-way valve rated for a specific pump or vacuum hose size.",
                    "Stated bag thickness in microns - thin bags puncture on sharp zipper teeth.",
                    "A double-zip seal track, which is the actual leak point on cheap versions."],
             skip="The items are down/feather-filled - vacuum compression can damage the fill long-term.",
             term="vacuum storage bags double zip valve"),
        dict(id="drawer-organizer", name="Adjustable drawer organizer", call="Expansion range, then material",
             photo=22,
             check=["A stated expansion range in inches that actually matches the drawer, not just "
                    "\"adjustable\".",
                    "Bamboo or solid plastic dividers rather than thin mesh that sags under folded "
                    "clothes.",
                    "Divider height tall enough for what's going in it - socks need less than sweaters."],
             skip="The drawer is an odd shape (corner unit, shallow pan) - a tray won't adjust to that.",
             term="adjustable drawer organizer dividers"),
        dict(id="door-organizer", name="Over-the-door organizer", call="Weight-per-pocket, then hook depth",
             photo=23,
             check=["A stated weight capacity per pocket, not just a total - one heavy item can tear a "
                    "light pocket.",
                    "Hook depth matched to the door thickness, so it doesn't block the door from "
                    "closing.",
                    "Clear pockets if it's for anything you need to find by sight."],
             skip="The door swings into a tight space - check clearance before anything else.",
             term="over the door hanging organizer pockets"),
        dict(id="closet-rod", name="Closet double-hang rod", call="Load rating, then adjustable width",
             photo=24,
             check=["A stated load rating in pounds for the rod itself, separate from the bracket "
                    "rating.",
                    "An adjustable width range that matches the closet, not a fixed size.",
                    "Mounting hardware rated for the wall or closet material it's going into."],
             skip="The closet rod is load-bearing from the original build - don't add a hanging unit "
                  "to it without checking first.",
             term="closet double hang rod adjustable"),
        dict(id="label-maker", name="Label maker", call="Tape width options, then power source", photo=25,
             check=["Multiple tape width options if labeling anything beyond standard bins (spice "
                    "jars need a narrower tape than file folders).",
                    "Battery life or a rechargeable port stated, not just \"portable\".",
                    "A built-in font/size preview screen rather than a tiny one-line display."],
             skip="It's a one-time project - a marker and painter's tape labels just as well for a "
                  "single pass.",
             term="label maker machine with tape"),
        dict(id="underbed-bins", name="Underbed storage bins with wheels", call="Clearance height, then wheel type",
             photo=26,
             check=["Measured clearance under the bed frame, compared with the bin's stated height - "
                    "this is the #1 return reason.",
                    "Wheel type: locking casters if the floor has any slope, plain wheels otherwise.",
                    "A lid that latches, so pulling it out doesn't spill the contents."],
             skip="The bed frame has drawers built in already - a rolling bin will just compete for "
                  "the same space.",
             term="underbed storage bins with wheels low profile"),
        dict(id="pantry-turntable", name="Pantry turntable / lazy susan", call="Diameter, then weight rating",
             photo=27,
             check=["Diameter measured against the actual shelf depth, with room to spin without "
                    "hitting the shelf above.",
                    "A stated weight capacity - glass jars add up faster than it looks.",
                    "A raised lip or divider if it's for loose bottles rather than boxed goods."],
             skip="The shelf is too shallow for anything to spin freely - a stepped shelf riser is the "
                  "better fit.",
             term="pantry lazy susan turntable"),
        dict(id="cable-box", name="Cable management box", call="Ventilation, then size for the power strip",
             photo=28,
             check=["Ventilation slots or cutouts - an enclosed box with a power strip inside can trap "
                    "heat.",
                    "Interior dimensions checked against the actual power strip and brick sizes, not "
                    "just \"fits most\".",
                    "Cord entry points on the sides, not just the back, if it sits against a wall."],
             skip="The setup already uses a cable sleeve or raceway that's working - don't add a second "
                  "system on top.",
             term="cable management box power strip"),
    ],
}


# ---------------------------------------------------------------- last-minute holiday gift guide
# WIDE_NET.md niche #6: the 1-20 Dec "late gift" surge, reusing items + photos already built for the
# other four guides - $0 marginal cost, new combinable content for the Pinterest surge window.
def last_minute_gifts(c: dict) -> str:
    root = "../"
    feed_walk = {it["id"]: it for it in PICKS["feeding"]["items"] + PICKS["walks"]["items"]}
    kitchen_by_id = {it["id"]: it for it in KITCHEN_GIFTS["items"]}
    home_by_id = {it["id"]: it for it in HOME_GIFTS["items"]}
    tee = next(l for l in c["pets"] if short(l["title"]) == "Custom Pet Portrait Tee")

    def amazon_card(it: dict) -> str:
        checks = "".join(f"<li>{html.escape(x)}</li>" for x in it["check"][:2])
        return f"""<article class="it sm" id="{it['id']}">
  <figure><img src="../img/picks/photo_{it['photo']:02d}.jpg" alt="{html.escape(it['name'])} - generic example" loading="lazy">
    <figcaption>AI-generated photo &middot; generic example, not a specific product</figcaption></figure>
  <div class="tx">
    <h2>{html.escape(it['name'])}</h2>
    <span class="call">{html.escape(it['call'])}</span>
    <ul>{checks}</ul>
    <a class="btn" href="{amazon_search(it['term'])}" target="_blank" rel="sponsored nofollow noopener">Search Amazon for {html.escape(it['name'].lower())} &rarr;</a>
    <small class="ad">#ad &middot; affiliate link</small>
  </div>
</article>"""

    dog_section = f"""<section class="cross"><h3>For the dog person</h3>
<p>Start with something we make, then two gear picks that solve a real problem fast.</p>
<div class="grid">{card(tee, root)}</div></section>
{amazon_card(feed_walk['slow-feeder'])}{amazon_card(feed_walk['harness'])}"""

    cook_section = f"""<section class="cross"><h3>For the cook</h3>
<p>Kitchen gear is the easiest category to get wrong as a gift - these two are decided by one spec each.
See the full <a href="kitchen-gifts.html">kitchen gift guide &rarr;</a></p></section>
{amazon_card(kitchen_by_id['cast-iron'])}{amazon_card(kitchen_by_id['thermometer'])}"""

    organizer_section = f"""<section class="cross"><h3>For the home organizer</h3>
<p>Small, giftable, and used the same week - unlike a lot of organizing gear. See the full
<a href="home-organization.html">home organization guide &rarr;</a></p></section>
{amazon_card(home_by_id['clear-bins'])}{amazon_card(home_by_id['label-maker'])}"""

    creator_section = """<section class="cross"><h3>For the creator</h3>
<p>Mic and light picks, by the spec that matters - not a claimed-use list. On our Clarity Stack site:
<a href="https://clairmont425.github.io/clarity-stack/gear/gifts-for-video-creators.html" target="_blank"
rel="noopener">gifts for video creators &rarr;</a></p></section>"""

    body = f"""<main class="pmain">
{disclosure_bar(root)}
<section class="phero"><p class="kick">Gift guide &middot; last-minute</p><h1>Still shopping?<br><em>Here's where to start.</em></h1>
<p class="sub">Four categories, one pick each, chosen by the spec that actually matters - not the one on the
box. Check each retailer's own shipping cutoff for your zip code; we don't control carrier timing.</p>
<div class="notest"><b>We have not tested the Amazon products below.</b> Each one tells you which spec
decides whether it works, so you can judge any listing - including ones we don't link.</div></section>
{dog_section}
{cook_section}
{organizer_section}
{creator_section}
<section class="cross"><h3>While you're here</h3><p>We make custom portraits of your pet on tees, mugs and canvas.</p>
<a class="btn ghost" href="../index.html#pets">See the pet portraits &rarr;</a></section>
</main>"""
    return page("Last-minute gift guide - DripDrop Picks",
                "Four quick gift picks - dog person, cook, home organizer, creator - chosen by the one "
                "spec that decides whether each one works.", body, root, cls="pk-page")


def home_organization() -> str:
    root = "../"
    g = HOME_GIFTS
    items_html = []
    for n, it in enumerate(g["items"], 1):
        checks = "".join(f"<li>{html.escape(x)}</li>" for x in it["check"])
        items_html.append(f"""<article class="it" id="{it['id']}">
  <figure><img src="../img/picks/photo_{it['photo']:02d}.jpg" alt="{html.escape(it['name'])} - generic example" loading="lazy">
    <figcaption>AI-generated photo &middot; generic example, not a specific product</figcaption></figure>
  <div class="tx">
    <span class="num">{n:02d}</span>
    <h2>{html.escape(it['name'])}</h2>
    <span class="call">{html.escape(it['call'])}</span>
    <h4>What to check</h4><ul>{checks}</ul>
    <p class="skip"><b>Skip it if</b> {html.escape(it['skip'])}</p>
    <a class="btn" href="{amazon_search(it['term'])}" target="_blank" rel="sponsored nofollow noopener">Search Amazon for {html.escape(it['name'].lower())} &rarr;</a>
    <small class="ad">#ad &middot; affiliate link</small>
  </div>
</article>""")
    body = f"""<main class="pmain">
{disclosure_bar(root)}
<section class="phero"><p class="kick">{g['kicker']}</p><h1>{g['title']}</h1><p class="sub">{g['lede']}</p>
<div class="notest"><b>We have not tested these products.</b> This page is a buying filter, not a
review: it tells you which specs decide whether the gear works, so you can judge any listing -
including ones we don't link.</div></section>
{''.join(items_html)}
<section class="cross"><h3>While you're here</h3><p>We make custom portraits of your pet on tees, mugs and canvas.</p>
<a class="btn ghost" href="../index.html#pets">See the pet portraits &rarr;</a></section>
</main>"""
    return page("Home organization gifts - DripDrop Picks", g["lede"], body, root, cls="pk-page")


def gifts_for_dog_people(c: dict) -> str:
    root = "../"
    by_id = {it["id"]: it for it in PICKS["feeding"]["items"] + PICKS["walks"]["items"]}
    amazon_items = [by_id[i] for i in DOG_GIFT_ITEM_IDS]
    etsy_ids = ["Custom Pet Portrait Tee", "Oversized Custom Pet Tee", "Custom Pet Portrait Mug",
                "Custom Pet Portrait Ornament"]
    etsy_picks = [l for l in c["pets"] if short(l["title"]) in etsy_ids]
    etsy_cards = "\n".join(card(l, root) for l in etsy_picks)
    amazon_items_html = []
    for n, it in enumerate(amazon_items, 1):
        checks = "".join(f"<li>{html.escape(x)}</li>" for x in it["check"])
        amazon_items_html.append(f"""<article class="it" id="{it['id']}">
  <figure><img src="../img/picks/photo_{it['photo']:02d}.jpg" alt="{html.escape(it['name'])} - generic example" loading="lazy">
    <figcaption>AI-generated photo &middot; generic example, not a specific product</figcaption></figure>
  <div class="tx">
    <span class="num">{n:02d}</span>
    <h2>{html.escape(it['name'])}</h2>
    <span class="call">{html.escape(it['call'])}</span>
    <h4>What to check</h4><ul>{checks}</ul>
    <p class="skip"><b>Skip it if</b> {html.escape(it['skip'])}</p>
    <a class="btn" href="{amazon_search(it['term'])}" target="_blank" rel="sponsored nofollow noopener">Search Amazon for {html.escape(it['name'].lower())} &rarr;</a>
    <small class="ad">#ad &middot; affiliate link</small>
  </div>
</article>""")
    body = f"""<main class="pmain">
{disclosure_bar(root)}
<section class="phero"><p class="kick">Gift guide</p><h1>Gifts for dog people</h1>
<p class="sub">Start with something we actually make, then the Amazon buying filters for the gear
that goes with it.</p></section>
<section class="cross"><h3>Our own products</h3>
<p>Custom pet portraits, made to order from your dog or cat's photo - our own designs, our own
photos, shipped through our Etsy shop.</p>
<div class="grid">{etsy_cards}</div></section>
<section class="phero"><div class="notest"><b>We have not tested these Amazon products.</b> This
section is a buying filter, not a review: it tells you which specs decide whether the gear works,
reusing the same criteria from our <a href="feeding.html">feeding</a> and <a href="walks.html">walks</a>
guides.</div></section>
{''.join(amazon_items_html)}
</main>"""
    return page("Gifts for dog people - DripDrop", "Custom pet portraits plus a buying filter for "
                "dog-gear gifts: the specs that decide feeding, walking and grooming gear.", body,
                root, cls="pk-page")


def kitchen_gifts() -> str:
    root = "../"
    g = KITCHEN_GIFTS
    items_html = []
    for n, it in enumerate(g["items"], 1):
        checks = "".join(f"<li>{html.escape(x)}</li>" for x in it["check"])
        items_html.append(f"""<article class="it" id="{it['id']}">
  <figure><img src="../img/picks/photo_{it['photo']:02d}.jpg" alt="{html.escape(it['name'])} - generic example" loading="lazy">
    <figcaption>AI-generated photo &middot; generic example, not a specific product</figcaption></figure>
  <div class="tx">
    <span class="num">{n:02d}</span>
    <h2>{html.escape(it['name'])}</h2>
    <span class="call">{html.escape(it['call'])}</span>
    <h4>What to check</h4><ul>{checks}</ul>
    <p class="skip"><b>Skip it if</b> {html.escape(it['skip'])}</p>
    <a class="btn" href="{amazon_search(it['term'])}" target="_blank" rel="sponsored nofollow noopener">Search Amazon for {html.escape(it['name'].lower())} &rarr;</a>
    <small class="ad">#ad &middot; affiliate link</small>
  </div>
</article>""")
    body = f"""<main class="pmain">
{disclosure_bar(root)}
<section class="phero"><p class="kick">{g['kicker']}</p><h1>{g['title']}</h1><p class="sub">{g['lede']}</p>
<div class="notest"><b>We have not tested these products.</b> This page is a buying filter, not a
review: it tells you which specs decide whether the gear works, so you can judge any listing -
including ones we don't link.</div></section>
{''.join(items_html)}
<section class="cross"><h3>While you're here</h3><p>We make custom portraits of your pet on tees, mugs and canvas.</p>
<a class="btn ghost" href="../index.html#pets">See the pet portraits &rarr;</a></section>
</main>"""
    return page("Kitchen gifts - DripDrop Picks", g["lede"], body, root, cls="pk-page")


def links_page(c: dict) -> str:
    root = "../"
    tee = next(l for l in c["pets"] if short(l["title"]) == "Custom Pet Portrait Tee")
    rows = [("Custom pet portrait tee", tee["url"]), ("Ugly Christmas sweaters", "../index.html#holiday"),
            ("Tie-dye & graphic tees", "../index.html#tees"), ("DripDrop Picks: pet gear filters (#ad)", "../picks/index.html"),
            ("Gifts for dog people (#ad)", "../picks/gifts-for-dog-people.html"),
            ("Kitchen gift guide (#ad)", "../picks/kitchen-gifts.html"),
            ("Home organization gift guide (#ad)", "../picks/home-organization.html"),
            ("Last-minute gift guide (#ad)", "../picks/last-minute-gifts.html"),
            ("Free printable coloring pages", "../free/index.html"),
            ("Shop everything on Etsy", ETSY_SHOP)]
    btns = "".join(f'<a class="lk" href="{u}">{html.escape(t)}<span>&rarr;</span></a>' for t, u in rows)
    body = f"""<main class="links"><img class="av" src="../img/shop/{tee['id']}_1.jpg" alt="">
<h1>Drip<span>Drop</span></h1><p>Your pet, on everything.</p>{btns}</main>"""
    return page("DripDrop - links", "DripDrop shop and picks.", body, root, cls="lk-page")


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(SRC / "img", DIST / "img")
    shutil.copytree(SRC / "assets", DIST / "assets")
    shutil.copytree(SRC / "free", DIST / "free")
    shutil.copytree(SRC / "freebies", DIST / "freebies")
    c = collections()
    files = {"index.html": home(c), "picks/index.html": picks_index(), "disclosure.html": disclosure(),
             "links/index.html": links_page(c), "free/index.html": free_page(), "books/index.html": books_index(),
             "picks/gifts-for-dog-people.html": gifts_for_dog_people(c),
             "picks/kitchen-gifts.html": kitchen_gifts(),
             "picks/home-organization.html": home_organization(),
             "picks/last-minute-gifts.html": last_minute_gifts(c),
             **{f"picks/{k}.html": guide(k) for k in PICKS}}
    for rel, text in files.items():
        p = DIST / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    (DIST / ".nojekyll").write_text("")
    sitemap_urls = [SITE + ("" if rel == "index.html" else rel.replace("index.html", "")) for rel in files]
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "".join(f"  <url><loc>{u}</loc></url>\n" for u in sitemap_urls)
               + "</urlset>\n")
    (DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n", encoding="utf-8")
    # every picks page must carry the Amazon sentence, the #ad mark and the not-tested banner
    for k in PICKS:
        t = files[f"picks/{k}.html"]
        assert AMAZON_SENTENCE in t and "#ad" in t and "We have not tested" in t and f"tag={TAG}" in t, k
    for k in ("gifts-for-dog-people", "kitchen-gifts", "home-organization", "last-minute-gifts"):
        t = files[f"picks/{k}.html"]
        assert AMAZON_SENTENCE in t and "#ad" in t and "We have not tested" in t and f"tag={TAG}" in t, k
    # books page: Amazon sentence + #ad present, no bare prices, every amazon.com link is sponsored+tagged
    bt = files["books/index.html"]
    assert AMAZON_SENTENCE in bt and "#ad" in bt, "books"
    assert not re.search(r"\$\d", bt), "books page must not show a price next to an Amazon link"
    for m in re.finditer(r'href="(https://www\.amazon\.com/[^"]+)"[^>]*', bt):
        assert f"tag={TAG}" in m.group(1), m.group(1)
    for m in re.finditer(r'<a[^>]+amazon\.com[^>]*>', bt):
        assert 'rel="sponsored nofollow noopener"' in m.group(0), m.group(0)
    print(f"built {len(files)} pages, {sum(len(v) for v in c.values())} shop items, tag {TAG} -> {DIST}")


if __name__ == "__main__":
    main()
