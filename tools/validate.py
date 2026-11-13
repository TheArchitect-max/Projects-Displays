#!/usr/bin/env python3
"""Fail-closed audit of all published 123 public IP displays and pinned hub mirror.

Read-only; validates the actual published files, not a legacy 119-asset template.
Usage: python3 tools/validate.py /path/to/pinned/MyProjects
Requires pypdf for PDF text and page-level checks (CI-only dependency).
"""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
import argparse
import csv
import hashlib
import json
import re
import subprocess

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
PIN = "28f29a547d0a753825e09c1e80ba75ac81014515"
EXPECTED_COUNT = 123
EXPECTED_SELLER_TOTAL = 25153000
EXPECTED_MIRROR_FILES = 430
ROOT_PUBLIC_FILES = (
    "index.html", "acquisition.html", "methodology.html", "sources.html",
    "404.html", "robots.txt", "sitemap.xml", "catalogue.csv",
    "identity-register.csv", "project-map.json", "PRESENTATION_NOTICE.txt",
    ".nojekyll"
)


def check(predicate, message):
    if not predicate:
        raise ValueError(message)


def data(path):
    return json.loads(path.read_text(encoding="utf-8"))


def records(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class Links(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        for field in ("href", "src"):
            if values.get(field):
                self.links.append(values[field])


def checked_hub(hub):
    check(hub.is_dir(), "Hub checkout does not exist")
    rev = subprocess.check_output(
        ["git", "-C", str(hub), "rev-parse", "HEAD"], text=True
    ).strip()
    check(rev == PIN, "Wrong hub source commit: " + rev)


def check_links(text, base, hub):
    count = 0
    for target in Links(text).links:
        url = urlparse(urljoin(base, target))
        if url.netloc.lower() != "thearchitect-max.github.io":
            continue
        check(url.path.startswith("/MyProjects/"), "Unapproved host path: " + target)
        suffix = unquote(url.path.removeprefix("/MyProjects/"))
        check(".." not in Path(suffix).parts, "Path traversal in public link")
        if suffix == "displays" or suffix.startswith("displays/"):
            path = ROOT / suffix.removeprefix("displays/") if suffix != "displays" else ROOT
        else:
            path = hub / suffix
        if url.path.endswith("/") or path.is_dir():
            path = path / "index.html"
        check(path.is_file(), "Broken public link: " + base + " -> " + target)
        count += 1
    return count


def mirrored_paths(root):
    paths = [root / path for path in ROOT_PUBLIC_FILES]
    for folder in ("assets", "products"):
        paths.extend(p for p in (root / folder).rglob("*") if p.is_file())
    return paths


def validate(hub):
    hub = Path(hub).resolve()
    checked_hub(hub)
    origin = hub / "displays"
    expected_files = {
        p.relative_to(origin).as_posix() for p in mirrored_paths(origin)
    }
    actual_files = {
        p.relative_to(ROOT).as_posix() for p in mirrored_paths(ROOT)
    }
    check(expected_files == actual_files,
          "Mirror file set drift: missing=%s, extra=%s" %
          (sorted(expected_files - actual_files), sorted(actual_files - expected_files)))
    check(len(expected_files) == EXPECTED_MIRROR_FILES,
          "Pinned publication file count drift")
    for path in sorted(expected_files):
        local, upstream = ROOT / path, origin / path
        check(hashlib.sha256(local.read_bytes()).digest() ==
              hashlib.sha256(upstream.read_bytes()).digest(),
              "Public mirror SHA-256 mismatch: " + path)

    buyer = data(ROOT / "assets/buyer-catalogue.json")
    prices = data(ROOT / "assets/pricing-catalogue.json")
    dossier = data(ROOT / "assets/buyer-dossiers.json")
    listing = data(ROOT / "project-map.json")
    projects = buyer["projects"]
    refs = ["TA-IP-%03d" % i for i in range(1, EXPECTED_COUNT + 1)]
    check([p["ref"] for p in projects] == refs, "Non-canonical buyer ID sequence")
    check({p["ref"] for p in prices["projects"]} == set(refs), "Pricing ID drift")
    check({p["ref"] for p in dossier["projects"]} == set(refs), "Dossier ID drift")
    check(listing["projectCount"] == len(listing["projects"]) == EXPECTED_COUNT,
          "Project map count drift")
    check({p["ref"] for p in listing["projects"]} == set(refs), "Project map ID drift")
    check(len({p["slug"] for p in projects}) == EXPECTED_COUNT,
          "Duplicate product slugs")
    check(len({p["referenceName"].casefold() for p in projects}) == EXPECTED_COUNT,
          "Duplicate reference aliases")
    check(sum(p["askingReferenceEUR"] for p in projects) == EXPECTED_SELLER_TOTAL,
          "Buyer seller total drift")
    check(prices["portfolio"]["sellerAskEUR"] == EXPECTED_SELLER_TOTAL,
          "Pricing total drift")
    check(prices["basisDate"] == "2026-11-10", "Financial assessment date drift")
    check(prices["displayCurrency"]["date"] == "2026-11-10",
          "Currency rate date drift")

    identity = records(ROOT / "identity-register.csv")
    commercial = records(ROOT / "catalogue.csv")
    check(len(identity) == len(commercial) == EXPECTED_COUNT, "CSV row count drift")
    check({r["Asset_ID"] for r in identity} == set(refs), "Identity CSV drift")
    check({r["Reference"] for r in commercial} == set(refs), "Catalogue CSV drift")
    by_price = {p["ref"]: p for p in prices["projects"]}
    by_dossier = {p["ref"]: p for p in dossier["projects"]}
    by_map = {p["ref"]: p for p in listing["projects"]}
    by_identity = {p["Asset_ID"]: p for p in identity}
    by_commercial = {p["Reference"]: p for p in commercial}
    for field in prices["fields"]:
        key = field["key"]
        check(prices["portfolio"][key] ==
              sum(p["values"][key] for p in prices["projects"]),
              "Aggregate pricing mismatch: " + key)

    page = (ROOT / "index.html").read_text(encoding="utf-8")
    card_refs = re.findall(
        r'<article class="asset-card"[^>]*data-project-ref="([^"]+)"', page)
    check(Counter(card_refs) == Counter(refs), "Collection card reference drift")
    check("119 INDEPENDENT ASSETS" not in page and
          not re.search(r"\b119 assets\b", page, re.I), "Legacy count on home page")

    internal_links = check_links(
        page, "https://thearchitect-max.github.io/MyProjects/displays/", hub)
    pdf_pages = 0
    for project in projects:
        ref, slug = project["ref"], project["slug"]
        folder = ROOT / "products" / slug
        html = (folder / "index.html").read_text(encoding="utf-8")
        brief = (folder / "product-brief.md").read_text(encoding="utf-8")
        pdf = PdfReader(folder / "factsheet.pdf", strict=True)
        check(len(pdf.pages) == 4, "Factsheet must have 4 pages: " + ref)
        pdf_pages += len(pdf.pages)
        pdf_text = "\n".join(p.extract_text() or "" for p in pdf.pages)
        check(ref in html and ref in brief and ref in pdf_text,
              "Missing asset reference: " + ref)
        check(project["referenceName"] in html and
              project["referenceName"] in brief, "Reference alias drift: " + ref)
        check('data-project-ref="' + ref + '"' in html,
              "Wrong product HTML ID: " + ref)
        check(project["title"] in brief, "Wrong product brief title: " + ref)
        check("Potential acquirers" in html and "Potential acquirers" in brief,
              "Buyer information missing: " + ref)
        check('href="factsheet.pdf"' in html and
              "product-brief.md" in html, "Download control missing: " + ref)
        check(by_dossier[ref]["version"] in pdf_text,
              "Missing qualified edition in PDF: " + ref)
        price = by_price[ref]
        check(price["values"]["sellerAskEUR"] ==
              project["askingReferenceEUR"], "Asking reference mismatch: " + ref)
        for field in prices["fields"]:
            value = price["values"][field["key"]]
            check(format(value, ",") in pdf_text,
                  "PDF financial field mismatch: " + ref + "/" + field["key"])
        row = by_commercial[ref]
        check(row["Project"] == project["title"] and
              int(row["sellerAskEUR"]) == project["askingReferenceEUR"],
              "Catalogue identity or amount mismatch: " + ref)
        check(by_identity[ref]["Canonical_project_title"] == project["title"] and
              by_identity[ref]["Feminine_name"] == project["referenceName"],
              "Identity CSV mismatch: " + ref)
        mapping = by_map[ref]
        check(mapping["slug"] == slug and
              mapping["referenceName"] == project["referenceName"] and
              mapping["profileUrl"] == project["profileUrl"],
              "Map identity mismatch: " + ref)
        for key, suffix in (("displayUrl", "/"), ("factsheetUrl", "/factsheet.pdf"),
                            ("briefUrl", "/product-brief.md")):
            check(project[key].endswith("/products/" + slug + suffix),
                  "Canonical public URL drift: " + ref + "/" + key)
        internal_links += check_links(
            html, "https://thearchitect-max.github.io/MyProjects/displays/products/"
                  + slug + "/", hub)

    aliases = data(ROOT / "assets/route-aliases.json")["aliases"]
    check(len(aliases) == 12 and
          len({a["legacySlug"] for a in aliases}) == 12,
          "Historical route alias contract changed")
    for alias in aliases:
        redirect = ROOT / "products" / alias["legacySlug"] / "index.html"
        html = redirect.read_text(encoding="utf-8")
        check("noindex,follow" in html and alias["slug"] in html,
              "Alias route must redirect: " + alias["legacySlug"])
        check(alias["ref"] in by_price, "Unknown alias ID")

    check((ROOT / "PUBLICATION_AUDIT_2026-11-13.md").is_file(),
          "Missing pinned publication audit")
    return {
        "result": "PASS",
        "sourceHead": PIN,
        "assets": EXPECTED_COUNT,
        "factsheets": EXPECTED_COUNT,
        "pdfPages": pdf_pages,
        "productBriefs": EXPECTED_COUNT,
        "individualSellerAsksEUR": EXPECTED_SELLER_TOTAL,
        "priceFieldsPerAsset": len(prices["fields"]),
        "mirroredSHA256Files": len(expected_files),
        "internalLinksValidated": internal_links,
        "redirectAliases": len(aliases),
        "buyerStatus": "date-scoped; not a live release or market certification"
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hub", type=Path, help="Exact pinned MyProjects checkout")
    arguments = parser.parse_args()
    print(json.dumps(validate(arguments.hub), indent=2))
