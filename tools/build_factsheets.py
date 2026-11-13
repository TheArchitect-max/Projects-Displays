#!/usr/bin/env python3
"""Canonical 123-asset factsheet build/check (no obsolete three-page generator).

The four-page approved PDFs belong to the pinned public MyProjects snapshot.
Use --write to mirror ALL 123 publication records; selective regeneration is
prohibited because a partial update would desynchronise prices, IDs and pages.
"""
import argparse
import json
from pathlib import Path
from sync_snapshot import sync

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hub", type=Path, help="Pinned MyProjects checkout")
    parser.add_argument("--write", action="store_true",
                        help="Explicit full-publication mirror including 123 PDFs")
    args = parser.parse_args()
    result = sync(args.hub, write=args.write)
    print(json.dumps({"factsheets": 123, "pdfPolicy": "four-page-approved-source",
                      **result}, indent=2))
