#!/usr/bin/env python3
"""Mirror the pinned, already public MyProjects/displays snapshot. No SaaS runtime."""
from pathlib import Path
import csv, hashlib, json, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
HUB_SHA = "28f29a547d0a753825e09c1e80ba75ac81014515"
FILES = ("index.html", "acquisition.html", "methodology.html", "sources.html",
         "404.html", "robots.txt", "sitemap.xml", "catalogue.csv",
         "identity-register.csv", "project-map.json", "PRESENTATION_NOTICE.txt", ".nojekyll")

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python tools/sync_snapshot.py /path/to/MyProjects")
    hub = Path(sys.argv[1]).resolve()
    actual = subprocess.check_output(["git", "-C", str(hub), "rev-parse", "HEAD"], text=True).strip()
    assert actual == HUB_SHA, f"Source drift: {actual} != {HUB_SHA}"
    src = hub / "displays"
    assert src.is_dir() and (hub / "assets" / "buyer-catalogue.json").is_file()
    catalogue = json.loads((src / "assets" / "buyer-catalogue.json").read_text(encoding="utf-8"))
    assert catalogue == json.loads((hub / "assets" / "buyer-catalogue.json").read_text(encoding="utf-8"))
    projects = catalogue["projects"]
    assert len(projects) == 123
    assert [p["ref"] for p in projects] == [f"TA-IP-{n:03}" for n in range(1, 124)]
    assert len({p["slug"] for p in projects}) == 123
    assert len({p["referenceName"] for p in projects}) == 123
    assert sum(int(p["askingReferenceEUR"]) for p in projects) == 25153000
    assert len(json.loads((src / "assets" / "pricing-catalogue.json").read_text())["projects"]) == 123
    assert len(json.loads((src / "assets" / "buyer-dossiers.json").read_text())["projects"]) == 123
    mapped = json.loads((src / "project-map.json").read_text())
    assert mapped["projectCount"] == len(mapped["projects"]) == 123
    with (src / "catalogue.csv").open(encoding="utf-8-sig", newline="") as f:
        assert len(list(csv.DictReader(f))) == 123
    for project in projects:
        p = src / "products" / project["slug"]
        for name in ("index.html", "product-brief.md", "factsheet.pdf"):
            f = p / name
            assert f.is_file() and f.stat().st_size > 100, f
        assert (p / "factsheet.pdf").read_bytes()[:5] == b"%PDF-"
    idx = (src / "index.html").read_text(encoding="utf-8")
    assert idx.count('class="asset-card"') == 123
    for name in FILES:
        assert (src / name).is_file()
    for name in ("assets", "products"):
        dest = ROOT / name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src / name, dest)
    for name in FILES:
        shutil.copy2(src / name, ROOT / name)
    count = 0
    for p in src.rglob("*"):
        if not p.is_file() or p.relative_to(src).parts[0] not in ("assets", "products", *FILES):
            continue
        local = ROOT / p.relative_to(src)
        assert local.is_file()
        assert hashlib.sha256(local.read_bytes()).digest() == hashlib.sha256(p.read_bytes()).digest(), str(p)
        count += 1
    report = (
        "# Public display snapshot verification — 13 November 2026\n\n"
        f"- Canonical public source: [MyProjects](https://github.com/TheArchitect-max/MyProjects/tree/{HUB_SHA}/displays)\n"
        f"- Pinned source commit: \x60{HUB_SHA}\x60\n"
        "- Assets: **123 distinct TA-IP identifiers**, each with unique slug and alias.\n"
        "- Public display documents: **123 HTML pages, 123 product briefs and 123 PDF files** checked.\n"
        "- Seller asking reference total: **EUR 25,153,000** (10 November 2026 seller inputs; not independently appraised).\n"
        f"- Source-mirrored files verified by SHA-256: **{count}**.\n"
        "- This receipt verifies publication consistency, not source-code ownership, release readiness, market value, production operation or rights clearance.\n"
        "- This repository is a static catalogue; no SaaS backend, sessions, database or payment processing is hosted on GitHub Pages or Actions.\n"
    )
    (ROOT / "PUBLICATION_AUDIT_2026-11-13.md").write_text(report, encoding="utf-8")
    print("STATIC_PUBLICATION_SYNC=PASS; assets=123; files_sha256_verified=", count)

if __name__ == "__main__":
    main()
