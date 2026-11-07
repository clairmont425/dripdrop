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
    body = f"""<main class="pmain">
{disclosure_bar(root)}
<section class="phero"><p class="kick">DripDrop Picks</p><h1>Buy the spec,<br><em>not the hype.</em></h1>
<p class="sub">Short buying filters for pet gear. We haven't tested these products - each guide tells you which
two or three specs decide whether a product works, so you can judge any listing yourself.</p></section>
<div class="pks two">{cards}</div>
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


def disclosure() -> str:
    body = f"""<main class="pmain narrow"><section class="phero"><p class="kick">Disclosure</p><h1>How DripDrop makes money</h1>
<p class="sub">DripDrop sells its own made-to-order products through Etsy. On DripDrop Picks pages, some links are
affiliate links: if you buy through them, we earn a commission at no extra cost to you. Those links are marked
<b>#ad</b>. {AMAZON_SENTENCE}</p>
<p class="sub">Picks pages are buying filters, not reviews. We say on every page that we haven't tested the products,
and the photos there are AI-generated generic examples of each category, labelled as such. Prices aren't shown
because they change - check the retailer.</p></section></main>"""
    return page("Affiliate disclosure - DripDrop", "How DripDrop makes money.", body, "", cls="pk-page")


def links_page(c: dict) -> str:
    root = "../"
    tee = next(l for l in c["pets"] if short(l["title"]) == "Custom Pet Portrait Tee")
    rows = [("Custom pet portrait tee", tee["url"]), ("Ugly Christmas sweaters", "../index.html#holiday"),
            ("Tie-dye & graphic tees", "../index.html#tees"), ("DripDrop Picks: pet gear filters (#ad)", "../picks/index.html"),
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
    shutil.copytree(SRC / "freebies", DIST / "freebies")
    c = collections()
    files = {"index.html": home(c), "picks/index.html": picks_index(), "disclosure.html": disclosure(),
             "links/index.html": links_page(c), "books/index.html": books_index(),
             **{f"picks/{k}.html": guide(k) for k in PICKS}}
    for rel, text in files.items():
        p = DIST / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    (DIST / ".nojekyll").write_text("")
    # every picks page must carry the Amazon sentence, the #ad mark and the not-tested banner
    for k in PICKS:
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
