#!/usr/bin/env python3
"""Validate all exhibition links and their canonical hub correspondence offline."""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, unquote
import argparse, csv, hashlib, json

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.returns, self.profiles = [], set(), [], []
        self.body = {}
        self.feed(text)
    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if attrs.get('id'): self.ids.add(attrs['id'])
        if tag == 'body': self.body = attrs
        if 'data-hub-return' in attrs: self.returns.append(attrs.get('href'))
        if 'data-project-profile' in attrs: self.profiles.append(attrs.get('href'))
        for key in ('href', 'src', 'action'):
            if attrs.get(key): self.links.append(attrs[key])

def validate(hub):
    source = Path(__file__).resolve().parents[1]
    mapping = json.loads((source / 'project-map.json').read_text())
    identities = json.loads((hub / 'assets/project-identities.json').read_text())
    sites = json.loads((hub / 'assets/public-sites.json').read_text())
    att = json.loads((hub / 'assets/public-attestation.json').read_text())
    values = json.loads((hub / 'assets/valuation-register.json').read_text())
    # The hub renders its profile sections in JS. Use anchors extracted by its
    # actual render functions rather than treating an empty HTML shell as content.
    report = hub / 'docs/DEVELOPMENT_VALUE_RENDERING_VALIDATION_2026-10-16.json'
    if not report.is_file(): report = hub / 'docs/MULTISOURCE_RENDERING_VALIDATION_2026-10-16.json'
    rendering = json.loads(report.read_text())
    assert rendering['result'] == 'PASS' and rendering['individualFinancialReviews'] == 105
    rendered_anchors = rendering['renderedPageAnchors']
    by_ref = {p['ref']:p for p in identities['projects']}
    price_by_ref = {p['ref']:p for p in values['updates']}
    site_by_ref = {p['ref']:p for p in sites['sites']}
    catalogue = {p['Asset reference']:p for p in csv.DictReader((source / 'catalogue.csv').open(encoding='utf-8-sig'))}
    assert mapping['projectCount'] == len(mapping['projects']) == len(by_ref) == len(site_by_ref) == sites['siteCount'] == 105
    assert len({p['slug'] for p in mapping['projects']}) == len({p['displaySlug'] for p in mapping['projects']}) == 105
    assert {'MyProjects','Projects-Displays'} <= set(identities['scope']['excludedRepositories'])
    pages = {p.relative_to(source).as_posix():Page(p.read_text()) for p in source.rglob('*.html')}
    destinations = Counter(urlparse(urljoin(mapping['displayBaseUrl'], link)).path.removesuffix('index.html').rstrip('/')
                           for link in pages['index.html'].links if 'products/' in link)
    assert len(destinations) == 105 and set(destinations.values()) == {1}, 'Duplicate display collection destinations'
    local_link_count = 0
    for rel, page in pages.items():
        for link in page.links:
            url = urlparse(urljoin(mapping['displayBaseUrl'] + rel, link))
            if url.netloc != 'thearchitect-max.github.io': continue
            assert url.path.startswith('/MyProjects/'), (rel, link, 'unexpected internal root')
            target = hub / unquote(url.path.removeprefix('/MyProjects/'))
            if target.is_dir() or url.path.endswith('/'): target = target / 'index.html'
            assert target.is_file(), (rel, link, 'missing target')
            local_link_count += 1
            if url.fragment:
                target_page = Page(target.read_text())
                anchors = target_page.ids | set(rendered_anchors.get(target.relative_to(hub).as_posix(), []))
                assert unquote(url.fragment) in anchors, (rel, link, 'missing fragment')
    for p in mapping['projects']:
        identity = by_ref[p['ref']]
        assert p['slug'] == identity['slug'] and p['title'] == identity['title']
        assert p['sellerAskEUR'] == price_by_ref[p['ref']]['sellerAskEUR'] == int(catalogue[p['ref']]['Seller ask EUR'])
        assert p['recreationCostEUR'] == price_by_ref[p['ref']]['replacementCostEUR'] == int(catalogue[p['ref']]['Estimated recreation cost EUR'])
        assert site_by_ref[p['ref']]['url'] == p['url']
        assert p['profileUrl'] == mapping['hubUrl'] + 'projects/' + p['slug'] + '/'
        page = pages[p['productPage']]
        assert page.body.get('data-project-ref') == p['ref']
        assert page.body.get('data-project-slug') == p['slug']
        assert len(page.returns) >= 2 and set(page.returns) == {mapping['hubUrl']}
        assert page.profiles == [p['profileUrl']]
        folder = source / p['productPage']
        assert folder.with_name('factsheet.pdf').read_bytes().startswith(b'%PDF-')
        assert folder.with_name('product-brief.md').is_file()
    mirrored = 0
    for folder in ('assets','products'):
        for p in (source / folder).rglob('*'):
            if p.is_file():
                target = hub / 'displays' / p.relative_to(source)
                assert target.is_file() and p.read_bytes() == target.read_bytes(), ('mirror mismatch',p)
                mirrored += 1
    for name in ('public-sites.json','project-identities.json','repository-inventory.json','portfolio-audit-certificate.json'):
        data = (hub / 'assets' / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == att['files'][name]['sha256'], name
        assert len(data) == att['files'][name]['bytes'], name
    for p in source.rglob('*.html'):
        assert 'github.com/TheArchitect-max/' not in p.read_text(), ('underlying repository link in exhibit', p)
    assert not list(source.glob('.github/workflows/*'))
    return {'projectsMatched':105,'pricesMatched':105,'productDisplays':105,
            'factsheets':105,'editableBriefs':105,'projectProfilesLinked':105,
            'hubReturnButtonsChecked':210,'uniqueCollectionSiteLinks':105,'duplicateCollectionSiteLinks':0,'exhibitPagesChecked':len(pages),
            'internalLinksAndFragmentsChecked':local_link_count,'mirroredFilesChecked':mirrored,
            'directoryDigestsPassed':True,'missingTargets':0,'workflowFilesAdded':0}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('hub_checkout',type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(args.hub_checkout.resolve()),indent=2))
