#!/usr/bin/env python3
"""Replace public references to blocked supplier-identifying images."""

from __future__ import annotations

import re
from pathlib import Path

from image_privacy import is_blocked_image, placeholder


ROOT = Path(__file__).resolve().parents[1]
IMAGE_REF = re.compile(
    r"assets/products/[A-Za-z0-9_./-]+\.(?:jpe?g|png|webp|svg)",
    flags=re.IGNORECASE,
)
GALLERY = re.compile(
    r'(<div class="[^"]*\bproduct-gallery\b[^"]*">)(.*?)(</div>)',
    flags=re.IGNORECASE | re.DOTALL,
)
IMAGE_TAG = re.compile(r'<img\b[^>]*\bsrc="([^"]+)"[^>]*>', flags=re.IGNORECASE)


def main() -> int:
    changed_files = 0
    replaced_references = 0
    removed_gallery_images = 0
    for path in sorted(ROOT.glob("*.html")):
        before = path.read_text(encoding="utf-8")
        file_replacements = 0
        file_removals = 0

        def clean_gallery(match: re.Match[str]) -> str:
            nonlocal file_replacements, file_removals
            opening, body, closing = match.groups()
            tags = list(IMAGE_TAG.finditer(body))
            if not tags:
                return match.group(0)
            blocked = [tag for tag in tags if is_blocked_image(tag.group(1))]
            if not blocked:
                return match.group(0)
            clean_exists = any(not is_blocked_image(tag.group(1)) for tag in tags)
            keep_placeholder = not clean_exists
            kept_placeholder = False

            def clean_tag(tag_match: re.Match[str]) -> str:
                nonlocal kept_placeholder, file_replacements, file_removals
                value = tag_match.group(1)
                if not is_blocked_image(value):
                    return tag_match.group(0)
                if keep_placeholder and not kept_placeholder:
                    kept_placeholder = True
                    file_replacements += 1
                    return tag_match.group(0).replace(value, placeholder(), 1)
                file_removals += 1
                return ""

            return opening + IMAGE_TAG.sub(clean_tag, body) + closing

        after = GALLERY.sub(clean_gallery, before)

        def replace_reference(match: re.Match[str]) -> str:
            nonlocal file_replacements
            value = match.group(0)
            if not is_blocked_image(value):
                return value
            file_replacements += 1
            return placeholder()

        after = IMAGE_REF.sub(replace_reference, after)
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed_files += 1
            replaced_references += file_replacements
            removed_gallery_images += file_removals
    print(
        f"Replaced {replaced_references} supplier-image references and removed "
        f"{removed_gallery_images} redundant branded gallery images across "
        f"{changed_files} HTML files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
