"""Render public product, qualification and handover information for buyers."""
from html import escape

HUB='https://thearchitect-max.github.io/MyProjects/'
def evaluation_sources_html(data):
 text='<section><h2>Sources behind the evaluation</h2><p>'+escape(data['scope'])+'</p><a class="button" href="'+HUB+'sources.html">Complete source register and per-asset mapping ↗</a></section>'
 for category in data['categories']:
  text+='<section id="'+category['id']+'"><h2>'+escape(category['title'])+'</h2><p>'+escape(category['description'])+'</p>'
  for source in data['externalSources']:
   if source['categoryId']!=category['id']:continue
   text+='<article class="evaluation-source" id="source-'+source['id']+'" data-evaluation-source="'+source['id']+'"><h3><a href="'+escape(source['url'],quote=True)+'" target="_blank" rel="noopener">'+escape(source['publisher']+' · '+source['title'])+' ↗</a></h3><p class="source-address"><a href="'+escape(source['url'],quote=True)+'">'+escape(source['url'])+'</a></p><dl class="source-meaning"><div><dt>Source finding</dt><dd>'+escape(source['finding'])+'</dd></div><div><dt>Application in the evaluation</dt><dd>'+escape(source['application'])+'</dd></div><div><dt>Limit of use</dt><dd>'+escape(source['useLimit'])+'</dd></div></dl><p class="small">Reference basis '+source['referenceBasisDate']+' · Source checked '+source['checkedOn']+' · '+escape(source['access'])+'.</p></article>'
  text+='</section>'
 return text+'<section><h2>Project-specific evidence and inputs</h2><p>Product documentation, version-specific qualification, seller rights/component records and disclosed engineering inputs support the per-project assessment. External sources provide contextual methods and rates.</p><div class="buyer-info-actions"><a class="button" href="'+HUB+'sources.html#assessment-records">Assessment records ↗</a><a class="button secondary" href="'+HUB+'connections.html">Connections ↗</a><a class="button secondary" href="assets/evaluation-sources.json" download>Download source register ↓</a></div></section>'
def ul(items):return '<ul>'+''.join('<li>'+escape(s)+'</li>' for s in items)+'</ul>'
def criteria(p):
 return '<div class="price-table-wrap"><table class="price-table buyer-criteria"><thead><tr><th>Acquisition criterion</th><th>Profile</th><th>Meaning for your review</th></tr></thead><tbody>'+''.join('<tr><th>'+escape(c['label'])+'</th><td>'+escape(c['grade'])+'</td><td>'+escape(c['criterion'])+'</td></tr>' for c in p['assessmentCriteria'])+'</tbody></table></div>'
def dossier_html(a,p,applications):
 text='<dl class="status-grid"><div><dt>Identified product edition</dt><dd>'+escape(p['version'])+'</dd></div><div><dt>Handover position</dt><dd>'+escape(p['transferPosition'])+'</dd></div></dl><p>'+escape(p['productPosition'])+'</p>'
 if p['developmentEdition']:text+='<p><strong>Separately scoped development:</strong> '+escape(p['developmentEdition'])+'</p>'
 text+='<h3>Priced first-party scope</h3><p>'+escape(p['offeredEdition'])+'</p>'
 for x in p['productDetails']:text+='<article class="boundary-box"><h3>'+escape(x['title'])+'</h3><p>'+escape(x['text'])+'</p>'+ul(x['items'])+'</article>'
 text+='<h3>Acquisition evidence profile</h3>'+criteria(p)+'<p class="small">Seller-side documentary grades apply to the identified edition. <a href="'+HUB+'assurance.html#criteria">Read grade definitions ↗</a></p><h3>Conditions before handover</h3>'+ul(p['sellerConditions'])+'<h3>Qualification objectives</h3>'+ul(p['qualificationObjectives']+p['buyerConditions'])+'<h3>Rights and components</h3><p>'+escape(p['rightsPosition'])+'</p>'
 labels={'dependencyManifestIdentified':'Dependency declaration','dependencyLockIdentified':'Dependency lock record','componentInventoryIdentified':'Component inventory artifact','licenceNoticesIdentified':'Licence notices','thirdPartyDisclosureIdentified':'Third-party disclosure','securityDocumentationIdentified':'Security documentation'}
 text+='<dl class="buyer-component-grid">'+''.join('<div><dt>'+label+'</dt><dd>'+('Identified in the reviewed records' if p['componentEvidence'][key] else 'Not established in the reviewed records')+'</dd></div>' for key,label in labels.items())+'</dl><p class="small">'+escape(p['componentEvidence']['interpretation'])+'</p>'
 rows=[c for c in applications['connections'] if any(m['ref']==a['ref'] for m in c['members'])]
 if rows:text+='<h3>Potential application context</h3><ul>'+''.join('<li><a href="'+HUB+'connections.html#'+escape(c['slug'],quote=True)+'">'+escape(c['title'])+'</a> — '+escape(next(m['role'] for m in c['members'] if m['ref']==a['ref']))+'</li>' for c in rows)+'</ul><p class="small">Proposed applications require separately agreed interfaces, integration and joint qualification. They are not additional assets or delivered integrated products.</p>'
 return text+'<p><a class="text-link" href="'+HUB+'transfer.html">Review the rights and delivery guide ↗</a></p>'
def dossier_brief(a,p,applications):
 text='## Product edition and acquisition dossier\n\nIdentified product edition: '+p['version']+'\n\nHandover position: '+p['transferPosition']+'\n\n'+p['productPosition']+'\n\n'
 if p['developmentEdition']:text+='Separately scoped development: '+p['developmentEdition']+'\n\n'
 text+='### Priced first-party scope\n\n'+p['offeredEdition']+'\n\n'
 for x in p['productDetails']:text+='### '+x['title']+'\n\n'+x['text']+'\n\n'+'\n'.join('- '+s for s in x['items'])+'\n\n'
 text+='### Acquisition evidence profile\n\n| Criterion | Profile | Meaning for your review |\n| --- | --- | --- |\n'+''.join('| '+c['label']+' | '+c['grade']+' | '+c['criterion'].replace('|','/')+' |\n' for c in p['assessmentCriteria'])+'\n'
 for heading,items in [('Conditions before handover',p['sellerConditions']),('Qualification objectives',p['qualificationObjectives']+p['buyerConditions'])]:text+='### '+heading+'\n\n'+'\n'.join('- '+s for s in items)+'\n\n'
 text+='### Rights and components\n\n'+p['rightsPosition']+'\n\n'+p['componentEvidence']['interpretation']+'\n\n'
 for key,label in [('dependencyManifestIdentified','Dependency declaration'),('dependencyLockIdentified','Dependency lock record'),('componentInventoryIdentified','Component inventory artifact'),('licenceNoticesIdentified','Licence notices'),('thirdPartyDisclosureIdentified','Third-party disclosure'),('securityDocumentationIdentified','Security documentation')]:text+='- '+label+': '+('identified' if p['componentEvidence'][key] else 'not established in reviewed records')+'\n'
 rows=[c for c in applications['connections'] if any(m['ref']==a['ref'] for m in c['members'])]
 if rows:text+='\n### Potential applications\n\n'+''.join('- ['+c['title']+']('+HUB+'connections.html#'+c['slug']+'): '+next(m['role'] for m in c['members'] if m['ref']==a['ref'])+'\n' for c in rows)+'\nProposed applications require separate interfaces, integration and joint qualification; they are not delivered integrated products.\n'
 return text+'\nGrade definitions: '+HUB+'assurance.html#criteria\n\nRights and delivery guide: '+HUB+'transfer.html\n\n'
