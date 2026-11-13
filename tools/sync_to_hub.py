#!/usr/bin/env python3
"""Retired reverse-sync compatibility entrypoint: READ ONLY.

MyProjects is the canonical owner of buyer data and public display content.
Never overwrite or delete that hub from this mirrored repository.
"""
from pathlib import Path
import argparse
import json
from sync_snapshot import sync

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hub_checkout", type=Path)
    args = parser.parse_args()
    result = sync(args.hub_checkout, write=False)
    print(json.dumps({"action": "NO_HUB_WRITE", "direction": "MyProjects -> Projects-Displays",
                      **result}, indent=2))
