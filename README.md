# DripDrop site
Static site for DripDrop: the Etsy shop showcase + DripDrop Picks (pet-gear buying filters with affiliate links).
Live: https://clairmont425.github.io/dripdrop/  ·  link-in-bio: /links/

    python build.py     # src/ + src/listings.json -> docs/ (GitHub Pages serves main:/docs)
    python shots.py     # desktop + phone screenshots of http://localhost:8765 for design review

Shop data comes from the Etsy API (refresh src/listings.json + src/img/shop/). Picks rules: see
clairity-productions/workflows/money_engine/operator/ventures/affiliate/AMAZON_RULES.md.
