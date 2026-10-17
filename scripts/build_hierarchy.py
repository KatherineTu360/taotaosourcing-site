#!/usr/bin/env python3
"""Build the representative hierarchical catalog and navigation pages.

Levels: products.html -> detail-{category}.html (group cards)
        -> category-{cat}--{group}.html (sub-group cards OR model list)
        -> category-{cat}--{group}--{sub}.html (2-3 representative products)

Model entries come from data/intel/*.json (supplier catalog extractions).
Existing detail products (data/catalog-products.json "products") are preferred
when they represent a leaf group. Full source data is retained internally, while
only a small buyer-facing shortlist is linked and indexable.
"""
from __future__ import annotations

import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from image_privacy import is_blocked_image, placeholder, public_image, public_images

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hierarchy_config import GROUPS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
INTEL = DATA / "intel"
ASSETS = ROOT / "assets" / "products"
DOMAIN = "https://taotaosourcing.com"
WHATSAPP = "8616626662274"
TODAY = date.today().isoformat()
REPRESENTATIVE_MAX = 3
REPRESENTATIVE_PATH = DATA / "representative-products.json"

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
HQ_RUN = Path("/Users/katherinetu/CODEX/独立站/website-optimization/run/taotaosourcing-hierarchy-2026-09-18")
GALLERY_MANIFEST = HQ_RUN / "gallery_manifest.json"
GALLERY_INDEX = json.loads(GALLERY_MANIFEST.read_text()) if GALLERY_MANIFEST.exists() else {}

# Exact-model images reviewed locally and confirmed free of supplier names,
# logos and contact details. Keep this list deliberately small: a generic or
# similar-looking product photo must never be presented as an exact model.
PHOTO_OVERRIDES = {
    "CJ5011-R": "assets/products/door-closers/cj5011-r-no-logo.jpeg",
    # Source: 睫毛/国内款(3)(2).xlsx. The image anchors match the adjacent
    # 6P/10P cell descriptions; the 6P derivative removes only the source
    # supplier branding while the original workbook remains unchanged.
    "CN-CL6P": "assets/products/eyelashes/cn-cl6p-excel-brand-removed.png",
    "CN-CL10P": "assets/products/eyelashes/cn-cl10p-excel-label-removed.png",
    # Source: LED电子屏幕（领英找我）/260305-Led poster display summary.xlsx.
    # The drawing anchor is on row 15, whose model cell identifies HB-D2.5.
    "HB-D2.5": "assets/products/led/hb-d2-5-excel.png",
}

# Category-card covers reviewed for relevance and supplier privacy. These are
# category-level visuals, not claims that the pictured item is a specific
# model. A value of None deliberately uses the compact verification state.
GROUP_COVER_OVERRIDES = {
    ("heatpump", "residential-hot-water"): None,
    ("heatpump", "residential-heating"): None,
    ("heatpump", "evi-cold-climate"): None,
    ("heatpump", "commercial-hot-water"): None,
    ("heatpump", "high-temp"): None,
    ("heatpump", "pool-spa"): "assets/products/heatpump/pool-heat-pump.jpg",
    ("heatpump", "commercial-heating"): "assets/products/industrial-detail/heatpump-r290-ultraheat.jpg",
    ("heatpump", "tanks"): None,
    ("sanitary", "smart-toilets"): None,
    ("sanitary", "toilets"): None,
    ("sanitary", "basins"): None,
    ("sanitary", "squat-urinal"): None,
    ("sanitary", "cisterns"): None,
    ("sanitary", "showers"): None,
    ("sanitary", "faucets"): None,
    ("sanitary", "hanging-pans"): None,
    ("sanitary", "bathroom-accessories"): None,
    ("sanitary", "smart-toilet"): None,
    ("sanitary", "bidet-seats"): None,
    ("sanitary", "one-piece"): None,
    ("sanitary", "two-piece"): None,
    ("sanitary", "wall-hung"): None,
    ("sanitary", "pedestal"): None,
    ("sanitary", "wall-counter"): None,
    ("sanitary", "art-undermount"): None,
    ("sanitary", "squat-pans"): None,
    ("sanitary", "urinals"): None,
    ("sanitary", "mop-tubs"): None,
    ("sanitary", "shower-columns"): None,
    ("sanitary", "concealed-showers"): None,
    ("sanitary", "basin-faucets"): None,
    ("sanitary", "kitchen-faucets"): None,
    ("sanitary", "taps-valves"): None,
    ("eyelashes", "cluster-trays"): "assets/products/eyelashes/cn-cl10p-excel-label-removed.png",
}

# The sanitary catalogue was extracted from composite PDF spreads. Several
# automatic crops contain adjacent products or specification text, so they are
# not safe to present as exact-model photos until manually matched.
UNVERIFIED_MODEL_IMAGE_CATEGORIES = {"sanitary"}

# Keep this supplier catalogue as an internal source record only. Its models,
# images and generated pages must not be included in the public site.
PUBLICLY_EXCLUDED_SOURCES = {"meicheng", "yongbao"}
# Source-specific group pages generated before a supplier was excluded must not
# remain in the public sitemap.
PUBLICLY_EXCLUDED_PAGE_PATHS = {
    "category-helmets--motorcycle--meicheng-city.html",
    "product-eraergy-go.html",
}
PUBLIC_MODEL_ALIASES = {
    "ERAERGY-GO": "MOBILE-POWER-GO",
}


def esc(v):
    return html.escape(str(v), quote=True)


def usable_public_image(value):
    """Return a publishable image, excluding the generic missing-photo asset."""
    if not value:
        return None
    image = public_image(value)
    return None if image == placeholder() else image


def group_cover(cat_slug, group):
    """Resolve a reviewed category cover or deliberately return no image."""
    key = (cat_slug, group.get("slug"))
    if key in GROUP_COVER_OVERRIDES:
        return usable_public_image(GROUP_COVER_OVERRIDES[key])
    return usable_public_image(group.get("cover"))


def slugify(s):
    s = re.sub(r"[^A-Za-z0-9]+", "-", str(s)).strip("-").lower()
    return s[:60] or "model"


def load_intel():
    data = {}
    for f in INTEL.glob("*.json"):
        if f.stem in PUBLICLY_EXCLUDED_SOURCES:
            continue
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


def excluded_product_slugs():
    """Product-page slugs that must also be removed from the public sitemap."""
    slugs = set()
    for source in PUBLICLY_EXCLUDED_SOURCES:
        path = INTEL / f"{source}.json"
        if not path.exists():
            continue
        for entry in json.loads(path.read_text()).get("models", []):
            slugs.add(slugify(entry.get("id") or entry.get("model")))
    return slugs


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
            public_mid = PUBLIC_MODEL_ALIASES.get(mid, mid)
            public_entry = dict(e)
            if public_mid != mid:
                public_entry["id"] = public_mid
                public_entry["model"] = public_mid
            entries.append({
                "id": public_mid,
                "slug": slugify(public_mid),
                "name": entry_title(src, public_entry),
                "model": str(public_entry.get("model") or public_mid),
                "spec": spec or ("Style reference from the supplier catalog; material, width and finish are confirmed per order." if src in ("belts","bags","slg") else ""),
                "source": src,
                "page": e.get("page"),
                "image": img,
                "_raw": e,
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


def representative_key(kind, item):
    """Return a stable leaf-level key so a curated page and raw model do not repeat."""
    value = str(item.get("model") or item.get("id") or item.get("slug") or item.get("name") or "")
    generic = ("to be confirmed", "no model code", "project-specific", "supplier catalog")
    if not value or any(token in value.lower() for token in generic) or len(value) > 80:
        value = str(item.get("slug") or item.get("name") or item.get("id") or value)
    return re.sub(r"[^a-z0-9]+", "", value.lower()) or f"{kind}-{id(item)}"


def product_has_public_photo(item):
    for value in list(item.get("images") or []) + [item.get("image")]:
        if not value or is_blocked_image(value):
            continue
        path = ROOT / str(value)
        if path.exists() and image_ok(path):
            return True
    return False


def entry_photo_override(item):
    value = PHOTO_OVERRIDES.get(str(item.get("id") or item.get("model") or ""))
    if not value or is_blocked_image(value):
        return None
    path = ROOT / value
    return value if path.exists() and image_ok(path) else None


def entry_has_public_photo(item, cat_slug, asset_leaf_slug):
    if entry_photo_override(item):
        return True
    image = item.get("image")
    if image:
        source = Path(image)
        target = f"assets/products/hierarchy/{cat_slug}/{asset_leaf_slug}/{item['slug']}.jpg"
        if source.exists() and image_ok(source) and not is_blocked_image(target):
            return True
    rel_paths = GALLERY_INDEX.get(str(item["id"])) or []
    for i, rel in enumerate(rel_paths):
        source = HQ_RUN / rel
        suffix = f"-{i}" if i else ""
        target = f"assets/products/gallery/{item['slug']}{suffix}.jpg"
        if source.exists() and image_ok(source) and not is_blocked_image(target):
            return True
    return False


def choose_representatives(entries, products, cat_slug, asset_leaf_slug):
    """Choose two or three representatives, prioritising clean product imagery."""
    chosen_entries = []
    chosen_products = []
    seen = set()
    candidates = []
    for kind, items in (("product", products), ("entry", entries)):
        for item in items:
            key = representative_key(kind, item)
            if key in seen:
                continue
            seen.add(key)
            has_photo = (product_has_public_photo(item) if kind == "product" else
                         entry_has_public_photo(item, cat_slug, asset_leaf_slug))
            candidates.append((kind, item, has_photo))

    clean = [candidate for candidate in candidates if candidate[2]]
    fallback = [candidate for candidate in candidates if not candidate[2]]
    selected = clean[:REPRESENTATIVE_MAX]
    minimum = min(2, len(candidates))
    if len(selected) < minimum:
        selected.extend(fallback[:minimum - len(selected)])
    for kind, item, _ in selected:
        if kind == "product":
            chosen_products.append(item)
        else:
            chosen_entries.append(item)
    return chosen_entries, chosen_products


def copy_image(src: Path, cat_slug: str, leaf_slug: str, slug: str) -> str | None:
    dest_dir = ASSETS / "hierarchy" / cat_slug / leaf_slug
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{slug}.jpg"
    public_path = f"assets/products/hierarchy/{cat_slug}/{leaf_slug}/{slug}.jpg"
    if is_blocked_image(public_path):
        return placeholder()
    if not dest.exists():
        shutil.copy2(src, dest)
    return public_path


# ---------------------------------------------------------------------------
# page rendering
# ---------------------------------------------------------------------------

def page_head(title, description, canonical, image):
    image = public_image(image)
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
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta property="og:site_name" content="Taotao Sourcing">
  <meta property="og:locale" content="en_US">
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
    candidates = list(entry.get("gallery") or [])
    if entry.get("image"):
        candidates.append(entry["image"])
    image = public_images(candidates)[0] if candidates else None
    image = usable_public_image(image)
    if cat_slug in UNVERIFIED_MODEL_IMAGE_CATEGORIES:
        image = None
    detail_href = entry.get("detail") or (product_ref and f"product-{product_ref['slug']}.html") or (group_path or "#")
    if product_ref:
        detail_link = f'<a class="more" href="product-{esc(product_ref["slug"])}.html">Full product details →</a>'
    elif entry.get("detail"):
        detail_link = f'<a class="more" href="{esc(entry["detail"])}">View details →</a>'
    else:
        detail_link = ""
    if image:
        media = f"""          <a class="catalog-product-media" href="{esc(detail_href)}">
            <img src="{esc(image)}" alt="{esc(entry['name'])} catalog reference" loading="lazy">
          </a>"""
        card_class = "catalog-product-card model-card"
    else:
        media = f"""          <a class="catalog-product-media catalog-product-media--pending" href="{esc(detail_href)}" aria-label="View {esc(entry['name'])} details">
            <span class="catalog-media-kicker">Image verification</span>
            <strong>Exact model photo on request</strong>
            <small>We verify the model and remove supplier-identifying marks before publication.</small>
          </a>"""
        card_class = "catalog-product-card model-card has-no-product-photo"
    page_ref = f'<span class="model-source">Catalog p.{entry["page"]}</span>' if entry.get("page") else ""
    wa = f"https://wa.me/{WHATSAPP}?text=" + __import__("urllib.parse", fromlist=["quote"]).quote(
        f"Hello Katherine, I'm interested in {entry['model']}. Target market and quantity: ")
    return f"""        <article class="{card_class}">
{media}
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
        img = group_cover(cat["slug"], grp)
        href = grp["_url_file"]
        sub_note = (f'{len(grp["subs"])} product types' if grp["subs"] else
                    f'{count} representative product' + ('' if count == 1 else 's'))
        if img:
            media = f"""          <a class="catalog-product-media catalog-product-media--cover" href="{href}">
            <img src="{esc(img)}" alt="{esc(grp['title'])} category photo" loading="lazy">
          </a>"""
            card_class = "catalog-product-card"
        else:
            media = f"""          <a class="catalog-product-media catalog-product-media--category" href="{href}" aria-label="Browse {esc(grp['title'])}">
            <span class="catalog-media-kicker">Sourcing category</span>
            <strong>{esc(grp['title'])}</strong>
            <small>Compare representative models and buyer checkpoints</small>
          </a>"""
            card_class = "catalog-product-card has-no-category-photo"
        cards.append(f"""        <article class="{card_class}">
{media}
          <div class="catalog-product-body">
            <span class="catalog-badge">{esc(sub_note)}</span>
            <h3><a href="{href}">{esc(grp['title'])}</a></h3>
            <p>{esc(grp.get('intro') or '')}</p>
            <a class="more" href="{href}">Browse models →</a>
          </div>
        </article>""")
    cards_html = "\n".join(cards)
    schema = breadcrumb_json(breadcrumbs)
    itemlist = json.dumps({
        "@context": "https://schema.org", "@type": "ItemList",
        "name": parent_title,
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1,
             "name": g.get("title", ""), "url": f"{DOMAIN}/{g.get('_url_file', '')}"}
            for i, g in enumerate(groups)
        ],
    }, ensure_ascii=False, separators=(",", ":"))
    schema = schema + f'</script><script type="application/ld+json">{itemlist}'

    head_image = next((group_cover(cat["slug"], group) for group in groups
                       if group_cover(cat["slug"], group)), "assets/logo.png")
    return f"""{page_head(f"{parent_title} | Taotao Sourcing", f"Browse {parent_title} product types and a focused shortlist of representative products for buyer review.", parent_url, head_image)}
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
    """Render the final-level page: a focused representative shortlist."""
    title = sub["title"]
    canonical = f"{DOMAIN}/{sub['_url_file']}"
    entries = sub["_public_entries"]
    products = sub["_public_products"]
    cards = [model_card(e, cat_slug=cat["slug"]) for e in entries]
    cards += [model_card(
        {"id": p["slug"], "slug": p["slug"], "name": p["name"], "model": p.get("model") or p["name"],
         "spec": p.get("summary", ""), "image": p.get("image"), "page": None},
        product_ref=p, cat_slug=cat["slug"])
        for p in products]
    count = len(entries) + len(products)
    trail = " / ".join(f'<a href="{u}">{esc(t)}</a>' for t, u in parent_chain) + f" / {esc(title)}"
    schema = breadcrumb_json(breadcrumbs)
    list_items = [{"@type": "ListItem", "position": i + 1, "name": e["name"],
                   "url": f"{DOMAIN}/{e.get('detail') or sub['_url_file']}"}
                  for i, e in enumerate(entries)]
    list_items += [{"@type": "ListItem", "position": len(list_items) + i + 1, "name": p["name"],
                    "url": f"{DOMAIN}/product-{p['slug']}.html"}
                   for i, p in enumerate(products)]
    itemlist = json.dumps({"@context": "https://schema.org", "@type": "ItemList",
                           "name": title, "numberOfItems": len(list_items),
                           "itemListElement": list_items},
                          ensure_ascii=False, separators=(",", ":"))
    schema = schema + f'</script><script type="application/ld+json">{itemlist}' + "\n"
    note = '<p class="source-note">This page shows a focused buyer-facing shortlist rather than every available model. Specifications, certification scope, MOQ and lead time are re-confirmed for the selected model and target market before quotation.</p>'
    # The categories reviewed in this pass use a category-level cover rather
    # than an arbitrary first model crop. Other categories retain their current
    # social image until their media has been reviewed separately.
    if cat["slug"] in {"heatpump", "sanitary", "eyelashes"}:
        head_image = group_cover(cat["slug"], group) or "assets/logo.png"
    else:
        head_image = (entries[0]["image"] if entries and entries[0].get("image")
                      else (products[0]["image"] if products else "assets/logo.png"))
    return f"""{page_head(f"{title} — Representative Products | Taotao Sourcing", f"Compare {count} representative {title} products and request a model-specific quotation, document check or broader shortlist.", canonical, head_image)}
{header()}
  <main>
    <section class="page-hero">
      <div class="container">
        <div class="breadcrumb"><a href="index.html">Home</a> / <a href="products.html">Products</a> / {trail}</div>
        <span class="catalog-eyebrow">{count} representative product{'' if count == 1 else 's'}</span>
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
            <h2>Need this model or a broader shortlist?</h2>
            <p>Send your target market, quantity and required documents. We can quote a representative model or prepare more suitable options from the retained internal catalogue.</p>
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


def set_indexability(path: Path, indexable: bool) -> None:
    """Keep legacy URLs available, but index only the representative catalogue."""
    text = path.read_text(encoding="utf-8")
    robots = re.compile(r'\s*<meta\s+name="robots"\s+content="noindex,follow"\s*/?>', re.I)
    updated = robots.sub("", text)
    if not indexable:
        marker = '  <meta name="viewport" content="width=device-width, initial-scale=1.0">'
        updated = updated.replace(marker, marker + '\n  <meta name="robots" content="noindex,follow">', 1)
    if updated != text:
        path.write_text(updated, encoding="utf-8")


def sync_sitemap(indexable_pages):
    """Keep core/article URLs and replace generated catalogue URLs without duplicates."""
    sitemap_path = ROOT / "sitemap.xml"
    existing = sitemap_path.read_text(encoding="utf-8")
    records = []
    seen = set()
    for block in re.findall(r"<url>.*?</url>", existing, flags=re.S):
        match = re.search(r"<loc>([^<]+)</loc>", block)
        if not match:
            continue
        loc = match.group(1)
        name = Path(urlparse(loc).path).name
        if name.startswith(("product-", "category-", "detail-")):
            continue
        if loc not in seen:
            lines = [line.strip() for line in block.strip().splitlines()]
            records.append("\n".join(
                line if index in (0, len(lines) - 1) else "  " + line
                for index, line in enumerate(lines)
            ))
            seen.add(loc)
    for name in indexable_pages:
        loc = f"{DOMAIN}/{name}"
        if loc in seen:
            continue
        records.append(
            "<url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{TODAY}</lastmod>\n"
            "    <changefreq>monthly</changefreq>\n"
            "    <priority>0.7</priority>\n"
            "  </url>"
        )
        seen.add(loc)
    body = "\n".join("  " + block.replace("\n", "\n  ") for block in records)
    sitemap_path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'{body}\n</urlset>\n',
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------

def main():
    catalog = json.loads((DATA / "catalog-products.json").read_text())
    intel = load_intel()
    products = catalog["products"]
    products_by_slug = {p["slug"]: p for p in products}
    used = set()
    unlinked_products = {p["slug"] for p in products}
    generated_model_pages = []
    generated_hierarchy_pages = []

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
                    asset_leaf_slug = f"{cat_slug}-{grp['slug']}-{sub['slug']}"
                    sub["_public_entries"], sub["_public_products"] = choose_representatives(
                        sub["_entries"], sub["_products"], cat_slug, asset_leaf_slug)
                    grp["_sub_entries"][sub["slug"]] = sub
                grp["_public_subs"] = [
                    sub for sub in grp["subs"]
                    if sub["_public_entries"] or sub["_public_products"]
                ]
            else:
                grp["_entries"] = resolve_group_models(grp["models"], intel, used, None)
                grp["_products"] = link_catalog_products(grp["models"], products_by_slug)
                asset_leaf_slug = f"{cat_slug}-{grp['slug']}"
                grp["_public_entries"], grp["_public_products"] = choose_representatives(
                    grp["_entries"], grp["_products"], cat_slug, asset_leaf_slug)
                grp["_public_subs"] = []

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

    # Phase A: URL assignment + gallery copy + detail slug allocation
    from build_model_pages import allocate_slug, copy_gallery, render_model_detail
    taken_slugs = set(products_by_slug) | {"index", "products", "contact", "about", "privacy"}
    detail_tasks = []
    render_tasks = []
    for cat in catalog["categories"]:
        cslug = cat["slug"]
        groups = GROUPS.get(cslug)
        if not groups:
            continue
        cat["groups"] = []
        for grp in groups:
            leaves = grp["subs"] or [grp]
            public_leaves = (
                grp["_public_subs"]
                if grp["subs"]
                else ([grp] if grp["_public_entries"] or grp["_public_products"] else [])
            )
            if not public_leaves:
                continue
            grp_url = f"category-{cslug}--{grp['slug']}.html"
            grp["_url_file"] = grp_url

            total_models = 0
            for sub in leaves:
                slug_parts = f"{cslug}--{grp['slug']}" + (f"--{sub['slug']}" if grp["subs"] else "")
                sub["_url_file"] = f"category-{slug_parts}.html"
                for e in sub["_entries"]:
                    is_public = e in sub["_public_entries"]
                    override = entry_photo_override(e) if is_public else None
                    if override:
                        e["image"] = override
                    elif is_public and e.get("image"):
                        e["image"] = copy_image(Path(e["image"]), cslug, slug_parts.replace("--", "-"), e["slug"])
                    if "detail" not in e:
                        page_slug = allocate_slug(e["slug"], taken_slugs)
                        e["detail"] = f"product-{page_slug}.html"
                    if is_public:
                        e["gallery"] = copy_gallery(str(e["id"]), e["detail"][len("product-"):-len(".html")])
                        detail_tasks.append((e, cat, grp, sub, sub["_public_entries"]))
                total_models += len(sub["_public_entries"]) + len(sub["_public_products"])
                for p in sub["_products"]:
                    unlinked_products.discard(p["slug"])

            # Group cover: first model image found in any leaf. Rendering later
            # decides whether that source is suitable for a public card.
            cover = None
            for sub in public_leaves:
                for e in sub["_public_entries"]:
                    reviewed_image = usable_public_image(e.get("image"))
                    if reviewed_image:
                        cover = reviewed_image
                        break
                if cover:
                    break
                for e in sub["_public_entries"]:
                    reviewed_gallery = [usable_public_image(value) for value in e.get("gallery") or []]
                    reviewed_gallery = [value for value in reviewed_gallery if value]
                    if reviewed_gallery:
                        cover = reviewed_gallery[0]
                        break
                if cover:
                    break
                for p in sub["_public_products"]:
                    cover = p.get("image")
                    break
                if cover:
                    break
            grp["cover"] = cover
            grp["total_models"] = total_models
            cat["groups"].append({
                "slug": grp["slug"], "title": grp["title"], "intro": grp.get("intro", ""),
                "subs": [{"slug": s["slug"], "title": s["title"], "intro": s.get("intro", ""),
                          "url": s["_url_file"], "modelCount": len(s["_public_entries"]) + len(s["_public_products"])}
                         for s in public_leaves if grp["subs"]],
                "url": grp_url, "cover": cover, "totalModels": total_models,
            })

            # collect hierarchy render tasks
            if grp["subs"]:
                for sub in public_leaves:
                    render_tasks.append(("leaf", cat, grp, sub, grp_url))
                render_tasks.append(("group", cat, grp, None, grp_url))
            else:
                render_tasks.append(("leaf", cat, grp, grp, grp_url))

    # Phase B: render model detail pages (siblings need slugs first)
    for e, cat, grp, sub, siblings in detail_tasks:
        page_slug = e["detail"][len("product-"):-len(".html")]
        (ROOT / e["detail"]).write_text(
            render_model_detail(e, cat, grp, sub, siblings, page_slug,
                                page_head, header, footer, breadcrumb_json, esc, WHATSAPP, DOMAIN),
            encoding="utf-8")
        generated_model_pages.append(e["detail"])

    # Phase C: render hierarchy pages
    for cat in catalog["categories"]:
        cslug = cat["slug"]
        if not GROUPS.get(cslug):
            continue
        for kind, cat, grp, sub, grp_url in [t for t in render_tasks if t[1]["slug"] == cslug]:
            if kind == "leaf":
                chain = ([(cat["title"], f"detail-{cslug}.html"), (grp["title"], grp_url)]
                         if grp["subs"] else [(cat["title"], f"detail-{cslug}.html")])
                crumbs = [("Home", DOMAIN + "/"), ("Products", DOMAIN + "/products.html"),
                          (cat["title"], f"{DOMAIN}/detail-{cslug}.html")]
                if grp["subs"]:
                    crumbs.append((grp["title"], f"{DOMAIN}/{grp_url}"))
                crumbs.append((sub["title"], f"{DOMAIN}/{sub['_url_file']}"))
                (ROOT / sub["_url_file"]).write_text(
                    render_model_list(cat, grp, sub, chain, crumbs), encoding="utf-8")
                generated_hierarchy_pages.append(sub["_url_file"])
            elif kind == "group":
                sub_cards = []
                for sub in grp["_public_subs"]:
                    cover = next((e["image"] for e in sub["_public_entries"] if e.get("image")),
                                 sub["_public_products"][0]["image"] if sub["_public_products"] else None)
                    sub_cards.append({"title": sub["title"], "intro": sub.get("intro", ""),
                                      "cover": cover, "_url_file": sub["_url_file"],
                                      "total_models": len(sub["_public_entries"]) + len(sub["_public_products"]),
                                      "subs": [], "slug": sub["slug"]})
                (ROOT / grp_url).write_text(
                    render_group_cards(cat, sub_cards, f"{cat['title']} — {grp['title']}",
                                       f"{DOMAIN}/{grp_url}",
                                       [("Home", DOMAIN + "/"), ("Products", DOMAIN + "/products.html"),
                                        (cat["title"], f"{DOMAIN}/detail-{cslug}.html"),
                                        (grp["title"], f"{DOMAIN}/{grp_url}")],
                                       back_link=f"detail-{cslug}.html", back_label=cat["title"]), encoding="utf-8")
                generated_hierarchy_pages.append(grp_url)
        # rewrite detail-{category}.html as group-card page
        detail_file = f"detail-{cslug}.html"
        gcards = []
        for grp in cat["groups"]:
            gcards.append({
                "title": grp["title"], "intro": grp["intro"], "cover": grp["cover"],
                "_url_file": grp["url"], "total_models": grp["totalModels"], "subs": grp["subs"],
                "slug": grp["slug"],
            })
        (ROOT / detail_file).write_text(
            render_group_cards(cat, gcards, cat["title"], f"{DOMAIN}/{detail_file}",
                               [("Home", DOMAIN + "/"), ("Products", DOMAIN + "/products.html"),
                                (cat["title"], f"{DOMAIN}/{detail_file}")]), encoding="utf-8")
        generated_hierarchy_pages.append(detail_file)

    representative_manual_pages = sorted({
        f"product-{p['slug']}.html"
        for groups in GROUPS.values()
        for grp in groups
        for sub in (grp["subs"] or [grp])
        for p in sub.get("_public_products", [])
    })
    representative_pages = sorted(set(generated_model_pages + representative_manual_pages))
    indexable_hierarchy_pages = sorted(set(generated_hierarchy_pages))

    removed_product_pages = 0
    representative_set = set(representative_pages)
    for path in ROOT.glob("product-*.html"):
        if path.name not in representative_set:
            path.unlink()
            removed_product_pages += 1
    for path in ROOT.glob("category-*.html"):
        set_indexability(path, path.name in indexable_hierarchy_pages)

    sync_sitemap(indexable_hierarchy_pages + representative_pages)

    leaf_groups = []
    for cat_slug, groups in GROUPS.items():
        for grp in groups:
            public_leaves = (
                grp["_public_subs"]
                if grp["subs"]
                else ([grp] if grp["_public_entries"] or grp["_public_products"] else [])
            )
            for sub in public_leaves:
                selected = [
                    {"kind": "catalog", "model": p.get("model") or p["name"],
                     "name": p["name"], "page": f"product-{p['slug']}.html"}
                    for p in sub["_public_products"]
                ] + [
                    {"kind": "model", "model": e["model"], "name": e["name"],
                     "page": e["detail"]}
                    for e in sub["_public_entries"]
                ]
                leaf_groups.append({
                    "category": cat_slug,
                    "group": grp["slug"],
                    "leaf": sub["slug"],
                    "title": sub["title"],
                    "page": sub["_url_file"],
                    "availableCandidates": len(sub["_entries"]) + len(sub["_products"]),
                    "representatives": selected,
                })
    REPRESENTATIVE_PATH.write_text(json.dumps({
        "schemaVersion": 1,
        "generatedAt": TODAY,
        "maxPerLeaf": REPRESENTATIVE_MAX,
        "leafGroups": leaf_groups,
        "indexableHierarchyPages": indexable_hierarchy_pages,
        "indexableProductPages": representative_pages,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # persist v2 data
    catalog["schemaVersion"] = 2
    catalog["generatedAt"] = TODAY
    catalog["representativeMode"] = {
        "maxPerLeaf": REPRESENTATIVE_MAX,
        "leafGroups": len(leaf_groups),
        "indexableProducts": len(representative_pages),
    }
    (DATA / "catalog-products.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=1))
    print(
        f"wrote {len(indexable_hierarchy_pages)} hierarchy pages and "
        f"selected {len(representative_pages)} representative product pages; "
        f"removed {removed_product_pages} stale generated product pages; "
        f"products without group: {sorted(unlinked_products)}"
    )


if __name__ == "__main__":
    main()
