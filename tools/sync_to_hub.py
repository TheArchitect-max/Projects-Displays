#!/usr/bin/env python3
"""Copy the maintained exhibition into an existing MyProjects checkout."""
from pathlib import Path
import argparse, hashlib, json, shutil

STATIC_FILES = ('index.html', 'acquisition.html', 'methodology.html', 'sources.html',
                '404.html', 'robots.txt', 'sitemap.xml', 'catalogue.csv',
                'source-register.csv', 'project-map.json', 'PRESENTATION_NOTICE.txt', '.nojekyll')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('hub_checkout', type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    hub = args.hub_checkout.resolve()
    identity_file = hub / 'assets/project-identities.json'
    if not identity_file.is_file():
        parser.error('Expected an existing MyProjects checkout with its canonical identity register')
    identities = json.loads(identity_file.read_text())['projects']
    mapping = json.loads((source / 'project-map.json').read_text())
    by_ref = {p['ref']: p for p in identities}
    if len(mapping['projects']) != len(identities) or len({p['ref'] for p in mapping['projects']}) != len(identities):
        parser.error('Display count or unique project references do not match the hub')
    for p in mapping['projects']:
        if p['ref'] not in by_ref or p['slug'] != by_ref[p['ref']]['slug'] or p['title'] != by_ref[p['ref']]['title']:
            parser.error('Canonical project identity mismatch: ' + p['ref'])
    # Copy the content before changing the directory record. No remote publication is performed.
    destination = hub / 'displays'
    destination.mkdir(parents=True, exist_ok=True)
    for name in STATIC_FILES:
        shutil.copy2(source / name, destination / name)
    for name in ('assets', 'products'):
        shutil.copytree(source / name, destination / name, dirs_exist_ok=True)
    directory_file = hub / 'assets/public-sites.json'
    directory = json.loads(directory_file.read_text())
    old_sites = {p['ref']: p for p in directory.get('sites', [])}
    directory['siteCount'] = len(mapping['projects'])
    directory['sites'] = [{**old_sites.get(p['ref'], {}),
                           **{k:p[k] for k in ('ref','title','slug','url','profileUrl','hubUrl','displaySlug')},
                           'kind':'digital-display','status':'live',
                           'provider':'Integrated static project display',
                           'sourceRepository':'Projects-Displays','publicationRepository':'MyProjects'}
                          for p in mapping['projects']]
    directory_file.write_text(json.dumps(directory, ensure_ascii=False, indent=2) + '\n')
    attestation_file = hub / 'assets/public-attestation.json'
    attestation = json.loads(attestation_file.read_text())
    data = directory_file.read_bytes()
    attestation['publicDisplayCount'] = directory['siteCount']
    attestation['files']['public-sites.json'] = {'algorithm':'SHA-256','sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
    attestation_file.write_text(json.dumps(attestation, ensure_ascii=False, indent=2) + '\n')
    print(f"Synchronized {len(mapping['projects'])} displays into {destination}")

if __name__ == '__main__':
    main()
