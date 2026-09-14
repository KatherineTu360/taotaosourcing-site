#!/usr/bin/env python3
"""Small deterministic checks for the generated Taotao Sourcing static site."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DATA = ROOT / "data" / "catalog-products.json"
PRIVATE_MAP = Path(
    "/Users/katherinetu/CODEX/独立站/website-optimization/run/"
    "taotaosourcing-products-2026-09-13/publication-source-map.json"
)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.h1 = 0
        self.title = []
        self.in_title = False
        self.links = []
        self.images = []
        self.canonicals = []
        self.descriptions = []

    def handle_starttag(self, tag: str, attrs) -> None:
        values = dict(attrs)
        if tag == "h1":
            self.h1 += 1
        elif tag == "title":
            self.in_title = True
        elif tag == "a" and values.get("href"):
            self.links.append(values["href"])
        elif tag == "img":
            if values.get("src"):
                self.images.append((values["src"], values.get("alt")))
        elif tag == "link" and values.get("rel") == "canonical":
            self.canonicals.append(values.get("href", ""))
        elif tag == "meta" and values.get("name") == "description":
            self.descriptions.append(values.get("content", ""))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title.append(data)


def local_target(value: str) -> str | None:
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc or value.startswith(("mailto:", "tel:", "#")):
        return None
    return unquote(parsed.path)


def main() -> None:
    errors = []
    warnings = []
    titles = {}
    canonicals = {}
    files = sorted(path for path in ROOT.glob("*.html") if not path.name.startswith("google"))
    forbidden = ["/Users/katherinetu/", "Dior", "Givenchy", "Chanel", "Loewe", "Miu Miu", "Goyard", "Louis Vuitton"]

    for path in files:
        text = path.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(text)
        if parser.h1 != 1:
            errors.append(f"{path.name}: expected one H1, found {parser.h1}")
        title = "".join(parser.title).strip()
        if not title:
            errors.append(f"{path.name}: missing title")
        elif title in titles:
            warnings.append(f"duplicate title: {path.name} and {titles[title]}")
        else:
            titles[title] = path.name
        if len(parser.canonicals) != 1:
            errors.append(f"{path.name}: expected one canonical, found {len(parser.canonicals)}")
        else:
            canonical = parser.canonicals[0]
            if canonical in canonicals:
                errors.append(f"duplicate canonical: {path.name} and {canonicals[canonical]}")
            canonicals[canonical] = path.name
        if len(parser.descriptions) != 1 or not parser.descriptions[0].strip():
            errors.append(f"{path.name}: missing meta description")
        for src, alt in parser.images:
            target = local_target(src)
            if target and not (ROOT / target).exists():
                errors.append(f"{path.name}: missing image {target}")
            if alt is None or not alt.strip():
                errors.append(f"{path.name}: image without alt {src}")
        for href in parser.links:
            target = local_target(href)
            if not target:
                continue
            resolved = ROOT / target
            if target.endswith("/"):
                resolved = resolved / "index.html"
            if not resolved.exists():
                errors.append(f"{path.name}: broken link {href}")
        for token in forbidden:
            if token.lower() in text.lower():
                errors.append(f"{path.name}: forbidden token {token}")
        if path.name.startswith("product-"):
            if '"@type":"Product"' in text or '"@type": "Product"' in text:
                errors.append(f"{path.name}: Product JSON-LD is not allowed without offer/review data")
            if "wa.me/8616626662274?text=" not in text:
                errors.append(f"{path.name}: missing product-specific WhatsApp link")

    data = json.loads(PUBLIC_DATA.read_text(encoding="utf-8"))
    private = json.loads(PRIVATE_MAP.read_text(encoding="utf-8"))
    public_slugs = {item["slug"] for item in data["products"]}
    source_slugs = set(private["sourceMap"])
    missing_source = public_slugs - source_slugs
    if missing_source:
        errors.append(f"public products missing source map: {sorted(missing_source)}")
    for item in data["products"]:
        expected = ROOT / f"product-{item['slug']}.html"
        if not expected.exists():
            errors.append(f"missing generated product page: {expected.name}")
        if "internal source" in item.get("model", "").lower():
            errors.append(f"{item['slug']}: internal reference leaked into public model field")
        evidence = private["sourceMap"].get(item["slug"], [])
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{item['slug']}: source evidence must be a non-empty list")

    catalog_html = (ROOT / "products.html").read_text(encoding="utf-8")
    category_slugs = {item["slug"] for item in data["categories"]}
    for category in data["categories"]:
        detail_name = f"detail-{category['slug']}.html"
        detail_path = ROOT / detail_name
        if not detail_path.exists():
            errors.append(f"missing category page: {detail_name}")
            continue
        if detail_name not in catalog_html:
            errors.append(f"products.html missing category link: {detail_name}")
        detail_html = detail_path.read_text(encoding="utf-8")
        category_products = [item for item in data["products"] if item["category"] == category["slug"]]
        if not category_products and not category.get("holdMessage"):
            errors.append(f"{category['slug']}: no products and no hold message")
        for item in category_products:
            product_name = f"product-{item['slug']}.html"
            if product_name not in detail_html:
                errors.append(f"{detail_name}: missing product link {product_name}")

    unknown_categories = {item["category"] for item in data["products"]} - category_slugs
    if unknown_categories:
        errors.append(f"products use unknown categories: {sorted(unknown_categories)}")

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for item in data["products"]:
        url = f"https://taotaosourcing.com/product-{item['slug']}.html"
        if url not in sitemap:
            errors.append(f"sitemap missing {url}")
    for category in data["categories"]:
        url = f"https://taotaosourcing.com/detail-{category['slug']}.html"
        if url not in sitemap:
            errors.append(f"sitemap missing {url}")

    print(f"Checked {len(files)} HTML pages and {len(public_slugs)} public product records.")
    for item in warnings:
        print("WARNING:", item)
    if errors:
        for item in errors:
            print("ERROR:", item)
        print(f"FAILED with {len(errors)} errors and {len(warnings)} warnings.")
        return 1
    print(f"PASS with {len(warnings)} warnings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
