from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.utils import ImageReader

LETTERHEAD_PAGE=(545.979,802.143)
NAVY=colors.HexColor('#102A53'); TEXT=colors.HexColor('#222B38')
MUTED=colors.HexColor('#5F6B7A'); LINE=colors.HexColor('#D8DEE8'); SOFT=colors.HexColor('#F6F8FB')

def safe(v,fallback='-'):
    s=str(v or '').strip(); return s if s else fallback
def fmt_date(v):
    if hasattr(v,'strftime'): return v.strftime('%d %B %Y')
    if isinstance(v,str) and v:
        try:return datetime.strptime(v[:10],'%Y-%m-%d').strftime('%d %B %Y')
        except ValueError:return v
    return '-'

def build_termination_letter_pdf(data,background_path):
    out=BytesIO(); w,h=LETTERHEAD_PAGE
    doc=BaseDocTemplate(out,pagesize=LETTERHEAD_PAGE,leftMargin=18*mm,rightMargin=18*mm,
        topMargin=44*mm,bottomMargin=18*mm,title=f"Termination Letter - {safe(data.get('employee_name'))}",
        author=safe(data.get('company_name'),'Guru Ram Singh Ji Associates'))
    bg=ImageReader(str(background_path))
    def page_bg(c,d):
        c.saveState(); c.drawImage(bg,0,0,width=w,height=h,mask='auto')
        c.setFillColor(colors.HexColor('#8A6A2B')); c.setFont('Helvetica-Bold',7)
        c.drawRightString(w-18*mm,12*mm,f"Page {d.page}"); c.restoreState()
    frame=Frame(18*mm,18*mm,w-36*mm,h-62*mm,id='terminationBody',showBoundary=0)
    doc.addPageTemplates(PageTemplate(id='letterhead',frames=[frame],onPage=page_bg))
    st={
      'title':ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=15,leading=18,textColor=NAVY,alignment=TA_CENTER,spaceAfter=3*mm),
      'ref':ParagraphStyle('ref',fontName='Helvetica',fontSize=8.5,leading=11,textColor=MUTED),
      'body':ParagraphStyle('body',fontName='Helvetica',fontSize=9.2,leading=13.5,textColor=TEXT,spaceAfter=2.1*mm),
      'tight':ParagraphStyle('tight',fontName='Helvetica',fontSize=8.8,leading=12.2,textColor=TEXT,spaceAfter=1.5*mm),
      'head':ParagraphStyle('head',fontName='Helvetica-Bold',fontSize=9.7,leading=12,textColor=NAVY,spaceBefore=1.7*mm,spaceAfter=1.1*mm),
      'small':ParagraphStyle('small',fontName='Helvetica',fontSize=7.5,leading=9.5,textColor=MUTED),
      'smallb':ParagraphStyle('smallb',fontName='Helvetica-Bold',fontSize=7.5,leading=9.5,textColor=NAVY),
    }
    name=safe(data.get('employee_name')); empid=safe(data.get('login_id'))
    des=safe(data.get('designation'),'Employee'); dept=safe(data.get('department'),'General')
    issue=fmt_date(data.get('document_date')); effective=fmt_date(data.get('effective_date'))
    last_working=fmt_date(data.get('last_working_date')); ref=safe(data.get('reference_no'))
    reason=safe(data.get('termination_reason')); category=safe(data.get('termination_category'))
    notice=safe(data.get('notice_details'),'As per applicable company policy')
    fnf=safe(data.get('fnf_details'),"In accordance with the company's applicable policies and the law, the 'Full and Final settlement' process will be completed only after the necessary clearances have been obtained and a period of 45 days has elapsed.")
    company=safe(data.get('company_name'),'Guru Ram Singh Ji Associates')
    assets=safe(data.get('asset_instructions'),'Return all company property, records, credentials and assets in your possession on or before the last working day.')
    additional=safe(data.get('additional_terms'),'')
    story=[Paragraph('TERMINATION OF EMPLOYMENT',st['title'])]
    meta=Table([[Paragraph(f"<b>Ref. No.:</b> {ref}",st['ref']),Paragraph(f"<b>Date:</b> {issue}",st['ref'])]],
               colWidths=[(w-36*mm)*.58,(w-36*mm)*.42])
    meta.setStyle(TableStyle([('ALIGN',(1,0),(1,0),'RIGHT'),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story += [meta,Spacer(1,1.5*mm),Paragraph(f"Dear <b>{name}</b>,",st['body'])]
    story.append(Paragraph(
      f"This letter serves as formal notice that your employment with <b>{company}</b> in the position of <b>{des}</b> is being terminated effective <b>{effective}</b>. Your last working day will be <b>{last_working}</b>, subject to completion of the required handover and clearance formalities.",st['body']))
    rows=[
      [Paragraph('EMPLOYEE ID',st['smallb']),Paragraph('DESIGNATION',st['smallb'])],
      [Paragraph(empid,st['tight']),Paragraph(des,st['tight'])],
      [Paragraph('DEPARTMENT',st['smallb']),Paragraph('TERMINATION CATEGORY',st['smallb'])],
      [Paragraph(dept,st['tight']),Paragraph(category,st['tight'])],
      [Paragraph('EFFECTIVE DATE',st['smallb']),Paragraph('LAST WORKING DAY',st['smallb'])],
      [Paragraph(effective,st['tight']),Paragraph(last_working,st['tight'])],
    ]
    tb=Table(rows,colWidths=[(w-36*mm)/2]*2)
    tb.setStyle(TableStyle([('BOX',(0,0),(-1,-1),.6,LINE),('INNERGRID',(0,0),(-1,-1),.35,LINE),
      ('BACKGROUND',(0,0),(-1,0),SOFT),('BACKGROUND',(0,2),(-1,2),SOFT),('BACKGROUND',(0,4),(-1,4),SOFT),
      ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
      ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story += [tb,Spacer(1,3*mm)]
    clauses=[
      ('1. Reason for Termination',reason),
      ('2. Handover and Company Property',assets),
      ('3. Full & Final Settlement',fnf),
      ('4. Confidentiality and Company Information','Your obligations relating to confidentiality, non-public company information, client information, records, credentials and intellectual property continue after separation to the extent applicable under your employment terms, company policy and law.'),
      ('5. Records, Access and Clearance','You must complete all pending work handover, return physical and digital records, surrender company access/credentials where applicable, and cooperate with the clearance process. Company system access may be withdrawn or disabled as part of the separation process.'),
      ('6. Employment Documents','Any relieving letter, experience letter, settlement statement or other separation document will be issued subject to completion of applicable clearance and company procedures.'),
    ]
    for h1,b in clauses: story += [Paragraph(h1,st['head']),Paragraph(b,st['tight'])]
    if additional:
        story += [Paragraph('7. Additional Information',st['head']),Paragraph(additional.replace('\n','<br/>'),st['tight'])]
    story += [PageBreak(),Paragraph(
      'We request you to complete the separation formalities professionally and coordinate with the authorised company representative for handover and clearance.',st['body']),
      Spacer(1,2*mm)]
    sig=Table([
      [Paragraph('<b>For Guru Ram Singh Ji Associates</b>',st['tight']),Paragraph('<b>Acknowledged by Employee</b>',st['tight'])],
      [Spacer(1,15*mm),Spacer(1,15*mm)],
      [Paragraph('Authorised Signatory',st['tight']),Paragraph(name,st['tight'])],
      [Paragraph('Name: __________________________',st['small']),Paragraph('Signature: ______________________',st['small'])],
      [Paragraph('Designation: ___________________',st['small']),Paragraph('Date: ___________________________',st['small'])],
    ],colWidths=[(w-36*mm)*.52,(w-36*mm)*.48])
    sig.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEABOVE',(0,2),(-1,2),.6,LINE),
      ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),6)]))
    story.append(sig)
    doc.build(story); out.seek(0); return out
