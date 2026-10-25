"""Present the approved public prices and their contextual sources."""
from pathlib import Path
from html import escape
import json,re,math
from decimal import Decimal,ROUND_HALF_UP

HUB='https://thearchitect-max.github.io/MyProjects/'
def money(n):return 'EUR '+format(n,',')
def label(key):return re.sub(r'([a-z])([A-Z])',r'\1 \2',key).removesuffix('EUR').strip().capitalize()
def record(asset,data):return next(p for p in data['projects'] if p['ref']==asset['ref'])
def usd_number(n,data):return int((Decimal(str(n))*Decimal(str(data['displayCurrency']['rate']))).quantize(Decimal(1),rounding=ROUND_HALF_UP))
def usd(n,data):return 'USD '+format(usd_number(n,data),',')
def pair(n,data):return '<strong>'+money(n)+'</strong><small class="price-usd" data-currency="USD">≈ '+usd(n,data)+'</small>'
def grid(values,data):
 return '<dl class="restored-price-grid">'+''.join('<div data-price-field="'+f['key']+'"><dt>'+escape(f['label'])+'</dt><dd><strong>'+money(values[f['key']])+'</strong><small class="price-usd">≈ '+usd(values[f['key']],data)+'</small></dd><small>'+escape(f['description'])+'</small></div>' for f in data['fields'])+'</dl>'
def sources(ids,data):
 rows=[]
 for id_ in ids:
  s=next(s for s in data['sources'] if s['id']==id_)
  rows.append('<li><a href="'+escape(s['url'],quote=True)+'" target="_blank" rel="noopener">'+escape(s['publisher']+' · '+s['title'])+' ↗</a><small>'+escape(s['application'])+'</small></li>')
 return '<ul class="price-source-links">'+''.join(rows)+'</ul>'
def future_html(p,data):
 f=p['futureReference'];n=f.get('milestoneConditionedEconomicReferenceEUR')
 content='<p class="conditional-value">'+money(n)+' <small>≈ '+usd(n,data)+'</small></p><p>'+escape(f.get('targetMilestone','Next maturity gate must be evidenced.'))+'</p><p>Model change: '+money(f['sensitivityDeltaEUR'])+'. '+escape(f.get('acceptanceRule','Conditional model sensitivity only.'))+'</p>' if n is not None else '<p>Not established. '+escape(f.get('reason','No separately supported next-stage reference is available.'))+'</p>'
 return '<div class="price-cost-basis"><h3>Milestone-conditioned economic reference</h3>'+content+'<p>A conditional maturity sensitivity, not a current asking price, forecast or established market value.</p></div>'
def numeric_rows(value,prefix=''):
 rows=[]
 for k,v in value.items():
  if isinstance(v,dict):rows+=numeric_rows(v,prefix+label(k)+' / ')
  elif isinstance(v,(int,float)) and not isinstance(v,bool):rows.append((prefix+label(k),money(v) if k.endswith('EUR') else str(v)))
 return rows
def budgets_html(p):
 rows=[]
 for b in p['costBudgets']:
  rows.append('<article class="price-budget-item"><h3>'+escape(b['kind'])+'</h3><p>'+escape(b.get('scope','Retained scoped reproduction budget.'))+'</p>'+('<ul>'+''.join('<li>'+escape(w['scope'])+(' — '+str(w['lowEffortHours'])+' assumed hours' if 'lowEffortHours' in w else '')+'</li>' for w in b.get('workPackages',[]))+'</ul>' if b.get('workPackages') else '')+'<dl class="price-budget-values">'+''.join('<div><dt>'+escape(k)+'</dt><dd>'+escape(v)+'</dd></div>' for k,v in numeric_rows(b))+'</dl><p class="small">'+escape(b.get('boundary','Seller assumptions for scoped reproduction, not actual spending.'))+'</p></article>')
 if p.get('costSensitivity'):rows.append('<article class="price-budget-item"><h3>Cost sensitivity</h3><dl class="price-budget-values">'+''.join('<div><dt>'+escape(k)+'</dt><dd>'+escape(v)+'</dd></div>' for k,v in numeric_rows(p['costSensitivity']))+'</dl><p>'+escape(p['costSensitivity']['sensitivityBasis'])+'</p></article>')
 return '<details class="price-budget"><summary>Cost assumptions and scoped work budgets</summary><p class="small">Scope budgets can overlap. Use the stated cost anchor and calculation method; do not add overlapping budgets.</p>'+''.join(rows)+'</details>' if rows else ''
def assessment_html(p):
 a=p['assessment']
 return '<div class="price-cost-basis" data-financial-assessment="'+p['ref']+'"><h3>'+escape(a['costEvidenceLabel'])+'</h3><p>'+escape(a['costEvidenceNote'])+'</p><p class="small">Assessment: '+escape(a['assessedOn'])+'. '+escape(a['financialScopeRule'])+'</p></div>'
def buyer_value_html(asset):
 return '<details class="price-budget" id="buyer-value-case" data-buyer-value-ref="'+asset['ref']+'"><summary>Buyer-specific economic value &amp; evaluation</summary><p>'+escape(asset['ref']+' / '+asset['referenceName']+' / '+asset['title'])+'</p><p>Assess a measurable benefit for the intended application against a credible build, licence or operating alternative. Support time advantage, incremental cash flow or avoided costs, counting each benefit once and including remaining qualification, integration, rights and operating requirements.</p><p>The published references describe their stated scope and assumptions. A separately evidenced buyer-specific case may support different consideration; no strategic premium, independently established market value or guaranteed transaction ceiling/floor is asserted.</p><a href="'+HUB+'valuation.html#buyer-value">Buyer-value framework, scenario requirements and source context ↗</a></details>'
def buyer_value_brief(asset):
 return '## Buyer-specific economic value and evaluation\n\n'+asset['ref']+' / '+asset['referenceName']+' / '+asset['title']+'\n\nAssess the intended use against a credible build, licence or operating alternative. Support any time advantage, incremental cash flow or avoided costs, count each benefit once, and include remaining qualification, integration, rights and operating requirements. The published references describe their stated scope and assumptions; a separately evidenced buyer-specific case may support different consideration. No strategic premium, independently established market value or guaranteed transaction ceiling/floor is asserted.\n\nBuyer-value framework, scenario requirements and source context: '+HUB+'valuation.html#buyer-value\n\n'
def full_html(asset,data):
 p=record(asset,data);fx=data['displayCurrency']
 return '<p>Price basis: '+escape(p['basisDate'])+'. EUR is the reference currency. Market value is not established.</p>'+grid(p['values'],data)+assessment_html(p)+buyer_value_html(asset)+'<a class="calculation-link" href="'+asset['profileUrl']+'#calculation">View this asset’s calculation and validation ↗</a><p class="small">Four model outputs, eight USD conversions and portfolio totals are checked against the disclosed inputs. <a href="'+HUB+'proof.html?v=calc5">Run the complete calculation checks ↗</a></p>'+future_html(p,data)+'<div class="price-cost-basis"><h3>Cost basis</h3><p>'+escape(p['costBasisNote'])+'</p></div>'+budgets_html(p)+'<h3>Sources and application</h3><p>Project prices are seller choices and cost-model outputs. External publishers provide method and rate context, not individual asset valuations.</p>'+sources(p['sourceIds'],data)+'<p class="small">Indicative USD conversion: EUR 1 = USD '+str(fx['rate'])+'; ECB '+escape(fx['date'])+'. EUR is authoritative.</p><a class="button secondary" href="'+HUB+'valuation.html#methodology">Full price method & source register ↗</a>'
def brief_prices(asset,data):
 p=record(asset,data);text='## Complete prices and economic references\n\nBasis: '+p['basisDate']+'. All amounts in EUR. Market value is not established.\n\n'
 text+='| Reference | EUR | USD - indicative |\n| --- | ---: | ---: |\n'+''.join('| '+f['label']+' | '+format(p['values'][f['key']],',')+' | '+format(usd_number(p['values'][f['key']],data),',')+' |\n' for f in data['fields'])+'\n'
 text+='USD = EUR × '+str(data['displayCurrency']['rate'])+', rounded half-up to whole USD. ECB date: '+data['displayCurrency']['date']+'. EUR is authoritative.\n\n'
 text+='\n'.join('- '+f['label']+': '+f['description'] for f in data['fields'])+'\n\n'
 f=p['futureReference'];n=f.get('milestoneConditionedEconomicReferenceEUR')
 text+='Milestone-conditioned reference: '+(money(n)+'; model change '+money(f['sensitivityDeltaEUR'])+'. '+f.get('targetMilestone','') if n is not None else 'Not established. '+f.get('reason',''))+'\n\nThis is a conditional model sensitivity, not a current asking price, forecast or market value.\n\n'
 text+='### Cost basis\n\n'+p['costBasisNote']+'\n\n'
 a=p['assessment'];text+='### Financial assessment\n\n'+a['costEvidenceLabel']+'. Assessed '+a['assessedOn']+'.\n\n'+a['costEvidenceNote']+'\n\n'+a['financialScopeRule']+'\n\n'
 for b in p['costBudgets']:
  text+='#### '+b['kind']+'\n\n'+b.get('scope','Retained scoped reproduction budget.')+'\n\n'+''.join('- '+w['scope']+(' — '+str(w['lowEffortHours'])+' assumed hours' if 'lowEffortHours' in w else '')+'\n' for w in b.get('workPackages',[]))+'\n'+''.join('- '+k+': '+v+'\n' for k,v in numeric_rows(b))+'\n'
  text+=b.get('boundary','Seller assumptions for scoped reproduction, not actual spending.')+'\n\n'
 if p.get('costSensitivity'):text+='#### Cost sensitivity\n\n'+''.join('- '+k+': '+v+'\n' for k,v in numeric_rows(p['costSensitivity']))+'\n'+p['costSensitivity']['sensitivityBasis']+'\n\n'
 text+='Scope budgets can overlap. Use the stated cost anchor and calculation method; do not add overlapping budgets.\n\n### Sources\n\nProject-specific prices are seller choices and model outputs; external publishers inform method, rates and currency only.\n\n'
 for id_ in p['sourceIds']:
  s=next(s for s in data['sources'] if s['id']==id_);text+='- ['+s['publisher']+' - '+s['title']+']('+s['url']+'): '+s['application']+'\n'
 fx=data['displayCurrency'];text+='\nIndicative USD conversion: EUR 1 = USD '+str(fx['rate'])+'; ECB '+fx['date']+'. EUR remains authoritative.\n\nFull pricing method and source register: '+HUB+'valuation.html#methodology\n\n'
 text+='Calculation inputs: '+json.dumps(p['calculationInputs'],ensure_ascii=False)+'.\n\nCalculation validation: '+HUB+'proof.html?v=calc5\n\nAsset-specific formulas: '+asset['profileUrl']+'#calculation\n\n'
 return text+buyer_value_brief(asset)
