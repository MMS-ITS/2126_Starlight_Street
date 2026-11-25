#!/usr/bin/env python3
"""Download the dated public image set recorded in image_manifest.json."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
MANIFEST = ASSETS / "image_manifest.json"
USER_AGENT = "Mozilla/5.0 (compatible; StarlightStreetFlyer/1.0; +https://github.com/MMS-ITS/2126_Starlight_Street)"


def download(url: str, target: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
    if not data:
        raise RuntimeError(f"Empty response for {url}")
    target.write_bytes(data)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures: list[tuple[str, str]] = []
    for index, item in enumerate(manifest["images"], start=1):
        target = ASSETS / item["file"]
        if target.exists() and target.stat().st_size > 0:
            print(f"[{index:02d}] keep     {target.name}")
            continue
        try:
            download(item["url"], target)
            print(f"[{index:02d}] download {target.name} ({target.stat().st_size:,} bytes)")
        except (OSError, urllib.error.URLError, RuntimeError) as exc:
            failures.append((target.name, str(exc)))
            print(f"[{index:02d}] FAILED   {target.name}: {exc}")
        time.sleep(0.08)

    if failures:
        details = "\n".join(f"- {name}: {error}" for name, error in failures)
        raise SystemExit(f"\n{len(failures)} download(s) failed:\n{details}")


if __name__ == "__main__":
    main()
