#!/usr/bin/env python3
"""Build the hierarchical catalog: data/catalog-products.json v2 + navigation pages.

Levels: products.html -> detail-{category}.html (group cards)
        -> category-{cat}--{group}.html (sub-group cards OR model list)
        -> category-{cat}--{group}--{sub}.html (model list, ALL models shown)

Model entries come from data/intel/*.json (supplier catalog extractions).
Existing detail products (data/catalog-products.json "products") are linked
into their leaf groups. Every intel entry must be assigned exactly once.
"""
from __future__ import annotations

import html
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hierarchy_config import GROUPS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
INTEL = DATA / "intel"
ASSETS = ROOT / "assets" / "products"
DOMAIN = "https://taotaosourcing.com"
WHATSAPP = "8616626662274"
TODAY = "2026-09-18"

IMG_DIRS = {
    "cbs-helmets": "helmets/cbs-helmets", "kuuvi-moto": "helmets/kuuvi-moto",
    "moon-sports": "helmets/moon-sports", "moon-ski": "helmets/moon-ski",
    "meicheng": "helmets/meicheng", "yongbao": "helmets/yongbao",
    "hongxin-visors": "helmet-visors/rows", "door-closers": "door-closers",
    "vt-hinges": "hinges/vt", "doors-windows": "doors-windows", "steel": "steel",
    "prefab-yk": "prefab", "sanitary": "sanitary", "heating": "heating",
    "led": "led", "pv": "pv", "storage": "storage", "decking": "decking",
    "track": "track", "lubricants": "lubricants",
}
BOOK_IMG = {"heatpumps": "heatpumps/{book}"}
CATALOG_IMG = {
    "bags": {"BAG2": "bags/bag2", "25W-NEW-BAGS": "bags/25w-new", "NEW-MODEL-BAGS": "bags/new-model"},
    "belts": {"25W-NEW-BELTS": "belts/25w-new", "BELT1": "belts/belt1",
              "MENS-BELT": "belts/mens", "WOMENS-BELT": "belts/womens"},
    "slg": {"CARD-HOLDER": "slg/card-holder", "KEY-HOLDER": "slg/key-holder",
            "PASSPORT-COVER": "slg/passport", "WALLETS": "slg/wallets"},
    "apparel": "apparel", "eyelashes": None,
}
RUN_IMG = Path("/Users/katherinetu/CODEX/独立站/website-optimization/run/taotaosourcing-hierarchy-2026-09-18/extracted_images")


def esc(v):
    return html.escape(str(v), quote=True)


def slugify(s):
    s = re.sub(r"[^A-Za-z0-9]+", "-", str(s)).strip("-").lower()
    return s[:60] or "model"


def load_intel():
    data = {}
    for f in INTEL.glob("*.json"):
        data[f.stem] = json.loads(f.read_text())
    return data


def image_ok(path: Path) -> bool:
    try:
        from PIL import Image, ImageStat
        im = Image.open(path).convert("RGB")
        if im.width < 70 or im.height < 50:
            return False
        st = ImageStat.Stat(im)
        if sum(st.stddev) / 3 < 8:      # flat/blank
            return False
        if sum(st.mean) / 3 > 249:      # near-white
            return False
        return True
    except Exception:
        return False


def find_image(source, entry):
    """Locate extracted image for an intel entry; copy into assets later."""
    slug = slugify(entry.get("id") or entry.get("model"))
    rel = None
    if source in IMG_DIRS:
        rel = IMG_DIRS[source]
    elif source == "heatpumps":
        rel = f"heatpumps/{entry.get('book', 'hotwater')}"
    elif source in CATALOG_IMG:
        m = CATALOG_IMG[source]
        rel = m.get(entry.get("catalog")) if isinstance(m, dict) else m
    if not rel:
        return None
    src = RUN_IMG / rel / f"{slug}.jpg"
    return src if src.exists() and image_ok(src) else None


TYPE_WORDS = {
    "mens-auto": "men's automatic-buckle belt", "mens-pin-dress": "men's dress belt (pin buckle)",
    "mens-pin-casual": "men's casual belt", "mens-pin-casual-wide": "men's casual wide belt",
    "mens-reversible-pin": "men's reversible belt", "mens-saffiano-pin": "men's Saffiano belt",
    "mens-golf-pin": "men's golf belt", "mens-golf-reversible": "men's reversible golf belt",
    "mens-webbing": "men's webbing belt", "mens-webbing-reversible": "men's reversible webbing belt",
    "mens-braided-reversible": "men's reversible braided belt", "mens-braided-stretch": "men's stretch braided belt",
    "mens-casual-clasp": "men's clasp belt", "mens-western": "men's western belt",
    "mens-suede-pin": "men's suede belt", "unisex-pin": "unisex pin-buckle belt",
    "womens-pin": "women's belt (pin buckle)", "womens-slide": "women's slide-buckle belt",
    "womens-oval": "women's oval-buckle belt", "womens-charm": "women's charm belt",
    "womens-frame": "women's frame-buckle belt", "womens-ring": "women's ring-buckle belt",
    "womens-horsebit": "women's horsebit belt", "womens-mariner": "women's mariner-buckle belt",
    "womens-plaque": "women's plaque-buckle belt", "womens-bezel": "women's bezel-buckle belt",
    "womens-arch": "women's arch-buckle belt", "womens-square": "women's square-buckle belt",
    "womens-stirrup": "women's stirrup-buckle belt", "womens-woven": "women's woven belt",
    "womens-oval-pin": "women's oval pin-buckle belt", "womens-teardrop": "women's teardrop-buckle belt",
    "womens-check": "women's check-print belt", "womens-asym": "women's asymmetric belt",
    "womens-double": "women's double-strap belt", "womens-corset": "women's corset belt",
    "womens-o-ring": "women's O-ring belt", "womens-knot": "women's knot-buckle belt",
    "womens-molten": "women's sculptural belt", "womens-sculptural": "women's sculptural belt",
    "womens-western": "women's western belt", "womens-covered": "women's covered-buckle belt",
    "womens-braided-crescent": "women's braided crescent belt", "womens-suede-bead-keeper": "women's suede beaded belt",
    "womens-suede-pin": "women's suede belt", "womens-suede-oval": "women's suede oval-buckle belt",
    "womens-frame-patent": "women's patent frame-buckle belt",
    "tote": "tote bag", "shoulder": "shoulder bag", "hobo": "hobo bag",
    "crossbody": "crossbody bag", "top-handle": "top-handle bag",
    "bucket": "bucket bag", "clutch": "clutch", "backpack": "backpack",
    "card-holder": "card holder", "card-wallet": "card wallet",
    "key-holder": "key holder", "passport-cover": "passport cover",
    "short-wallet": "short wallet", "long-wallet": "long wallet",
}
MATERIAL_WORDS = {
    "leather": "leather", "suede": "suede", "straw": "straw/raffia",
    "canvas": "canvas & leather", "snake": "snake-print leather",
    "lambskin": "lambskin", "leopard": "leopard-print",
}


def entry_title(source, entry):
    mid = entry.get("id") or entry.get("model")
    if source == "belts":
        words = TYPE_WORDS.get(entry.get("type", ""), "belt")
        return f"{mid} " + " ".join(w.capitalize() for w in words.split())
    if source in ("bags", "slg"):
        words = TYPE_WORDS.get(entry.get("type"), entry.get("type", "style"))
        mat = MATERIAL_WORDS.get(entry.get("material"), "")
        title = (f"{mid} {words}".title()
                 .replace("Men'S", "Men's").replace("Women'S", "Women's")
                 .replace("Bag2-", "BAG2-").replace("Nb25-", "NB25-")
                 .replace("Nmb-", "NMB-").replace("Ch-", "CH-")
                 .replace("Kh-", "KH-").replace("Pc-", "PC-")
                 .replace("Wl-", "WL-"))
        return title + (f" ({mat})" if mat and source == "bags" else "")
    if source == "apparel":
        return f"Style {entry['id'].split('-')[1]}"
    return str(entry.get("model") or mid)


def resolve_group_models(rules, intel, used, log):
    """Resolve one leaf group's model entries from assignment rules."""
    entries = []
    for rule in rules:
        src = rule["source"]
        if src == "catalog":
            continue
        pool = intel.get(src, {}).get("models", [])
        keys = [k.lower() for k in rule["keys"]]
        for e in pool:
            mid = str(e.get("id") or e.get("model"))
            ekey = mid.lower()
            chosen = False
            if "__public_molds__" in rule["keys"] and src == "hongxin-visors" and e.get("model") == "__public__":
                chosen = True
            if not chosen and keys:
                chosen = ekey in keys
            if not chosen and rule.get("match"):
                try:
                    chosen = bool(rule["match"](str(e.get("model") or mid), e))
                except Exception:
                    chosen = False
            if not chosen or mid in rule["exclude"]:
                continue
            if mid in used:
                continue
            used.add(mid)
            img = find_image(src, e)
            spec = e.get("spec") or ("" if src in ("belts", "bags", "slg") else e.get("type") or "")
            if e.get("shell"):
                spec = f"{e['type']}; shell: {e['shell']}" if spec else f"Shell: {e['shell']}"
            if e.get("sizes"):
                spec += f"; sizes {e['sizes']}" if spec else f"Sizes: {e['sizes']}"
            if e.get("cert"):
                spec += f"; {e['cert']}"
            entries.append({
                "id": mid,
                "slug": slugify(mid),
                "name": entry_title(src, e),
                "model": str(e.get("model") or mid),
                "spec": spec or ("Style reference from the supplier catalog; material, width and finish are confirmed per order." if src in ("belts","bags","slg") else ""),
                "source": src,
                "page": e.get("page"),
                "image": img,
            })
    return entries


def link_catalog_products(rules, products_by_frag):
    """Return list of existing product dicts referenced by catalog rules."""
    out = []
    seen = set()
    for rule in rules:
        if rule["source"] != "catalog":
            continue
        for frag in rule["keys"]:
            for slug, prod in products_by_frag.items():
                if frag.lower() in slug and slug not in seen:
                    seen.add(slug)
                    out.append(prod)
    return out


def copy_image(src: Path, cat_slug: str, leaf_slug: str, slug: str) -> str | None:
    dest_dir = ASSETS / "hierarchy" / cat_slug / leaf_slug
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{slug}.jpg"
    if not dest.exists():
        shutil.copy2(src, dest)
    return f"assets/products/hierarchy/{cat_slug}/{leaf_slug}/{slug}.jpg"


# ---------------------------------------------------------------------------
# page rendering
# ---------------------------------------------------------------------------

def page_head(title, description, canonical, image):
    img_url = image if str(image).startswith("http") else f"{DOMAIN}/{image}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{esc(img_url)}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/png" href="assets/logo.png">
  <link rel="stylesheet" href="css/style.css">
</head>"""


def header(active="products"):
    def cls(n):
        return ' class="active"' if n == active else ""
    return f"""<body>
  <header class="site-header">
    <div class="container header-inner">
      <a href="index.html" class="brand" aria-label="Taotao Sourcing home">
        <img src="assets/logo.png" alt="Taotao Sourcing logo">
        <span class="brand-name">Taotao Sourcing<small>Sourcing · Risk Control</small></span>
      </a>
      <nav class="main-nav" id="mainNav" aria-label="Main navigation">
        <a href="index.html"{cls('home')}>Home</a>
        <a href="products.html"{cls('products')}>Products</a>
        <a href="services.html"{cls('services')}>Services</a>
        <a href="articles.html"{cls('articles')}>Insights</a>
        <a href="about.html"{cls('about')}>About</a>
        <a href="contact.html" class="nav-cta">Start an Inquiry</a>
      </nav>
      <button class="nav-toggle" id="navToggle" aria-label="Toggle menu" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>"""


FOOTER = open(ROOT / "scripts" / "_footer_partial.html").read() if (ROOT / "scripts" / "_footer_partial.html").exists() else None


def footer():
    if FOOTER:
        return FOOTER
    from build_product_pages import footer as fp
    return fp()


def breadcrumb_json(items):
    parts = [{"@type": "ListItem", "position": i, "name": n, "item": u}
             for i, (n, u) in enumerate(items, 1)]
    return json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList",
                       "itemListElement": parts}, ensure_ascii=False, separators=(",", ":"))


def model_card(entry, product_ref=None, cat_slug=None, group_path=None):
    model_badge = f'<span class="catalog-badge">{esc(entry["model"])}</span>'
    img = (f'<img src="{esc(entry["image"])}" alt="{esc(entry["name"])} catalog reference" loading="lazy">'
           if entry.get("image") else
           '<div class="model-img-placeholder" aria-hidden="true"><span>Photo on request</span></div>')
    detail_link = ""
    if product_ref:
        detail_link = f'<a class="more" href="product-{esc(product_ref["slug"])}.html">Full product details →</a>'
    page_ref = f'<span class="model-source">Catalog p.{entry["page"]}</span>' if entry.get("page") else ""
    wa = f"https://wa.me/{WHATSAPP}?text=" + __import__("urllib.parse", fromlist=["quote"]).quote(
        f"Hello Katherine, I'm interested in {entry['model']}. Target market and quantity: ")
    return f"""        <article class="catalog-product-card model-card">
          <a class="catalog-product-media" href="{esc(product_ref and 'product-' + product_ref['slug'] + '.html' or (group_path or '#'))}">
            {img}
          </a>
          <div class="catalog-product-body">
            {model_badge}
            <h3>{esc(entry['name'])}</h3>
            <p>{esc(entry['spec'][:180]) if entry.get('spec') else 'Specifications confirmed against the supplier catalog per order.'}</p>
            {page_ref}
            {detail_link}
            <a class="more" href="{wa}" target="_blank" rel="noreferrer">Ask price →</a>
          </div>
        </article>"""


def render_group_cards(cat, groups, parent_title, parent_url, breadcrumbs, back_link=None, back_label=None):
    cards = []
    for grp in groups:
        count = grp.get("total_models", 0)
        img = grp.get("cover") or "assets/logo.png"
        href = grp["_url_file"]
        sub_note = f'{len(grp["subs"])} sub-categories' if grp["subs"] else f'{count} models'
        cards.append(f"""        <article class="catalog-product-card">
          <a class="catalog-product-media" href="{href}">
            <img src="{esc(img)}" alt="{esc(grp['title'])} category photo" loading="lazy">
          </a>
          <div class="catalog-product-body">
            <span class="catalog-badge">{esc(sub_note)}</span>
            <h3><a href="{href}">{esc(grp['title'])}</a></h3>
            <p>{esc(grp.get('intro') or '')}</p>
            <a class="more" href="{href}">Browse models →</a>
          </div>
        </article>""")
    cards_html = "\n".join(cards)
    schema = breadcrumb_json(breadcrumbs)
    return f"""{page_head(f"{parent_title} | Taotao Sourcing", f"Browse {parent_title} sub-categories and full model lists reviewed from supplier catalogs.", parent_url, groups[0]["cover"] if groups else "assets/logo.png")}
{header()}
  <main>
    <section class="page-hero">
      <div class="container">
        <div class="breadcrumb"><a href="index.html">Home</a> / <a href="products.html">Products</a> / {esc(parent_title)}</div>
        <h1>{esc(parent_title)}</h1>
        <p>{esc(cat.get('group_intro') or cat.get('intro', ''))}</p>
      </div>
    </section>
    <section class="section">
      <div class="container">
        <p class="backlink"><a href="{esc(back_link or 'products.html')}">← Back to {esc(back_label or 'full catalog')}</a></p>
        <div class="catalog-product-grid">
{cards_html}
        </div>
        <div class="cta-band">
          <div>
            <h2>Need a shortlist or a quotation?</h2>
            <p>Share your target market, quantity and required certifications. We will compare suitable suppliers and flag the items that still need confirmation.</p>
          </div>
          <div class="hero-actions">
            <a class="btn btn-red" href="contact.html">Start an Inquiry</a>
            <a class="btn btn-wa" href="https://wa.me/{WHATSAPP}" target="_blank" rel="noreferrer">WhatsApp Katherine</a>
          </div>
        </div>
      </div>
    </section>
  </main>
  <script type="application/ld+json">{schema}</script>
{footer()}"""


def render_model_list(cat, group, sub, parent_chain, breadcrumbs):
    """Render the final-level page: ALL models of this leaf group."""
    title = sub["title"]
    canonical = f"{DOMAIN}/{sub['_url_file']}"
    entries = sub["_entries"]
    products = sub["_products"]
    cards = [model_card(e) for e in entries]
    cards += [model_card(
        {"id": p["slug"], "slug": p["slug"], "name": p["name"], "model": p.get("model") or p["name"],
         "spec": p.get("summary", ""), "image": p.get("image"), "page": None}, product_ref=p)
        for p in products]
    count = len(entries) + len(products)
    trail = " / ".join(f'<a href="{u}">{esc(t)}</a>' for t, u in parent_chain) + f" / {esc(title)}"
    schema = breadcrumb_json(breadcrumbs)
    note = '<p class="source-note">Model lists are transcribed from the reviewed supplier catalogs; specifications and certification documents are re-confirmed per order. Entries without photos are quoted with catalog pages on request.</p>'
    return f"""{page_head(f"{title} — All Models | Taotao Sourcing", f"Complete {title} model list ({count} models) reviewed from supplier catalogs, with specs and inquiry entry.", canonical, (entries[0]["image"] if entries and entries[0].get("image") else (products[0]["image"] if products else "assets/logo.png")))}
{header()}
  <main>
    <section class="page-hero">
      <div class="container">
        <div class="breadcrumb"><a href="index.html">Home</a> / <a href="products.html">Products</a> / {trail}</div>
        <span class="catalog-eyebrow">{count} models listed</span>
        <h1>{esc(title)}</h1>
        <p>{esc(sub.get('intro') or group.get('intro') or '')}</p>
      </div>
    </section>
    <section class="section">
      <div class="container">
        <p class="backlink"><a href="{parent_chain[-1][1]}">← Back to {esc(parent_chain[-1][0])}</a></p>
        <div class="catalog-product-grid">
{chr(10).join(cards)}
        </div>
        {note}
        <div class="cta-band">
          <div>
            <h2>Ask about any model on this page</h2>
            <p>Send the model numbers you need. We confirm availability, certification documents, MOQ and lead time per model with the supplier before quotation.</p>
          </div>
          <div class="hero-actions">
            <a class="btn btn-red" href="contact.html">Start an Inquiry</a>
            <a class="btn btn-wa" href="https://wa.me/{WHATSAPP}" target="_blank" rel="noreferrer">WhatsApp Katherine</a>
          </div>
        </div>
      </div>
    </section>
  </main>
  <script type="application/ld+json">{schema}</script>
{footer()}"""


# ---------------------------------------------------------------------------

def main():
    catalog = json.loads((DATA / "catalog-products.json").read_text())
    intel = load_intel()
    products = catalog["products"]
    products_by_slug = {p["slug"]: p for p in products}
    used = set()
    unlinked_products = {p["slug"] for p in products}
    generated_pages = []

    # resolve model entries per leaf group
    for cat_slug, groups in GROUPS.items():
        for grp in groups:
            grp["_entries"] = []
            grp["_products"] = []
            grp["_sub_entries"] = {}
            if grp["subs"]:
                for sub in grp["subs"]:
                    sub["_entries"] = resolve_group_models(sub["models"], intel, used, None)
                    sub["_products"] = link_catalog_products(sub["models"], products_by_slug)
                    grp["_sub_entries"][sub["slug"]] = sub
            else:
                grp["_entries"] = resolve_group_models(grp["models"], intel, used, None)
                grp["_products"] = link_catalog_products(grp["models"], products_by_slug)

    # coverage check
    total_intel = sum(len(v.get("models", [])) for v in intel.values())
    leftovers = []
    for src, doc in intel.items():
        if src in ("jewelry", "robots"):
            continue
        for e in doc.get("models", []):
            mid = str(e.get("id") or e.get("model"))
            if mid not in used:
                leftovers.append(f"{src}:{mid}")
    print(f"intel entries: {total_intel}, assigned: {len(used)}, unassigned: {len(leftovers)}")
    if leftovers:
        for x in leftovers[:40]:
            print("  LEFTOVER", x)

    # URL assignment + asset copy + rendering
    for cat in catalog["categories"]:
        cslug = cat["slug"]
        groups = GROUPS.get(cslug)
        if not groups:
            continue
        cat["groups"] = []
        for grp in groups:
            if grp["subs"]:
                leaves = grp["subs"]
                grp_url = f"category-{cslug}--{grp['slug']}.html"
            else:
                leaves = [grp]
                grp_url = f"category-{cslug}--{grp['slug']}.html"
            grp["_url_file"] = grp_url

            total_models = 0
            for sub in leaves:
                slug_parts = f"{cslug}--{grp['slug']}" + (f"--{sub['slug']}" if grp["subs"] else "")
                sub["_url_file"] = f"category-{slug_parts}.html"
                # copy images
                for e in sub["_entries"]:
                    if e.get("image"):
                        e["image"] = copy_image(Path(e["image"]), cslug, slug_parts.replace("--", "-"), e["slug"])
                total_models += len(sub["_entries"]) + len(sub["_products"])
                for p in sub["_products"]:
                    unlinked_products.discard(p["slug"])

            # group cover: first model image found in any leaf
            cover = None
            for sub in leaves:
                for e in sub["_entries"]:
                    if e.get("image"):
                        cover = e["image"]
                        break
                if cover:
                    break
                for p in sub["_products"]:
                    cover = p.get("image")
                    break
                if cover:
                    break
            grp["cover"] = cover
            grp["total_models"] = total_models
            cat["groups"].append({
                "slug": grp["slug"], "title": grp["title"], "intro": grp.get("intro", ""),
                "subs": [{"slug": s["slug"], "title": s["title"], "intro": s.get("intro", ""),
                          "url": s["_url_file"], "modelCount": len(s["_entries"]) + len(s["_products"])}
                         for s in grp["subs"]],
                "url": grp_url, "cover": cover, "totalModels": total_models,
            })

            # write sub pages first, then group page
            if grp["subs"]:
                for sub in grp["subs"]:
                    chain = [(cat["title"], f"detail-{cslug}.html"), (grp["title"], grp_url)]
                    crumbs = [("Home", DOMAIN + "/"), ("Products", DOMAIN + "/products.html"),
                              (cat["title"], f"{DOMAIN}/detail-{cslug}.html"),
                              (grp["title"], f"{DOMAIN}/{grp_url}"), (sub["title"], f"{DOMAIN}/{sub['_url_file']}")]
                    (ROOT / sub["_url_file"]).write_text(
                        render_model_list(cat, grp, sub, chain, crumbs), encoding="utf-8")
                    generated_pages.append(sub["_url_file"])
                # group page renders sub cards: reuse render_group_cards with subs as cards
                sub_cards = []
                for sub in grp["subs"]:
                    cover = next((e["image"] for e in sub["_entries"] if e.get("image")),
                                 sub["_products"][0]["image"] if sub["_products"] else None)
                    sub_cards.append({"title": sub["title"], "intro": sub.get("intro", ""),
                                      "cover": cover, "_url_file": sub["_url_file"],
                                      "total_models": len(sub["_entries"]) + len(sub["_products"]),
                                      "subs": [], "slug": sub["slug"]})
                (ROOT / grp_url).write_text(
                    render_group_cards(cat, sub_cards, f"{cat['title']} — {grp['title']}",
                                       f"{DOMAIN}/{grp_url}",
                                       [("Home", DOMAIN + "/"), ("Products", DOMAIN + "/products.html"),
                                        (cat["title"], f"{DOMAIN}/detail-{cslug}.html"),
                                        (grp["title"], f"{DOMAIN}/{grp_url}")],
                                       back_link=f"detail-{cslug}.html", back_label=cat["title"]), encoding="utf-8")
                generated_pages.append(grp_url)
            else:
                chain = [(cat["title"], f"detail-{cslug}.html")]
                crumbs = [("Home", DOMAIN + "/"), ("Products", DOMAIN + "/products.html"),
                          (cat["title"], f"{DOMAIN}/detail-{cslug}.html"),
                          (grp["title"], f"{DOMAIN}/{grp_url}")]
                (ROOT / grp_url).write_text(
                    render_model_list(cat, grp, grp, chain, crumbs), encoding="utf-8")
                generated_pages.append(grp_url)

        # rewrite detail-{category}.html as group-card page
        detail_file = f"detail-{cslug}.html"
        gcards = []
        for grp in cat["groups"]:
            note = f'{len(grp["subs"])} sub-categories · {grp["totalModels"]} models' if grp["subs"] else f'{grp["totalModels"]} models'
            gcards.append({
                "title": grp["title"], "intro": grp["intro"], "cover": grp["cover"],
                "_url_file": grp["url"], "total_models": grp["totalModels"], "subs": grp["subs"],
                "slug": grp["slug"],
            })
        (ROOT / detail_file).write_text(
            render_group_cards(cat, gcards, cat["title"], f"{DOMAIN}/{detail_file}",
                               [("Home", DOMAIN + "/"), ("Products", DOMAIN + "/products.html"),
                                (cat["title"], f"{DOMAIN}/{detail_file}")]), encoding="utf-8")
        generated_pages.append(detail_file)

    # sitemap: add hierarchy pages
    sitemap_path = ROOT / "sitemap.xml"
    sm = sitemap_path.read_text()
    start = "  <!-- GENERATED PRODUCT URLS END -->"
    new_block = []
    for name in generated_pages:
        new_block.extend(["  <url>", f"    <loc>{DOMAIN}/{name}</loc>",
                          f"    <lastmod>{TODAY}</lastmod>", "    <changefreq>monthly</changefreq>",
                          "    <priority>0.7</priority>", "  </url>"])
    if start in sm:
        before, rest = sm.split(start, 1)
        sm = before + start + "\n" + "\n".join(new_block) + rest
    sitemap_path.write_text(sm)

    # persist v2 data
    catalog["schemaVersion"] = 2
    catalog["generatedAt"] = TODAY
    (DATA / "catalog-products.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=1))
    print(f"wrote {len(generated_pages)} hierarchy pages; products without group: {sorted(unlinked_products)}")


if __name__ == "__main__":
    main()
