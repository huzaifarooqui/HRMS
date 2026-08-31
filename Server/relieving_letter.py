from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.utils import ImageReader

PAGE=(545.979,802.143)
NAVY=colors.HexColor('#102A53'); GOLD=colors.HexColor('#A47B2C')
TEXT=colors.HexColor('#222B38'); MUTED=colors.HexColor('#5F6B7A')
LINE=colors.HexColor('#D8DEE8'); SOFT=colors.HexColor('#F6F8FB')

def safe(v,fallback='-'):
    s=str(v or '').strip(); return s if s else fallback
def fmt(v):
    if hasattr(v,'strftime'): return v.strftime('%d %B %Y')
    try:return datetime.strptime(str(v)[:10],'%Y-%m-%d').strftime('%d %B %Y')
    except:return safe(v)

def build_relieving_letter_pdf(data,bgpath):
    out=BytesIO();w,h=PAGE
    doc=BaseDocTemplate(out,pagesize=PAGE,leftMargin=18*mm,rightMargin=18*mm,
        topMargin=44*mm,bottomMargin=18*mm,title='Relieving Letter - '+safe(data.get('employee_name')),
        author=safe(data.get('company_name'),'Guru Ram Singh Ji Associates'))
    bg=ImageReader(str(bgpath))
    def onpage(c,d):
        c.saveState();c.drawImage(bg,0,0,width=w,height=h,mask='auto')
        c.setFillColor(GOLD);c.setFont('Helvetica-Bold',7);c.drawRightString(w-18*mm,12*mm,f'Page {d.page}');c.restoreState()
    doc.addPageTemplates(PageTemplate(id='p',frames=[Frame(18*mm,18*mm,w-36*mm,h-62*mm,id='f')],onPage=onpage))
    st={
      'title':ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=15,leading=18,textColor=NAVY,alignment=TA_CENTER,spaceAfter=3*mm),
      'ref':ParagraphStyle('ref',fontName='Helvetica',fontSize=8.5,leading=11,textColor=MUTED),
      'body':ParagraphStyle('body',fontName='Helvetica',fontSize=9.4,leading=14,textColor=TEXT,spaceAfter=2.5*mm),
      'tight':ParagraphStyle('tight',fontName='Helvetica',fontSize=8.9,leading=12.5,textColor=TEXT,spaceAfter=1.5*mm),
      'head':ParagraphStyle('head',fontName='Helvetica-Bold',fontSize=9.8,leading=12,textColor=NAVY,spaceBefore=1.5*mm,spaceAfter=1*mm),
      'small':ParagraphStyle('small',fontName='Helvetica',fontSize=7.5,leading=9.5,textColor=MUTED),
      'smallb':ParagraphStyle('smallb',fontName='Helvetica-Bold',fontSize=7.5,leading=9.5,textColor=NAVY)}
    name=safe(data.get('employee_name')); company=safe(data.get('company_name'),'Guru Ram Singh Ji Associates')
    ref=safe(data.get('reference_no')); issue=fmt(data.get('document_date')); join=fmt(data.get('joining_date')); last=fmt(data.get('last_working_date'))
    des=safe(data.get('designation'));dept=safe(data.get('department'));empid=safe(data.get('login_id'))
    separation=safe(data.get('separation_type'),'Resignation')
    clearance=safe(data.get('clearance_status'),'Completed')
    handover=safe(data.get('handover_remarks'),'The required handover and applicable company clearance formalities have been completed.')
    fnf=safe(data.get('fnf_status'),'Full & Final settlement will be processed in accordance with applicable company policy and law.')
    additional=safe(data.get('additional_remarks'),'')

    story=[Paragraph('RELIEVING LETTER',st['title'])]
    meta=Table([[Paragraph(f'<b>Ref. No.:</b> {ref}',st['ref']),Paragraph(f'<b>Date:</b> {issue}',st['ref'])]],colWidths=[(w-36*mm)*.58,(w-36*mm)*.42])
    meta.setStyle(TableStyle([('ALIGN',(1,0),(1,0),'RIGHT')]))
    story += [meta,Spacer(1,2*mm),Paragraph(f'Dear <b>{name}</b>,',st['body'])]
    story.append(Paragraph(
      f'This is to confirm that you have been relieved from your duties and responsibilities with <b>{company}</b> at the close of business on <b>{last}</b>. Your employment with the organisation commenced on <b>{join}</b>, and at the time of separation you were serving as <b>{des}</b> in the <b>{dept}</b> department.',st['body']))
    rows=[
      [Paragraph('EMPLOYEE ID',st['smallb']),Paragraph('SEPARATION TYPE',st['smallb'])],
      [Paragraph(empid,st['tight']),Paragraph(separation,st['tight'])],
      [Paragraph('DESIGNATION',st['smallb']),Paragraph('DEPARTMENT',st['smallb'])],
      [Paragraph(des,st['tight']),Paragraph(dept,st['tight'])],
      [Paragraph('DATE OF JOINING',st['smallb']),Paragraph('LAST WORKING DAY',st['smallb'])],
      [Paragraph(join,st['tight']),Paragraph(last,st['tight'])],
      [Paragraph('CLEARANCE STATUS',st['smallb']),Paragraph('RELIEVING EFFECTIVE',st['smallb'])],
      [Paragraph(clearance,st['tight']),Paragraph(last,st['tight'])],
    ]
    tb=Table(rows,colWidths=[(w-36*mm)/2]*2)
    tb.setStyle(TableStyle([('BOX',(0,0),(-1,-1),.6,LINE),('INNERGRID',(0,0),(-1,-1),.35,LINE),
      ('BACKGROUND',(0,0),(-1,0),SOFT),('BACKGROUND',(0,2),(-1,2),SOFT),('BACKGROUND',(0,4),(-1,4),SOFT),('BACKGROUND',(0,6),(-1,6),SOFT),
      ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story += [tb,Spacer(1,4*mm),
      Paragraph('1. Handover & Clearance',st['head']),Paragraph(handover,st['tight']),
      Paragraph('2. Full & Final Settlement',st['head']),Paragraph(fnf,st['tight']),
      Paragraph('3. Continuing Obligations',st['head']),Paragraph(
        'Any continuing obligations relating to confidentiality, company information, records, intellectual property or other applicable post-employment obligations remain subject to your employment terms, company policy and applicable law.',st['tight'])]
    if additional:
        story += [Paragraph('4. Additional Remarks',st['head']),Paragraph(additional.replace('\n','<br/>'),st['tight'])]
    story += [Spacer(1,2*mm),Paragraph(
      f'We acknowledge your association with {company} and wish you success in your future professional endeavours.',st['body']),Spacer(1,7*mm)]
    sig=Table([[Paragraph('<b>For Guru Ram Singh Ji Associates</b>',st['tight'])],[Spacer(1,15*mm)],[Paragraph('Authorised Signatory',st['tight'])],[Paragraph('Name: ______________________________',st['small'])],[Paragraph('Designation: _________________________',st['small'])]],colWidths=[(w-36*mm)*.55])
    sig.setStyle(TableStyle([('LINEABOVE',(0,2),(0,2),.6,LINE),('LEFTPADDING',(0,0),(-1,-1),0)]));story.append(sig)
    doc.build(story);out.seek(0);return out
