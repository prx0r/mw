from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_json(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256_text(payload)


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_digest(root: str | Path) -> str:
    """Stable digest of relative path + content digests, ignoring .git."""
    base = Path(root)
    entries: list[tuple[str, str]] = []
    for p in sorted(base.rglob("*")):
        if not p.is_file() or ".git" in p.parts:
            continue
        entries.append((p.relative_to(base).as_posix(), sha256_file(p)))
    return sha256_json(entries)
