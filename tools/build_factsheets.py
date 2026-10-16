#!/usr/bin/env python3
"""Build the two-page downloadable factsheets from the current editable briefs."""
from pathlib import Path
from html import escape
import argparse, csv, json, re
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
GOLD=colors.HexColor('#94703e')
INK=colors.HexColor('#1b1916')
GREY=colors.HexColor('#5e5a52')

def plain(value):
    return str(value).replace('—','-').replace('–','-').replace('\u2011','-').replace('\u2212','-').replace('↗','').replace('↓','')

def sections(text):
    parts=re.split(r'^## (.+)$',text,flags=re.M)
    return {parts[i].strip():parts[i+1].strip() for i in range(1,len(parts),2)}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refs',nargs='+',help='Regenerate only the specified canonical project references')
    args=parser.parse_args()
    fonts=Path('/usr/share/fonts/truetype/dejavu')
    pdfmetrics.registerFont(TTFont('FactSans',str(fonts/'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('FactSansBold',str(fonts/'DejaVuSans-Bold.ttf')))
    body=ParagraphStyle('body',fontName='FactSans',fontSize=8.5,leading=12,textColor=INK,spaceAfter=7)
    title=ParagraphStyle('title',parent=body,fontName='FactSansBold',fontSize=21,leading=25,spaceAfter=13)
    sub=ParagraphStyle('sub',parent=body,fontSize=8,textColor=GREY,spaceAfter=9)
    h2=ParagraphStyle('h2',parent=body,fontName='FactSansBold',fontSize=11,leading=15,textColor=GOLD,spaceBefore=12,spaceAfter=6)
    small=ParagraphStyle('small',parent=body,fontSize=7.5,leading=10,textColor=GREY)
    rows={r['Asset reference']:r for r in csv.DictReader((ROOT/'catalogue.csv').open(encoding='utf-8-sig'))}
    mapping=json.loads((ROOT/'project-map.json').read_text())
    def p(s,style=body):return Paragraph(escape(plain(s)).replace('\n','<br/>'),style)
    def blocks(text,style=body):
        return [p(x.strip().removeprefix('- '),style) for x in text.split('\n\n') if x.strip()]
    def footer(canvas,doc):
        canvas.saveState();canvas.setStrokeColor(GOLD);canvas.line(43,52,A4[0]-43,52)
        canvas.setFillColor(GREY);canvas.setFont('FactSans',7)
        canvas.drawString(43,38,'THEARCHITECT_MAX | PRIVATE SOFTWARE IP | 16 OCTOBER 2026')
        canvas.drawRightString(A4[0]-43,38,str(doc.page));canvas.restoreState()
    generated=[]
    for m in mapping['projects']:
        if args.refs and m['ref'] not in args.refs:continue
        row=rows[m['ref']];folder=ROOT/m['productPage'];folder=folder.parent
        text=(folder/'product-brief.md').read_text();sec=sections(text)
        intro=text.split('Buyer-facing edition:',1)[1].split('\n\n',1)[1].split('\n## ',1)[0].strip()
        story=[p(m['ref']+' / '+row['Reference alias']+' / INDEPENDENT IP ASSET',sub),p(m['title'],title),p(intro),p('Product overview',h2)]
        story+=blocks(sec['Product overview'])
        story+=[p('Documented functions',h2)]
        story+=[p('• '+x.removeprefix('- ')) for x in sec['Documented functions'].splitlines() if x.startswith('- ')]
        story+=[p('Potential buyer fit',h2)]
        story+=[p(' / '.join(x.removeprefix('- ') for x in sec['Potential buyers'].splitlines() if x.startswith('- ')))]
        story+=[p('Buyer profiles are positioning suggestions; they are not established customers or contracts.',small),p('Documented output types',h2)]
        story+=[p(' / '.join(x.removeprefix('- ') for x in sec['Documented output types'].splitlines() if x.startswith('- ')))]
        story+=[p('Profile and full editable brief',h2),p(m['profileUrl'],small),p('The full editable brief accompanies this factsheet and retains the detailed product and transaction boundaries.',small),PageBreak()]
        story+=[p(m['ref']+' / CURRENT POSITION & ACQUISITION',sub),p('Status and commercial reference',title)]
        money=Table([[p('SELLER ASKING REFERENCE',small),p('RECREATION ESTIMATE',small)],[p('EUR '+format(m['sellerAskEUR'],','),h2),p('EUR '+format(m['recreationCostEUR'],','),h2)]],colWidths=[250,250])
        money.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#f3eee5')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10)]))
        story+=[money,Spacer(1,10),p('Current repository documentation',h2)]
        story+=blocks(sec['Status and limitations'])
        story+=[p('Individual financial-reference review',h2)]
        story+=blocks(sec['Individual financial-reference review'].split('\n\n')[0],small)
        story+=[p('Commercial and delivery boundary',h2),p('Amounts are seller model estimates, not expenditure, a contractor quotation or independent market/income value. AS IS acquisition requires a written agreement defining first-party rights, exact delivery and acceptance. Third-party rights retain their own terms. Future development, hosting, support, customer content and credentials are separately scoped or excluded.',small),p('Source basis',h2),p(m['ref']+'-P: current documentation. '+m['ref']+'-C: financial-reference review, 16 October 2026. '+m['ref']+'-A: retained dated handover assessment. Shared WIPO, Knab and limited Upwork sources provide method/rate context, not asset appraisals. Product tests were not rerun.',small)]
        output=folder/'factsheet.pdf'
        SimpleDocTemplate(str(output),pagesize=A4,rightMargin=43,leftMargin=43,topMargin=43,bottomMargin=65,title=m['title']+' - '+m['ref'],author='THEARCHITECT_MAX',pageCompression=1).build(story,onFirstPage=footer,onLaterPages=footer)
        count=len(PdfReader(output).pages)
        assert count==2,(m['ref'],count)
        generated.append({'ref':m['ref'],'path':str(output.relative_to(ROOT)),'pages':count})
    print(json.dumps({'factsheets':len(generated),'pages':sum(x['pages'] for x in generated),'allTwoPages':True},indent=2))

if __name__=='__main__':main()
