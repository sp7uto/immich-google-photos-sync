#!/usr/bin/env python3
"""Synchronize documentation images and README/wiki image references.

Only the three publicly shared Google Photos images are downloaded.
Run from the repository root. Designed for GitHub Actions.
"""
from __future__ import annotations

import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMAGES = ROOT / "docs" / "images"
ART = {
    "immich-header.jpg": "https://lh3.googleusercontent.com/pw/AP1GczOFyuxkUmxTsORsaXX6z2ky94-m6qMV_rm_fHo96uzQChurOYTJR8zOftdc5SgQ745nWGmuIxAoi5OX2zZPKinELqY59ku1EDk10si_CTlP4Baz5oBY=s1411-n-no",
    "immich-workflow.jpg": "https://lh3.googleusercontent.com/pw/AP1GczMUBirbcJRiuUbSyVrv8e06zZLMWNNODuSf2ysG_JHYbZ4DDgWliS3VCKEzv0EBgd98vyV5F-RJ_q9x2eXdupkoEKFj1zvh3YgtLTpVDfQ66g0At-d5=s1411-n-no",
    "immich-footer.jpg": "https://lh3.googleusercontent.com/pw/AP1GczOdZak7C7uZuOD717B6_A_k-ivTrg4ONLaivtfLTEjXupgvEqJdDBpV3zKVu1pAhKXWiOmYe18GxvhPIVaV_IWwfhYFD24cg4zedowT0QV-uQvlQHhr=s1411-n-no",
}

def ensure_images() -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    for name, url in ART.items():
        dest = IMAGES / name
        if dest.exists() and dest.stat().st_size > 10000:
            print(f"Already stored: {dest}")
            continue
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        # Public Google Photos previews use a different URL modifier from viewer thumbnails.
        # Attempt a larger public preview first, then the known Open Graph preview.
        data = None
        ctype = ""
        last_error = None
        for suffix in ("=w1200-h630-p-k", "=w600-h315-p-k"):
            candidate = url.split("=")[0] + suffix
            req = urllib.request.Request(candidate, headers={"User-Agent": "Mozilla/5.0", "Accept": "image/*"})
            try:
                with urllib.request.urlopen(req, timeout=45) as r:
                    data = r.read(10_000_001)
                    ctype = r.headers.get("Content-Type", "")
                if data.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"RIFF")):
                    break
            except Exception as exc:
                last_error = exc
                print(f"Preview not available: {suffix}: {exc}")
                data = None
        if data is None:
            raise RuntimeError(f"{name}: Google Photos previews not downloadable: {last_error}")
        if len(data) < 10000 or len(data) > 10_000_000:
            raise RuntimeError(f"{name}: unexpected image size {len(data)}")
        if not (data.startswith(b"\xff\xd8\xff") or data.startswith(b"\x89PNG\r\n\x1a\n") or data.startswith(b"RIFF")):
            raise RuntimeError(f"{name}: not an expected raster image, Content-Type={ctype}")
        # Use the file's actual format, not a misleading extension.
        if data.startswith(b"\xff\xd8\xff"):
            ext = "jpg"
        elif data.startswith(b"\x89PNG"):
            ext = "png"
        else:
            ext = "webp"
        actual = dest.with_suffix("." + ext)
        actual.write_bytes(data)
        print(f"Downloaded: {actual} ({len(data)} bytes)")
        if actual != dest and dest.exists():
            dest.unlink()

def replace_links() -> None:
    for path in (ROOT / "README.md", ROOT / "README.pl.md",
                 ROOT / "docs/wiki/Home.md", ROOT / "docs/wiki/Home-PL.md"):
        text = path.read_text(encoding="utf-8")
        for name, old in ART.items():
            matches = list((IMAGES).glob(name.rsplit(".", 1)[0] + ".*"))
            matches = [p for p in matches if p.suffix.lower() in {".jpg", ".png", ".webp"}]
            if len(matches) != 1:
                raise RuntimeError(f"{name}: exactly one local image required, got {matches}")
            stored = matches[0].name
            direct = ("https://raw.githubusercontent.com/sp7uto/immich-google-photos-sync/"
                      "main/docs/images/" + stored)
            text = text.replace(old, direct)
        path.write_text(text, encoding="utf-8")
        print(f"Rewrote: {path.relative_to(ROOT)}")

if __name__ == "__main__":
    ensure_images()
    replace_links()
