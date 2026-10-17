#!/usr/bin/env python3
"""Validate buyer information, visible prices, downloads and the mirrored display."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin,urlparse,unquote
from collections import Counter
import argparse,csv,json,re
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self,text):super().__init__();self.links=[];self.body={};self.feed(text)
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='body':self.body=a
  if t=='a' and a.get('href'):self.links.append(a['href'])
def validate(hub):
 d=json.loads((ROOT/'assets/buyer-catalogue.json').read_text());assert d==json.loads((hub/'assets/buyer-catalogue.json').read_text());mapping=json.loads((ROOT/'project-map.json').read_text());assert len(mapping['projects'])==108
 assert set(mapping)=={'schema','projectCount','projects'}
 allowed={'ref','title','slug','displaySlug','productPage','url','profileUrl','factsheetUrl','briefUrl'}
 for m in mapping['projects']:assert set(m)==allowed
 assert not (ROOT/'source-register.csv').exists() and not (ROOT/'docs').exists();assert not list(ROOT.glob('.github/workflows/*'))
 catalogue=list(csv.DictReader((ROOT/'catalogue.csv').open(encoding='utf-8-sig')));assert len(catalogue)==108
 index=(ROOT/'index.html').read_text();destinations=Counter(x for x in Page(index).links if x.startswith('products/'));assert len(destinations)==108 and set(destinations.values())=={1}
 count=0
 for a in d['projects']:
  folder=ROOT/'products'/a['slug'];text=(folder/'index.html').read_text();p=Page(text);assert p.body['data-project-ref']==a['ref'];assert 'Potential acquirers' in text
  money='EUR '+format(a['askingReferenceEUR'],',');assert money in re.search(r'<div class="plaque-price">.*?</div>',text)[0]
  for b in a['potentialBuyers']:assert b.replace('&','&amp;') in text
  brief=(folder/'product-brief.md').read_text();assert '## Potential acquirers' in brief and money in brief
  pdf=PdfReader(folder/'factsheet.pdf');assert len(pdf.pages)==2;pdftext='\n'.join(x.extract_text() for x in pdf.pages);assert 'Potential acquirers' in pdftext and a['ref'] in pdftext
  assert not re.search(r'\b[a-f0-9]{40}\b',text+brief+pdftext);count+=1
 mirrored=0
 for directory in ['assets','products']:
  for p in (ROOT/directory).rglob('*'):
   if p.is_file():assert p.read_bytes()==(hub/'displays'/p.relative_to(ROOT)).read_bytes();mirrored+=1
 for p in ROOT.glob('*.html'):
  for link in Page(p.read_text()).links:
   url=urlparse(urljoin('https://thearchitect-max.github.io/MyProjects/displays/'+p.name,link))
   if url.netloc!='thearchitect-max.github.io':continue
   target=hub/unquote(url.path.removeprefix('/MyProjects/'));target=target/'index.html' if url.path.endswith('/') else target;assert target.is_file(),(p,link)
 return dict(result='PASS',buyerDisplays=count,factsheets=count,pdfPages=count*2,productBriefs=count,uniqueCollectionEntries=108,duplicateCollectionEntries=0,currentAskingPlaques=108,mirroredFiles=mirrored)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('hub',type=Path);a=p.parse_args();print(json.dumps(validate(a.hub.resolve()),indent=2))
