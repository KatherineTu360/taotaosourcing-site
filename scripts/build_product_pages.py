#!/usr/bin/env python3
"""Build Taotao Sourcing category and product pages from reviewed catalog data."""

from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import quote, urlparse

from image_privacy import placeholder, public_image, public_images


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "catalog-products.json"
REPRESENTATIVE_PATH = ROOT / "data" / "representative-products.json"
DOMAIN = "https://taotaosourcing.com"
WHATSAPP = "8616626662274"
TODAY = date.today().isoformat()
UNVERIFIED_PRODUCT_IMAGE_CATEGORIES = {"sanitary"}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def page_head(title: str, description: str, canonical: str, image: str, *, indexable: bool = True) -> str:
    image = public_image(image)
    image_url = image if image.startswith("http") else f"{DOMAIN}/{image}"
    robots = "" if indexable else '  <meta name="robots" content="noindex,follow">\n'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
{robots}  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{esc(image_url)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta property="og:site_name" content="Taotao Sourcing">
  <meta property="og:locale" content="en_US">
  <link rel="icon" type="image/png" href="assets/logo.png">
  <link rel="stylesheet" href="css/style.css">
</head>"""


def header(active: str = "products") -> str:
    def cls(name: str) -> str:
        return ' class="active"' if name == active else ""

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


def footer() -> str:
    return """  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div>
          <div class="footer-brand">
            <img src="assets/logo.png" alt="Taotao Sourcing logo">
            <div><strong>Taotao Sourcing</strong><small>Zhaoqing Taotao Import and Export Trading Co., Ltd.</small></div>
          </div>
          <p class="footer-summary">A South China sourcing partner combining supplier document checks, factory visits and a bank-informed approach to observable business risks.</p>
          <div class="footer-social">
            <a href="https://www.linkedin.com/in/katherine-tu-1b2574286/" target="_blank" rel="noreferrer" aria-label="LinkedIn" title="LinkedIn">in</a>
            <a href="https://www.youtube.com/@TuKatherine" target="_blank" rel="noreferrer" aria-label="YouTube" title="YouTube">▶</a>
            <a href="https://www.instagram.com/katherinetu360/" target="_blank" rel="noreferrer" aria-label="Instagram" title="Instagram">ig</a>
            <a href="https://www.facebook.com/profile.php?id=61583761061206" target="_blank" rel="noreferrer" aria-label="Facebook" title="Facebook">f</a>
          </div>
        </div>
        <div>
          <h4>Catalog</h4>
          <ul>
            <li><a href="products.html">All categories</a></li>
            <li><a href="detail-helmets.html">Helmets &amp; visors</a></li>
            <li><a href="detail-doors-windows.html">Doors &amp; windows</a></li>
            <li><a href="detail-storage.html">Energy equipment</a></li>
          </ul>
        </div>
        <div>
          <h4>Services</h4>
          <ul>
            <li><a href="services.html#verification">Supplier Verification</a></li>
            <li><a href="services.html#audit">Factory Visits &amp; Reviews</a></li>
            <li><a href="services.html#qc">Inspection &amp; QC</a></li>
            <li><a href="services.html#full-service">Full Sourcing Service</a></li>
          </ul>
        </div>
        <div>
          <h4>Contact</h4>
          <ul>
            <li>Zhaoqing, Guangdong, China</li>
            <li><a class="nowrap" href="https://wa.me/8616626662274" target="_blank" rel="noreferrer">WhatsApp: +86 166 2666 2274</a></li>
            <li><a href="mailto:rabieternity@gmail.com">rabieternity@gmail.com</a></li>
            <li><a href="contact.html">Inquiry form →</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© 2026 Zhaoqing Taotao Import and Export Trading Co., Ltd. All rights reserved.</span>
        <span><a href="privacy.html">Privacy</a></span>
      </div>
    </div>
  </footer>

    <script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","name":"Zhaoqing Taotao Import and Export Trading Co., Ltd.","alternateName":"Taotao Sourcing","url":"https://taotaosourcing.com/","logo":"https://taotaosourcing.com/assets/logo.png","email":"rabieternity@gmail.com","telephone":"+8616626662274","address":{"@type":"PostalAddress","addressLocality":"Zhaoqing","addressRegion":"Guangdong","addressCountry":"CN"},"sameAs":["https://www.linkedin.com/in/katherine-tu-1b2574286/","https://www.youtube.com/@TuKatherine","https://www.instagram.com/katherinetu360/","https://www.facebook.com/profile.php?id=61583761061206"]}</script>
  <script type="application/ld+json">{"@context":"https://schema.org","@type":"WebSite","name":"Taotao Sourcing","url":"https://taotaosourcing.com/","publisher":{"@type":"Organization","name":"Zhaoqing Taotao Import and Export Trading Co., Ltd."}}</script>
  <a class="wa-float" href="https://wa.me/8616626662274" target="_blank" rel="noreferrer" aria-label="Chat on WhatsApp">
    <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M16 3C9.4 3 4 8.3 4 14.9c0 2.6.8 5 2.3 7L4 29l7.3-2.2c1.9 1 4 1.6 6.2 1.6h.5c6.6 0 12-5.3 12-11.9C30 8.3 22.6 3 16 3zm5.9 16.9c-.3.8-1.7 1.6-2.4 1.7-.6.1-1.4.1-2.2-.1-.5-.2-1.2-.4-2-.8-3.5-1.5-5.8-5-6-5.3-.2-.2-1.4-1.9-1.4-3.6 0-1.7.9-2.6 1.2-2.9.3-.3.7-.4 1-.4h.7c.2 0 .5-.1.8.6.3.8 1.1 2.6 1.2 2.8.1.2.1.4 0 .7-.1.2-.2.4-.4.6l-.6.7c-.2.2-.4.4-.2.8.2.4 1 1.7 2.2 2.7 1.5 1.4 2.8 1.8 3.2 2 .4.2.6.2.9-.1.2-.3 1-1.2 1.3-1.6.3-.4.5-.3.9-.2.4.1 2.2 1 2.6 1.2.4.2.6.3.7.5.1.2.1 1-.2 1.7z"/></svg>
  </a>
  <script src="js/main.js"></script>
</body>
</html>
"""


def breadcrumb_json(items: list[tuple[str, str]]) -> str:
    parts = []
    for position, (name, url) in enumerate(items, 1):
        parts.append({"@type": "ListItem", "position": position, "name": name, "item": url})
    value = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": parts}
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def product_card(product: dict) -> str:
    badge = f'<span class="catalog-badge">{esc(product["model"])}</span>' if product.get("model") else ""
    image = public_images(list(product.get("images") or []) + [product.get("image")])[0]
    if product.get("category") in UNVERIFIED_PRODUCT_IMAGE_CATEGORIES:
        image = placeholder()
    if image == placeholder():
        media = f"""          <a class="catalog-product-media catalog-product-media--pending" href="product-{esc(product['slug'])}.html">
            <span class="catalog-media-kicker">Image verification</span>
            <strong>Exact model photo on request</strong>
            <small>Model-specific image is checked before publication.</small>
          </a>"""
        card_class = "catalog-product-card has-no-product-photo"
    else:
        media = f"""          <a class="catalog-product-media" href="product-{esc(product['slug'])}.html">
            <img src="{esc(image)}" alt="{esc(product['imageAlt'])}" loading="lazy">
          </a>"""
        card_class = "catalog-product-card"
    return f"""        <article class="{card_class}">
{media}
          <div class="catalog-product-body">
            {badge}
            <h3><a href="product-{esc(product['slug'])}.html">{esc(product['name'])}</a></h3>
            <p>{esc(product['summary'])}</p>
            <a class="more" href="product-{esc(product['slug'])}.html">View product details →</a>
          </div>
        </article>"""


def render_category(category: dict, products: list[dict]) -> str:
    canonical = f"{DOMAIN}/detail-{category['slug']}.html"
    cards = "\n".join(product_card(item) for item in products)
    product_area = (
        f'<div class="catalog-product-grid">\n{cards}\n        </div>'
        if products
        else (
            '<div class="catalog-hold-panel">'
            '<h2>Current publication status</h2>'
            f'<p>{esc(category.get("holdMessage", "Current product records are awaiting source verification."))}</p>'
            '</div>'
        )
    )
    inquiry = quote(f"Hello Katherine, I'm sourcing {category['title']}. My target market and estimated quantity are: ")
    hero_image = public_image(category.get("heroImage"))
    schema = breadcrumb_json([
        ("Home", DOMAIN + "/"),
        ("Products", DOMAIN + "/products.html"),
        (category["title"], canonical),
    ])
    return f"""{page_head(category['seoTitle'], category['metaDescription'], canonical, hero_image)}
{header()}
  <main>
    <section class="page-hero">
      <div class="container">
        <div class="breadcrumb"><a href="index.html">Home</a> / <a href="products.html">Products</a> / {esc(category['title'])}</div>
        <h1>{esc(category['title'])}</h1>
        <p>{esc(category['intro'])}</p>
      </div>
    </section>
    <section class="section">
      <div class="container">
        <p class="backlink"><a href="products.html">← Back to full catalog</a></p>
        <div class="catalog-intro-panel">
          <img src="{esc(hero_image)}" alt="{esc(category['heroAlt'])}">
          <div>
            <span class="catalog-eyebrow">Reviewed supplier material</span>
            <h2>{(str(len(products)) + ' reviewed product ' + ('page' if len(products) == 1 else 'pages')) if products else 'Source verification in progress'}</h2>
            <p>{esc(category['buyerNote'])}</p>
          </div>
        </div>
        {product_area}
        <div class="cta-band">
          <div>
            <h2>Need a shortlist, documents or a quotation?</h2>
            <p>Share your target market, quantity and required specifications. We will compare suitable suppliers and flag the items that still need confirmation.</p>
          </div>
          <div class="hero-actions">
            <a class="btn btn-red" href="contact.html">Start an Inquiry</a>
            <a class="btn btn-wa" href="https://wa.me/{WHATSAPP}?text={inquiry}" target="_blank" rel="noreferrer">WhatsApp Katherine</a>
          </div>
        </div>
      </div>
    </section>
  </main>
  <script type="application/ld+json">{schema}</script>
{footer()}"""


def spec_rows(product: dict) -> str:
    rows = []
    if product.get("model"):
        rows.append(("Model / series", product["model"]))
    for item in product.get("specifications", []):
        rows.append((item["label"], item["value"]))
    for label in ("MOQ", "Sample", "Lead time", "OEM / ODM"):
        key = label.lower().replace(" / ", "_").replace(" ", "_")
        if key in product:
            rows.append((label, product[key]))
    return "\n".join(f"            <tr><th>{esc(label)}</th><td>{esc(value)}</td></tr>" for label, value in rows)


def render_product(product: dict, category: dict, related: list[dict], *, indexable: bool = True) -> str:
    canonical = f"{DOMAIN}/product-{product['slug']}.html"
    inquiry_text = product.get("inquiryMessage") or (
        f"Hello Katherine, I'm interested in {product.get('model') or product['name']}. "
        "My target market and estimated quantity are: "
    )
    inquiry = quote(inquiry_text)
    features = "\n".join(f"              <li>{esc(item)}</li>" for item in product.get("features", []))
    checks = "\n".join(f"              <li>{esc(item)}</li>" for item in product.get("confirmBeforeOrder", []))
    gallery_parts = []
    gallery_paths = public_images(product.get("images") or [product.get("image")])
    if product.get("category") in UNVERIFIED_PRODUCT_IMAGE_CATEGORIES:
        gallery_paths = [placeholder()]
    if gallery_paths == [placeholder()]:
        gallery_paths = []
        gallery_parts.append(
            '          <div class="product-photo-pending">'
            '<span class="catalog-media-kicker">Image verification</span>'
            '<strong>Exact model photo available on request</strong>'
            '<small>We verify the model and remove supplier-identifying marks before publication.</small>'
            '</div>'
        )
    else:
        for i, path in enumerate(gallery_paths):
            loading = ' loading="lazy"' if i else ""
            gallery_parts.append(
                f'          <img src="{esc(path)}" alt="{esc(product["imageAlt"])}"{loading}>'
            )
    gallery = "\n".join(gallery_parts)
    related_cards = "\n".join(product_card(item) for item in related[:3])
    schema = breadcrumb_json([
        ("Home", DOMAIN + "/"),
        ("Products", DOMAIN + "/products.html"),
        (category["title"], f"{DOMAIN}/detail-{category['slug']}.html"),
        (product["name"], canonical),
    ])
    note = product.get("documentNote", "Specifications shown here come from the supplied catalog material. Confirm the final model, configuration and current documents before placing an order.")
    return f"""{page_head(product['seoTitle'], product['metaDescription'], canonical, gallery_paths[0] if gallery_paths else "assets/logo.png", indexable=indexable)}
{header()}
  <main>
    <section class="page-hero product-page-hero">
      <div class="container">
        <div class="breadcrumb"><a href="index.html">Home</a> / <a href="products.html">Products</a> / <a href="detail-{esc(category['slug'])}.html">{esc(category['title'])}</a> / {esc(product.get('model') or product['name'])}</div>
        <span class="catalog-eyebrow">{esc(product['productType'])}</span>
        <h1>{esc(product['name'])}</h1>
        <p>{esc(product['summary'])}</p>
      </div>
    </section>
    <section class="section product-detail-section">
      <div class="container">
        <div class="product-detail-grid">
          <div class="product-gallery">
{gallery}
          </div>
          <div class="product-facts">
            <span class="catalog-badge">{esc(product.get('model') or 'Supplier catalog series')}</span>
            <h2>Product overview</h2>
            <p>{esc(product['description'])}</p>
            <ul class="product-feature-list">
{features}
            </ul>
            <div class="hero-actions product-actions">
              <a class="btn btn-red" href="contact.html?product={quote(product.get('model') or product['name'])}">Request a Quotation</a>
              <a class="btn btn-wa" href="https://wa.me/{WHATSAPP}?text={inquiry}" target="_blank" rel="noreferrer">WhatsApp Katherine</a>
            </div>
          </div>
        </div>
        <div class="product-info-grid">
          <section class="product-info-card">
            <h2>Available information</h2>
            <div class="spec-table-wrap">
              <table class="spec-table"><tbody>
{spec_rows(product)}
              </tbody></table>
            </div>
          </section>
          <section class="product-info-card">
            <h2>Confirm before order</h2>
            <ul class="verification-list">
{checks}
            </ul>
            <p class="source-note"><strong>Document note:</strong> {esc(note)}</p>
          </section>
        </div>
        <section class="sourcing-review-panel">
          <div>
            <span class="catalog-eyebrow">Risk-aware sourcing</span>
            <h2>What Taotao Sourcing can check</h2>
            <p>We review the supplier's observable business identity, production fit, quotation assumptions and model-specific documents. Factory visits and production follow-up can be arranged when required.</p>
          </div>
          <a class="btn btn-outline" href="services.html">View sourcing services</a>
        </section>
        {('<section class="related-products"><h2>Related products</h2><div class="catalog-product-grid">' + related_cards + '</div></section>') if related_cards else ''}
        <div class="cta-band">
          <div><h2>Ask about this product</h2><p>Include your target market, estimated quantity, required documents, logo or packaging needs, and delivery destination.</p></div>
          <div class="hero-actions">
            <a class="btn btn-red" href="contact.html?product={quote(product.get('model') or product['name'])}">Start an Inquiry</a>
            <a class="btn btn-wa" href="https://wa.me/{WHATSAPP}?text={inquiry}" target="_blank" rel="noreferrer">Ask on WhatsApp</a>
          </div>
        </div>
      </div>
    </section>
  </main>
  <script type="application/ld+json">{schema}</script>
{footer()}"""


def update_sitemap(generated: list[str]) -> None:
    path = ROOT / "sitemap.xml"
    existing = path.read_text(encoding="utf-8")
    records = []
    seen = set()
    for block in re.findall(r"<url>.*?</url>", existing, flags=re.S):
        match = re.search(r"<loc>([^<]+)</loc>", block)
        if not match:
            continue
        loc = match.group(1)
        if Path(urlparse(loc).path).name.startswith("product-"):
            continue
        if loc not in seen:
            lines = [line.strip() for line in block.strip().splitlines()]
            records.append("\n".join(
                line if index in (0, len(lines) - 1) else "  " + line
                for index, line in enumerate(lines)
            ))
            seen.add(loc)
    for name in generated:
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
    path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'{body}\n</urlset>\n',
        encoding="utf-8",
    )


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    categories = {item["slug"]: item for item in data["categories"]}
    products = data["products"]
    slugs = [item["slug"] for item in products]
    if len(slugs) != len(set(slugs)):
        raise SystemExit("Duplicate product slug found")
    representative = None
    if REPRESENTATIVE_PATH.exists():
        manifest = json.loads(REPRESENTATIVE_PATH.read_text(encoding="utf-8"))
        representative = set(manifest.get("indexableProductPages", []))
    generated = []
    built_categories = 0
    for category_slug, category in categories.items():
        if category.get("albumPage"):
            continue
        category_products = [item for item in products if item["category"] == category_slug]
        if not category_products and not category.get("holdMessage"):
            raise SystemExit(f"No product records or hold message for category: {category_slug}")
        if representative is None:
            detail_name = f"detail-{category_slug}.html"
            (ROOT / detail_name).write_text(render_category(category, category_products), encoding="utf-8")
            built_categories += 1
        for product in category_products:
            name = f"product-{product['slug']}.html"
            if representative is not None and name not in representative:
                continue
            related = [
                item for item in category_products
                if item["slug"] != product["slug"]
                and (representative is None or f"product-{item['slug']}.html" in representative)
            ]
            indexable = representative is None or name in representative
            (ROOT / name).write_text(
                render_product(product, category, related, indexable=indexable), encoding="utf-8")
            if indexable:
                generated.append(name)
    update_sitemap(generated)
    print(f"Built {built_categories} category pages and {len(generated)} representative product pages.")


if __name__ == "__main__":
    main()
