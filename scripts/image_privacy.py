"""Public-image privacy rules for supplier-identifying source material."""

from __future__ import annotations

import fnmatch
import json
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "data" / "supplier-image-privacy.json"


@lru_cache(maxsize=1)
def rules() -> dict:
    return json.loads(RULES_PATH.read_text(encoding="utf-8"))


def normalize_image_path(value: str | None) -> str:
    if not value:
        return ""
    parsed = urlparse(str(value))
    path = parsed.path.lstrip("/")
    return path


def is_blocked_image(value: str | None) -> bool:
    path = normalize_image_path(value)
    if not path:
        return False
    config = rules()
    if path in set(config.get("blockedPaths", [])):
        return True
    if Path(path).name in set(config.get("blockedBasenames", [])):
        return True
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in config.get("blockedGlobs", []))


def placeholder() -> str:
    return str(rules()["placeholder"])


def public_image(value: str | None) -> str:
    return placeholder() if not value or is_blocked_image(value) else str(value)


def public_images(values) -> list[str]:
    clean = []
    for value in values or []:
        if value and not is_blocked_image(value) and value not in clean:
            clean.append(str(value))
    return clean or [placeholder()]
