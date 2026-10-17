#!/usr/bin/env python3
"""Synchronise the approved public exhibition into the existing static hub."""
from pathlib import Path
import argparse,json,shutil

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('hub_checkout',type=Path);args=parser.parse_args()
 source=Path(__file__).resolve().parents[1];hub=args.hub_checkout.resolve();data=json.loads((source/'assets/buyer-catalogue.json').read_text())
 assert data==json.loads((hub/'assets/buyer-catalogue.json').read_text()),'Approved public data differs'
 assert len(data['projects'])==108
 destination=hub/'displays'
 if destination.exists():shutil.rmtree(destination)
 destination.mkdir()
 for name in ['index.html','acquisition.html','methodology.html','sources.html','404.html','robots.txt','sitemap.xml','catalogue.csv','project-map.json','PRESENTATION_NOTICE.txt','.nojekyll']:
  if (source/name).exists():shutil.copy2(source/name,destination/name)
 for name in ['assets','products']:shutil.copytree(source/name,destination/name)
 print('Synchronized 108 approved buyer presentations and their public information files.')

if __name__=='__main__':main()
