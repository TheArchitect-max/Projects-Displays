#!/usr/bin/env python3
"""Canonical 123-asset publication builder, retaining the historical command name.

The original HTML templater only supported 119 assets and must not overwrite
the canonical 123-asset publication. Build from a pinned MyProjects checkout.
"""
import argparse
import json
from pathlib import Path
from sync_snapshot import sync

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hub", type=Path, help="Pinned MyProjects checkout")
    parser.add_argument("--write", action="store_true",
                        help="Explicitly rebuild the entire mirror; no partial assets")
    args = parser.parse_args()
    result = sync(args.hub, write=args.write)
    print(json.dumps({"builder": "canonical-public-snapshot", **result}, indent=2))
