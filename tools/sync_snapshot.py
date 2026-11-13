#!/usr/bin/env python3
"""Pinned public hub -> Projects-Displays mirror. Never writes to MyProjects.

Default mode is read-only; --write explicitly copies the whole 123-asset
canonical publication. Partial regeneration is forbidden.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
HUB_SHA = "32af5dbb4bb7c9c261bd1d7e022341aaaa7bc916"
ROOT_FILES = (
    "index.html", "acquisition.html", "methodology.html", "sources.html",
    "404.html", "robots.txt", "sitemap.xml", "catalogue.csv",
    "identity-register.csv", "project-map.json", "PRESENTATION_NOTICE.txt",
    ".nojekyll"
)


def require(test, message):
    if not test:
        raise ValueError(message)


def paths(root):
    for name in ROOT_FILES:
        yield root / name
    for name in ("assets", "products"):
        yield from sorted(p for p in (root / name).rglob("*") if p.is_file())


def sync(hub, write=False):
    hub = Path(hub).resolve()
    sha = subprocess.check_output(
        ["git", "-C", str(hub), "rev-parse", "HEAD"], text=True
    ).strip()
    require(sha == HUB_SHA, "Hub source HEAD mismatch; refusing sync: " + sha)
    source = hub / "displays"
    require(source.is_dir(), "Missing canonical public displays")
    data = json.loads((source / "assets/buyer-catalogue.json").read_text())
    require(data == json.loads((hub / "assets/buyer-catalogue.json").read_text()),
            "Canonical catalogue mismatch")
    projects = data["projects"]
    require([a["ref"] for a in projects] ==
            ["TA-IP-%03d" % n for n in range(1, 124)], "123 project IDs required")
    require(len({a["slug"] for a in projects}) == 123, "Duplicate project slugs")
    require(len({a["referenceName"].casefold() for a in projects}) == 123,
            "Duplicate identity aliases")
    require(sum(int(a["askingReferenceEUR"]) for a in projects) == 25153000,
            "Unexpected dated seller reference total")
    price = json.loads((source / "assets/pricing-catalogue.json").read_text())
    require(len(price["projects"]) == 123 and
            price["portfolio"]["sellerAskEUR"] == 25153000,
            "123-asset pricing contract missing")
    mapping = json.loads((source / "project-map.json").read_text())
    require(mapping["projectCount"] == len(mapping["projects"]) == 123,
            "123-asset map contract missing")
    for a in projects:
        directory = source / "products" / a["slug"]
        for name in ("index.html", "product-brief.md", "factsheet.pdf"):
            file = directory / name
            require(file.is_file() and file.stat().st_size > 100,
                    "Missing buyer document: " + str(file))
        require((directory / "factsheet.pdf").read_bytes().startswith(b"%PDF-"),
                "Invalid factsheet PDF header")
    require((source / "index.html").read_text().count('class="asset-card"') == 123,
            "Collection count drift")
    origin = {p.relative_to(source).as_posix() for p in paths(source)}
    require(len(origin) == 430, "Pinned source file set count drift")

    if write:
        for folder in ("assets", "products"):
            target = ROOT / folder
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source / folder, target)
        for name in ROOT_FILES:
            shutil.copy2(source / name, ROOT / name)

    current = {p.relative_to(ROOT).as_posix() for p in paths(ROOT)}
    require(current == origin,
            "Mirror has missing or extra files: missing=%s extra=%s" %
            (sorted(origin - current), sorted(current - origin)))
    for path in sorted(origin):
        a = (ROOT / path).read_bytes()
        b = (source / path).read_bytes()
        require(hashlib.sha256(a).digest() == hashlib.sha256(b).digest(),
                "Public mirror drift: " + path)

    if write:
        report = (
            "# Public display snapshot verification — 13 November 2026\n\n"
            f"- Canonical public source: [MyProjects](https://github.com/TheArchitect-max/MyProjects/tree/{HUB_SHA}/displays)\n"
            f"- Pinned source commit: \x60{HUB_SHA}\x60\n"
            "- Assets: **123 distinct TA-IP identifiers**, each with unique slug and alias.\n"
            "- Public display documents: **123 HTML pages, 123 product briefs and 123 PDF files** checked.\n"
            "- Seller asking reference total: **EUR 25,153,000** (10 November 2026 seller inputs; not independently appraised).\n"
            f"- Source-mirrored files verified by SHA-256: **{len(origin)}**.\n"
            "- This receipt verifies publication consistency, not source-code ownership, release readiness, market value, production operation or rights clearance.\n"
            "- This repository is a static catalogue; no SaaS backend, sessions, database or payment processing is hosted on GitHub Pages or Actions.\n"
        )
        (ROOT / "PUBLICATION_AUDIT_2026-11-13.md").write_text(report)
    return {"result": "PASS", "mode": "WRITE" if write else "CHECK_ONLY",
            "sourceHead": HUB_SHA, "assetCount": 123,
            "mirroredSHA256Files": len(origin), "sellerAsksEUR": 25153000}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hub", type=Path, help="Pinned local MyProjects checkout")
    parser.add_argument("--write", action="store_true",
                        help="Explicitly mirror all 123 files (never hub-side writes)")
    args = parser.parse_args()
    print(json.dumps(sync(args.hub, write=args.write), indent=2))
