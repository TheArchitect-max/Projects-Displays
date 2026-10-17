#!/usr/bin/env python3
"""Build buyer-only two-page factsheets from the approved public catalogue."""
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

ROOT=Path(__file__).resolve().parents[1]
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--refs',nargs='+');args=parser.parse_args()
 data=json.loads((ROOT/'assets/buyer-catalogue.json').read_text());cats={c['id']:c for c in data['categories']}
 fonts=Path('/usr/share/fonts/truetype/dejavu');pdfmetrics.registerFont(TTFont('FactSans',str(fonts/'DejaVuSans.ttf')));pdfmetrics.registerFont(TTFont('FactSansBold',str(fonts/'DejaVuSans-Bold.ttf')))
 body=ParagraphStyle('body',fontName='FactSans',fontSize=8.5,leading=12,textColor=colors.HexColor('#1b1916'),spaceAfter=7)
 title=ParagraphStyle('title',parent=body,fontName='FactSansBold',fontSize=21,leading=25,spaceAfter=13)
 heading=ParagraphStyle('heading',parent=body,fontName='FactSansBold',fontSize=11,leading=15,textColor=colors.HexColor('#94703e'),spaceBefore=12,spaceAfter=6)
 small=ParagraphStyle('small',parent=body,fontSize=7.5,leading=10,textColor=colors.HexColor('#5e5a52'))
 def p(text,style=body):return Paragraph(escape(str(text).replace('—','-').replace('–','-').replace('‑','-')).replace('\n','<br/>'),style)
 def lines(items):return [p('• '+s) for s in items]
 def footer(canvas,doc):
  canvas.saveState();canvas.setStrokeColor(colors.HexColor('#94703e'));canvas.line(43,52,A4[0]-43,52);canvas.setFillColor(colors.HexColor('#5e5a52'));canvas.setFont('FactSans',7);canvas.drawString(43,38,'THEARCHITECT_MAX | SOFTWARE IP | BUYER INFORMATION');canvas.drawRightString(A4[0]-43,38,str(doc.page));canvas.restoreState()
 count=0
 for a in data['projects']:
  if args.refs and a['ref'] not in args.refs:continue
  text=a['title'].replace('Spatial-Computing','Spatial-\nComputing') if a['ref']=='TA-IP-108' else a['title']
  story=[p(a['ref']+' / '+a['referenceName']+' / INDEPENDENT IP ASSET',small),p(text,title),p(a['summary']),p('Product overview',heading),p(a['overview']),p('Potential acquirers',heading)]+lines(a['potentialBuyers'])
  story+=[p('Documented functions',heading)]+lines(a['capabilities'])
  story+=[p('Available output types',heading),p(' / '.join(a['outputTypes'])),p(cats[a['categoryId']]['title'],small),PageBreak()]
  story+=[p(a['ref']+' / ACQUISITION SCOPE',small),p('Defined work.\nSeparate written terms.',title)]
  money=Table([[p('SELLER ASKING REFERENCE / AS IS',small),p('CURRENT OFFERED POSITION',small)],[p('EUR '+format(a['askingReferenceEUR'],','),heading),p(a['maturity'],heading)]],colWidths=[250,250]);money.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#f3eee5')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10)]))
  story+=[money,Spacer(1,10),p('Current scope and conditions',heading),p(a['maturityNote']),p(a['availability'])]+lines(a['materialBoundaries'])
  story+=[p('Offered first-party perimeter',heading)]+lines(a['offeredScope'])
  story+=[p('Separately scoped or excluded',heading)]+[p(x,small) for x in a['excludedScope']]
  story+=[p('Buyer information and next step',heading),p('Quote '+a['ref']+' and the project title when discussing your intended use through the verified seller contact channel supplied with this portfolio. Detailed diligence is handled through an agreed review process.',small),p(a['profileUrl'],small),p('The asking reference is an indicative seller choice, not an independent market appraisal. Rights, exact delivery, acceptance, consideration and taxes require separate written terms. Viewing this document grants no software or IP rights. Buyer descriptions indicate potential fit, not existing customers or contracts.',small)]
  output=ROOT/'products'/a['slug']/'factsheet.pdf';SimpleDocTemplate(str(output),pagesize=A4,rightMargin=43,leftMargin=43,topMargin=43,bottomMargin=65,title=a['title']+' - '+a['ref'],author='THEARCHITECT_MAX',pageCompression=1).build(story,onFirstPage=footer,onLaterPages=footer)
  assert len(PdfReader(output).pages)==2,a['ref'];count+=1
 print(json.dumps(dict(factsheets=count,pages=count*2,allTwoPages=True,buyerInformationOnly=True)))

if __name__=='__main__':main()
