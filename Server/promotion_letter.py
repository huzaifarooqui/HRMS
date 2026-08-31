from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.utils import ImageReader

LETTERHEAD_PAGE=(545.979,802.143)
NAVY=colors.HexColor('#102A53'); GOLD=colors.HexColor('#A47B2C')
TEXT=colors.HexColor('#222B38'); MUTED=colors.HexColor('#5F6B7A')
LINE=colors.HexColor('#D8DEE8'); SOFT=colors.HexColor('#F6F8FB')

def safe(v,fallback='-'):
    s=str(v or '').strip(); return s if s else fallback
def fmt_date(v):
    if hasattr(v,'strftime'): return v.strftime('%d %B %Y')
    if isinstance(v,str) and v:
        try:return datetime.strptime(v[:10],'%Y-%m-%d').strftime('%d %B %Y')
        except ValueError:return v
    return '-'
def money(v):
    try:return f"Rs. {float(v):,.0f}"
    except:return '-'

def build_promotion_letter_pdf(data,background_path):
    out=BytesIO(); w,h=LETTERHEAD_PAGE
    doc=BaseDocTemplate(out,pagesize=LETTERHEAD_PAGE,leftMargin=18*mm,rightMargin=18*mm,
        topMargin=44*mm,bottomMargin=18*mm,title=f"Promotion Letter - {safe(data.get('employee_name'))}",
        author=safe(data.get('company_name'),'Guru Ram Singh Ji Associates'))
    bg=ImageReader(str(background_path))
    def page_bg(c,d):
        c.saveState(); c.drawImage(bg,0,0,width=w,height=h,mask='auto')
        c.setFillColor(GOLD); c.setFont('Helvetica-Bold',7); c.drawRightString(w-18*mm,12*mm,f"Page {d.page}")
        c.restoreState()
    frame=Frame(18*mm,18*mm,w-36*mm,h-62*mm,id='promotionBody',showBoundary=0)
    doc.addPageTemplates(PageTemplate(id='letterhead',frames=[frame],onPage=page_bg))
    st={
      'title':ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=15,leading=18,textColor=NAVY,alignment=TA_CENTER,spaceAfter=3*mm),
      'ref':ParagraphStyle('ref',fontName='Helvetica',fontSize=8.5,leading=11,textColor=MUTED),
      'body':ParagraphStyle('body',fontName='Helvetica',fontSize=9.3,leading=13.8,textColor=TEXT,spaceAfter=2.3*mm),
      'tight':ParagraphStyle('tight',fontName='Helvetica',fontSize=8.8,leading=12.3,textColor=TEXT,spaceAfter=1.5*mm),
      'head':ParagraphStyle('head',fontName='Helvetica-Bold',fontSize=9.7,leading=12,textColor=NAVY,spaceBefore=1.8*mm,spaceAfter=1.1*mm),
      'small':ParagraphStyle('small',fontName='Helvetica',fontSize=7.5,leading=9.5,textColor=MUTED),
      'smallb':ParagraphStyle('smallb',fontName='Helvetica-Bold',fontSize=7.5,leading=9.5,textColor=NAVY),
      'highlight':ParagraphStyle('highlight',fontName='Helvetica-Bold',fontSize=10.2,leading=14,textColor=GOLD,alignment=TA_CENTER,spaceAfter=3*mm),
    }
    name=safe(data.get('employee_name')); empid=safe(data.get('login_id'))
    old_des=safe(data.get('current_designation')); new_des=safe(data.get('new_designation'))
    old_dep=safe(data.get('current_department')); new_dep=safe(data.get('new_department'))
    effective=fmt_date(data.get('effective_date')); issue=fmt_date(data.get('document_date'))
    reporting=safe(data.get('reporting_to')); ref=safe(data.get('reference_no'))
    company=safe(data.get('company_name'),'Guru Ram Singh Ji Associates')
    revised=data.get('revised_salary'); salary_applicable=str(data.get('salary_revision_applicable','No')).lower()=='yes'
    responsibilities=safe(data.get('revised_responsibilities'),'You will assume the responsibilities associated with your promoted role and such other reasonable duties as may be assigned by your reporting senior or management.')
    additional=safe(data.get('additional_terms'),'')
    story=[Paragraph('PROMOTION LETTER',st['title'])]
    meta=Table([[Paragraph(f"<b>Ref. No.:</b> {ref}",st['ref']),Paragraph(f"<b>Date:</b> {issue}",st['ref'])]],
               colWidths=[(w-36*mm)*.58,(w-36*mm)*.42])
    meta.setStyle(TableStyle([('ALIGN',(1,0),(1,0),'RIGHT'),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story += [meta,Spacer(1,1.5*mm),Paragraph(f"Dear <b>{name}</b>,",st['body'])]
    story.append(Paragraph(
      f"We are pleased to inform you that, in recognition of your contribution, performance and the confidence placed in your capabilities, you are being promoted from <b>{old_des}</b> to <b>{new_des}</b>, effective <b>{effective}</b>.",st['body']))
    story.append(Paragraph(f"Congratulations on your promotion to <b>{new_des}</b>.",st['highlight']))
    rows=[
      [Paragraph('EMPLOYEE ID',st['smallb']),Paragraph('EFFECTIVE DATE',st['smallb'])],
      [Paragraph(empid,st['tight']),Paragraph(effective,st['tight'])],
      [Paragraph('CURRENT DESIGNATION',st['smallb']),Paragraph('NEW DESIGNATION',st['smallb'])],
      [Paragraph(old_des,st['tight']),Paragraph(new_des,st['tight'])],
      [Paragraph('CURRENT DEPARTMENT',st['smallb']),Paragraph('NEW DEPARTMENT',st['smallb'])],
      [Paragraph(old_dep,st['tight']),Paragraph(new_dep,st['tight'])],
      [Paragraph('REPORTING TO / SENIOR',st['smallb']),Paragraph('SALARY REVISION',st['smallb'])],
      [Paragraph(reporting,st['tight']),Paragraph(money(revised)+'/ month' if salary_applicable and revised else 'No change / As communicated',st['tight'])],
    ]
    tb=Table(rows,colWidths=[(w-36*mm)/2]*2)
    tb.setStyle(TableStyle([('BOX',(0,0),(-1,-1),.6,LINE),('INNERGRID',(0,0),(-1,-1),.35,LINE),
      ('BACKGROUND',(0,0),(-1,0),SOFT),('BACKGROUND',(0,2),(-1,2),SOFT),('BACKGROUND',(0,4),(-1,4),SOFT),('BACKGROUND',(0,6),(-1,6),SOFT),
      ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
      ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story += [tb,Spacer(1,3*mm)]
    clauses=[
      ('1. New Role and Responsibilities',responsibilities),
      ('2. Reporting and Department',f'With effect from <b>{effective}</b>, you will be part of the <b>{new_dep}</b> department and will report to <b>{reporting}</b>. The reporting structure or responsibilities may be reasonably revised in accordance with business requirements and company policy.'),
      ('3. Compensation', (f'Your revised monthly salary will be <b>{money(revised)}</b> with effect from <b>{effective}</b>. Applicable statutory deductions, payroll rules and company policies will continue to apply.' if salary_applicable and revised else 'There is no salary revision recorded as part of this promotion letter. Your existing compensation and applicable payroll terms will continue unless separately revised and communicated in writing.')),
      ('4. Performance and Expectations','This promotion carries increased responsibility and accountability. You are expected to maintain high standards of performance, professional conduct, teamwork, confidentiality, attendance and compliance with company policies while supporting the objectives of your department and the organisation.'),
      ('5. Continuity of Employment Terms','Except for the changes specifically stated in this letter, all other applicable terms and conditions of your employment, including company policies and obligations, will continue to remain in force.'),
    ]
    for h1,b in clauses: story += [Paragraph(h1,st['head']),Paragraph(b,st['tight'])]
    if additional: story += [Paragraph('6. Additional Terms',st['head']),Paragraph(additional.replace('\n','<br/>'),st['tight'])]
    story += [PageBreak(),Paragraph(
      f"We appreciate your contribution to {company} and look forward to your continued growth and success in your new role. We wish you every success with your enhanced responsibilities.",st['body']),
      Spacer(1,5*mm)]
    sig=Table([
      [Paragraph('<b>For Guru Ram Singh Ji Associates</b>',st['tight']),Paragraph('<b>Accepted by Employee</b>',st['tight'])],
      [Spacer(1,15*mm),Spacer(1,15*mm)],
      [Paragraph('Authorised Signatory',st['tight']),Paragraph(name,st['tight'])],
      [Paragraph('Name: __________________________',st['small']),Paragraph('Signature: ______________________',st['small'])],
      [Paragraph('Designation: ___________________',st['small']),Paragraph('Date: ___________________________',st['small'])],
    ],colWidths=[(w-36*mm)*.52,(w-36*mm)*.48])
    sig.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEABOVE',(0,2),(-1,2),.6,LINE),
      ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),6)]))
    story.append(sig)
    doc.build(story);out.seek(0);return out
