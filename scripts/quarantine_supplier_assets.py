#!/usr/bin/env python3
"""Move blocked supplier-identifying assets out of the published site tree.

Originals are preserved under ``_supplier-originals`` with their relative path.
That directory is excluded from the GitHub Pages build by ``_config.yml``.
"""

from __future__ import annotations

import shutil
import json
from pathlib import Path

from image_privacy import is_blocked_image


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOT = ROOT / "assets" / "products"
ARCHIVE_ROOT = ROOT / "_supplier-originals"
RULES_PATH = ROOT / "data" / "supplier-image-privacy.json"


def main() -> int:
    candidates = [path for path in PUBLIC_ROOT.rglob("*") if path.is_file()]
    blocked = [path for path in candidates if is_blocked_image(path.relative_to(ROOT).as_posix())]
    rules = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    blocked_pages = [ROOT / value for value in rules.get("blockedPublicFiles", [])]
    sources = sorted(blocked + [path for path in blocked_pages if path.is_file()])
    moved = 0
    for source in sources:
        relative = source.relative_to(ROOT)
        destination = ARCHIVE_ROOT / relative
        if destination.exists():
            raise SystemExit(
                f"Refusing to overwrite preserved original: {destination.relative_to(ROOT)}"
            )
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        moved += 1
    print(f"Preserved {moved} blocked supplier files under {ARCHIVE_ROOT.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
