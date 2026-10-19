#!/usr/bin/env python3
"""Build three-page buyer factsheets with complete prices and source links."""
from pathlib import Path
from html import escape
import argparse,json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader
from pricing_publication import record as price_record,money as price_money,usd

ROOT=Path(__file__).resolve().parents[1]
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--refs',nargs='+');args=parser.parse_args()
 dossiers={p['ref']:p for p in json.loads((ROOT/'assets/buyer-dossiers.json').read_text())['projects']};data=json.loads((ROOT/'assets/buyer-catalogue.json').read_text());cats={c['id']:c for c in data['categories']};pricing=json.loads((ROOT/'assets/pricing-catalogue.json').read_text())
 fonts=Path('/usr/share/fonts/truetype/dejavu');pdfmetrics.registerFont(TTFont('FactSans',str(fonts/'DejaVuSans.ttf')));pdfmetrics.registerFont(TTFont('FactSansBold',str(fonts/'DejaVuSans-Bold.ttf')))
 body=ParagraphStyle('body',fontName='FactSans',fontSize=8.5,leading=12,textColor=colors.HexColor('#1b1916'),spaceAfter=7)
 title=ParagraphStyle('title',parent=body,fontName='FactSansBold',fontSize=21,leading=25,spaceAfter=13)
 heading=ParagraphStyle('heading',parent=body,fontName='FactSansBold',fontSize=11,leading=15,textColor=colors.HexColor('#94703e'),spaceBefore=12,spaceAfter=6)
 small=ParagraphStyle('small',parent=body,fontSize=7.5,leading=10,textColor=colors.HexColor('#5e5a52'))
 def p(text,style=body):return Paragraph(escape(str(text).replace('—','-').replace('–','-').replace('‑','-')).replace('\n','<br/>'),style)
 def link(text,url):return Paragraph('<link href="'+escape(url,quote=True)+'" color="#94703e">'+escape(text)+'</link>',small)
 def lines(items):return [p('• '+s) for s in items]
 def footer(canvas,doc):
  canvas.saveState();canvas.setStrokeColor(colors.HexColor('#94703e'));canvas.line(43,52,A4[0]-43,52);canvas.setFillColor(colors.HexColor('#5e5a52'));canvas.setFont('FactSans',7);canvas.drawString(43,38,'THEARCHITECT_MAX | SOFTWARE IP | BUYER INFORMATION');canvas.drawRightString(A4[0]-43,38,str(doc.page));canvas.restoreState()
 count=0
 for a in data['projects']:
  if args.refs and a['ref'] not in args.refs:continue
  text=a['title'].replace('Spatial-Computing','Spatial-\nComputing') if a['ref']=='TA-IP-107' else a['title']
  story=[p(a['ref']+' / '+a['referenceName']+' / INDEPENDENT IP ASSET',small),p(text,title),p(a['summary']),p('Product overview',heading),p(a['overview']),p('Potential acquirers',heading)]+lines(a['potentialBuyers'])
  story+=[p('Documented functions',heading)]+lines(a['capabilities'])
  story+=[p('Available output types',heading),p(' / '.join(a['outputTypes'])),p(cats[a['categoryId']]['title'],small),PageBreak()]
  story+=[p(a['ref']+' / ACQUISITION SCOPE',small),p('Defined work.\nSeparate written terms.',title)]
  money=Table([[p('SELLER ASKING REFERENCE / AS IS',small),p('CURRENT OFFERED POSITION',small)],[p('EUR '+format(a['askingReferenceEUR'],','),heading),p(a['maturity'],heading)]],colWidths=[250,250]);money.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#f3eee5')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10)]))
  story+=[money,Spacer(1,10),p('Current scope and conditions',heading),p(a['maturityNote']),p(a['availability']),p('Identified edition: '+dossiers[a['ref']]['version'],small)]+lines(a['materialBoundaries'])
  story+=[p('Offered first-party perimeter',heading)]+lines(a['offeredScope'])
  story+=[p('Separately scoped or excluded',heading)]+[p(x,small) for x in a['excludedScope']]
  story+=[p('Buyer information and next step',heading),p('Quote '+a['ref']+' and the project title when discussing your intended use through the verified seller contact channel supplied with this portfolio. Detailed diligence is handled through an agreed review process.',small),p(a['profileUrl'],small),p('The asking reference is an indicative seller choice, not an independent market appraisal. Rights, exact delivery, acceptance, consideration and taxes require separate written terms. Viewing this document grants no software or IP rights. Buyer descriptions indicate potential fit, not existing customers or contracts.',small)]
  q=price_record(a,pricing);f=q['futureReference'];n=f.get('milestoneConditionedEconomicReferenceEUR')
  story+=[PageBreak(),p(a['ref']+' / '+a['referenceName']+' / FINANCIAL REFERENCES',small),p('Prices & sources.',title),p('Price basis: '+q['basisDate']+'. EUR is the reference currency; market value is not established.',small)]
  table=[[p('PRICE / MODEL REFERENCE',small),p('EUR',small),p('USD - indicative',small)]]
  for field in pricing['fields']:table.append([p(field['label']),p(format(q['values'][field['key']],',')),p(usd(q['values'][field['key']],pricing).removeprefix('USD '),small)])
  financial=Table(table,colWidths=[270,115,115],hAlign='LEFT');financial.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#f3eee5')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.35,colors.HexColor('#ded5c4')),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),4)]));story+=[financial]
  story+=[p('Milestone-conditioned reference',heading),p(price_money(n)+'; model change '+price_money(f['sensitivityDeltaEUR'])+'. '+f.get('targetMilestone','Next maturity gate must be evidenced.') if n is not None else 'Not established. '+f.get('reason','No separately supported next-stage reference is available.'),small),p('This is a conditional maturity sensitivity, not a current asking price, forecast or established market value.',small),p('Cost basis',heading),p(q['costBasisNote'],small),p(q['assessment']['costEvidenceLabel']+'. Budget coverage concerns the stated priced scope; independent quotation and market value are not established.',small),p('Source references',heading)]
  for id_ in dict.fromkeys(q['sourceIds']+['ECB-FX']):
   source=next(s for s in pricing['sources'] if s['id']==id_);story+=[link(source['publisher']+' - '+source['title'],source['url'])]
  fx=pricing['displayCurrency'];story+=[p('External sources inform the method, contractor-rate context and currency only. Project-specific prices and model factors remain seller assumptions. The marketability, monetisation and strategic references share a cost anchor; their weighted blend is not an independent appraisal.',small),p('USD display: EUR 1 = USD '+str(fx['rate'])+'; ECB '+fx['date']+'. EUR is authoritative.',small),link('Complete assumptions, scoped budgets and sources: '+a['profileUrl']+'#pricing',a['profileUrl']+'#pricing')]
  output=ROOT/'products'/a['slug']/'factsheet.pdf';SimpleDocTemplate(str(output),pagesize=A4,rightMargin=43,leftMargin=43,topMargin=43,bottomMargin=65,title=a['title']+' - '+a['ref'],author='THEARCHITECT_MAX',pageCompression=1).build(story,onFirstPage=footer,onLaterPages=footer)
  assert len(PdfReader(output).pages)==3,a['ref'];count+=1
 print(json.dumps(dict(factsheets=count,pages=count*3,allThreePages=True,pricesAndSourcesIncluded=True)))

if __name__=='__main__':main()
