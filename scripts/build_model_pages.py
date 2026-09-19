#!/usr/bin/env python3
"""Model detail-page rendering (MX802-style template) for build_hierarchy."""
import json
import shutil
from pathlib import Path
from urllib.parse import quote

from model_copy import build as build_copy

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "products"
HQ_RUN = Path("/Users/katherinetu/CODEX/独立站/website-optimization/run/"
              "taotaosourcing-hierarchy-2026-09-18")
GALLERY_MANIFEST = HQ_RUN / "gallery_manifest.json"
HQ_ROOT = HQ_RUN / "extracted_hq"
GALLERY_ASSETS = ASSETS / "gallery"

FAQS = [
    ("What is the MOQ for the {m}?",
     "Minimum order quantity depends on the model, colour and level of customization. "
     "Send your target quantity with your inquiry and we confirm pricing and availability with the factory."),
    ("What is the lead time for the {m}?",
     "Lead time depends on order size and customization. We confirm a realistic delivery "
     "schedule in the quotation based on the factory's current production plan."),
    ("Can I review a sample of the {m} first?",
     "Yes. Sample terms are confirmed in the quotation, and bulk production starts only "
     "after the approved sample."),
    ("Which documents apply to the {m}?",
     "We request the model-specific documents that apply to your destination market from "
     "the supplier and share them before order confirmation."),
]


def allocate_slug(base_slug, taken):
    slug = base_slug or "model"
    candidate = slug
    n = 2
    while candidate in taken:
        candidate = f"{slug}-{n}"
        n += 1
    taken.add(candidate)
    return candidate


def copy_gallery(key, slug):
    """Copy manifest gallery images for key into assets; return asset paths."""
    if not GALLERY_MANIFEST.exists():
        return []
    rel_paths = json.loads(GALLERY_MANIFEST.read_text()).get(key) or []
    out = []
    for i, rel in enumerate(rel_paths):
        src = HQ_RUN / rel
        if not src.exists():
            continue
        suffix = f"-{i}" if i else ""
        dest = GALLERY_ASSETS / f"{slug}{suffix}.jpg"
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            shutil.copy2(src, dest)
        out.append(f"assets/products/gallery/{dest.name}")
    return out


def render_model_detail(entry, cat, group, sub, siblings, canonical_slug,
                        page_head, header, footer, breadcrumb_json, esc, WHATSAPP, DOMAIN):
    raw = entry.get("_raw", {})
    c = build_copy(entry["source"], {
        "model": entry["model"], "id": entry["id"], "name": entry.get("name"),
        "type": raw.get("type"),
        "spec": raw.get("spec"), "shell": raw.get("shell"), "sizes": raw.get("sizes"),
        "cert": raw.get("cert"), "refrigerant": raw.get("refrigerant"),
        "capacity": raw.get("capacity"), "material": raw.get("material"),
        "page": entry.get("page"),
    })
    title = c["title"]
    canonical = f"{DOMAIN}/product-{canonical_slug}.html"
    wa_text = quote(f"Hello Katherine, I'm interested in {entry['model']}. Target market and quantity: ")

    gallery = entry.get("gallery") or []
    if not gallery and entry.get("image"):
        gallery = [entry["image"]]
    if gallery:
        main_img, thumbs = gallery[0], gallery[1:]
        gallery_html = (
            f'<img src="{esc(main_img)}" alt="{esc(title)} product photo">'
            + "".join(
                f'<img src="{esc(t)}" alt="{esc(title)} catalogue view {i + 2}" loading="lazy">'
                for i, t in enumerate(thumbs))
        )
    else:
        gallery_html = ('<div class="model-img-placeholder"><span>Photos available on request — '
                        'catalogue page reference is listed in the specifications.</span></div>')

    spec_rows = "\n".join(
        f"            <tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in c["spec_rows"])
    benefits = "\n".join(
        f'          <div class="benefit"><h3>{esc(b[0])}</h3><p>{esc(b[1])}</p></div>'
        for b in c["benefits"])
    faqs = "\n".join(
        f'          <details class="faq-item"><summary>{esc(q.format(m=entry["model"]))}</summary>'
        f'<p>{esc(a)}</p></details>' for q, a in FAQS)

    related = []
    for sib in siblings:
        if sib is entry:
            continue
        href = sib.get("detail")
        if not href:
            continue
        img = (sib.get("gallery") or [sib.get("image") or "assets/logo.png"])[0]
        related.append(
            '        <article class="catalog-product-card">\n'
            f'          <a class="catalog-product-media" href="{esc(href)}">\n'
            f'            <img src="{esc(img)}" alt="{esc(sib["name"])}" loading="lazy">\n'
            '          </a>\n'
            '          <div class="catalog-product-body">\n'
            f'            <span class="catalog-badge">{esc(sib["model"])}</span>\n'
            f'            <h3><a href="{esc(href)}">{esc(sib["name"])}</a></h3>\n'
            f'            <a class="more" href="{esc(href)}">View details →</a>\n'
            '          </div>\n'
            '        </article>')
    related_html = "\n".join(related[:8]) or \
        "        <p>Related models from the same series are listed on the series page above.</p>"

    crumbs = [("Home", DOMAIN + "/"), ("Products", DOMAIN + "/products.html"),
              (cat["title"], f"{DOMAIN}/detail-{cat['slug']}.html")]
    if group is not sub:
        crumbs.append((group["title"], f"{DOMAIN}/{group['_url_file']}"))
    crumbs.append(((sub.get("title") or group["title"]), f"{DOMAIN}/{sub['_url_file']}"))
    crumbs.append((title, canonical))
    faq_schema = json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q.format(m=entry["model"]),
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in FAQS
        ],
    }, ensure_ascii=False, separators=(",", ":"))
    schema = breadcrumb_json(crumbs) + '</script><script type="application/ld+json">' + faq_schema
    trail = " / ".join(f'<a href="{u}">{esc(t)}</a>' for t, u in crumbs[:-1]) + f" / {esc(title)}"

    return f"""{page_head(c["seo_title"], c["meta_desc"], canonical, gallery[0] if gallery else "assets/logo.png")}
{header()}
  <main>
    <section class="page-hero product-page-hero">
      <div class="container">
        <div class="breadcrumb">{trail}</div>
        <span class="catalog-eyebrow">{esc(entry["model"])}</span>
        <h1>{esc(title)}</h1>
        <p>{esc(c["overview"])}</p>
      </div>
    </section>
    <section class="section product-detail-section">
      <div class="container">
        <div class="product-detail-grid">
          <div class="product-gallery model-gallery">
{gallery_html}
          </div>
          <div class="product-facts">
            <span class="catalog-badge">{esc(entry["model"])}</span>
            <h2>Product overview</h2>
            <p>{esc(c["overview"])}</p>
            <div class="hero-actions product-actions">
              <a class="btn btn-red" href="contact.html?product={quote(entry['model'])}">Request a Quotation</a>
              <a class="btn btn-wa" href="https://wa.me/{WHATSAPP}?text={wa_text}" target="_blank" rel="noreferrer">WhatsApp Katherine</a>
            </div>
          </div>
        </div>
        <div class="product-info-grid">
          <section class="product-info-card">
            <h2>Specifications</h2>
            <div class="spec-table-wrap">
              <table class="spec-table"><tbody>
{spec_rows}
              </tbody></table>
            </div>
          </section>
          <section class="product-info-card">
            <h2>Why buyers choose the {esc(entry["model"])}</h2>
            <div class="benefit-list">
{benefits}
            </div>
          </section>
        </div>
        <section class="model-section">
          <h2>Quality checks before shipment</h2>
          <p>{esc(c["qc"])}</p>
        </section>
        <section class="model-section">
          <h2>OEM / ODM and branding</h2>
          <p>{esc(c["oem"])}</p>
        </section>
        <section class="model-section model-faq">
          <h2>Frequently asked questions</h2>
{faqs}
        </section>
        <section class="related-products">
          <h2>Related models</h2>
          <div class="catalog-product-grid">
{related_html}
          </div>
        </section>
        <div class="cta-band">
          <div><h2>Request a quotation</h2><p>Include your target market, estimated quantity and required documents. We confirm specifications and certificate scope with the factory before you commit.</p></div>
          <div class="hero-actions">
            <a class="btn btn-red" href="contact.html?product={quote(entry['model'])}">Start an Inquiry</a>
            <a class="btn btn-wa" href="https://wa.me/{WHATSAPP}?text={wa_text}" target="_blank" rel="noreferrer">Ask on WhatsApp</a>
          </div>
        </div>
      </div>
    </section>
  </main>
  <script type="application/ld+json">{schema}</script>
{footer()}"""
