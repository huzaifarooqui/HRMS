from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.utils import ImageReader

LETTERHEAD_PAGE=(545.979,802.143)
NAVY=colors.HexColor('#102A53')
TEXT=colors.HexColor('#222B38')
MUTED=colors.HexColor('#5F6B7A')
LINE=colors.HexColor('#D8DEE8')
SOFT=colors.HexColor('#F6F8FB')

def safe(v,fallback='-'):
    s=str(v or '').strip()
    return s if s else fallback

def fmt_date(v):
    if hasattr(v,'strftime'): return v.strftime('%d %B %Y')
    if isinstance(v,str) and v:
        try:return datetime.strptime(v[:10],'%Y-%m-%d').strftime('%d %B %Y')
        except ValueError:return v
    return '-'

def build_appointment_letter_pdf(data,background_path):
    out=BytesIO(); w,h=LETTERHEAD_PAGE
    doc=BaseDocTemplate(out,pagesize=LETTERHEAD_PAGE,leftMargin=18*mm,rightMargin=18*mm,
        topMargin=44*mm,bottomMargin=18*mm,title=f"Appointment Letter - {safe(data.get('employee_name'))}",
        author=safe(data.get('company_name'),'Guru Ram Singh Ji Associates'))
    bg=ImageReader(str(background_path))
    def page_bg(c,d):
        c.saveState(); c.drawImage(bg,0,0,width=w,height=h,mask='auto')
        c.setFillColor(colors.HexColor('#8A6A2B')); c.setFont('Helvetica-Bold',7)
        c.drawRightString(w-18*mm,12*mm,f"Page {d.page}"); c.restoreState()
    frame=Frame(18*mm,18*mm,w-36*mm,h-62*mm,id='appointmentBody',showBoundary=0)
    doc.addPageTemplates(PageTemplate(id='letterhead',frames=[frame],onPage=page_bg))

    st={
      'title':ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=15,leading=18,textColor=NAVY,alignment=TA_CENTER,spaceAfter=3*mm),
      'ref':ParagraphStyle('ref',fontName='Helvetica',fontSize=8.5,leading=11,textColor=MUTED),
      'body':ParagraphStyle('body',fontName='Helvetica',fontSize=9.2,leading=13.5,textColor=TEXT,spaceAfter=2.1*mm),
      'tight':ParagraphStyle('tight',fontName='Helvetica',fontSize=8.7,leading=12,textColor=TEXT,spaceAfter=1.4*mm),
      'head':ParagraphStyle('head',fontName='Helvetica-Bold',fontSize=9.6,leading=12,textColor=NAVY,spaceBefore=1.7*mm,spaceAfter=1.1*mm),
      'small':ParagraphStyle('small',fontName='Helvetica',fontSize=7.5,leading=9.5,textColor=MUTED),
      'smallb':ParagraphStyle('smallb',fontName='Helvetica-Bold',fontSize=7.5,leading=9.5,textColor=NAVY),
    }
    name=safe(data.get('employee_name')); designation=safe(data.get('designation'),'Employee')
    dept=safe(data.get('department'),'General'); joining=fmt_date(data.get('joining_date'))
    effective=fmt_date(data.get('effective_date')); issue=fmt_date(data.get('document_date'))
    location=safe(data.get('work_location')); reporting=safe(data.get('reporting_to'))
    probation=safe(data.get('probation_months'),'3'); empid=safe(data.get('login_id'))
    ref=safe(data.get('reference_no')); company=safe(data.get('company_name'),'Guru Ram Singh Ji Associates')
    extra=safe(data.get('additional_terms'),'')
    story=[Paragraph('APPOINTMENT LETTER',st['title'])]
    meta=Table([[Paragraph(f"<b>Ref. No.:</b> {ref}",st['ref']),Paragraph(f"<b>Date:</b> {issue}",st['ref'])]],
               colWidths=[(w-36*mm)*.58,(w-36*mm)*.42])
    meta.setStyle(TableStyle([('ALIGN',(1,0),(1,0),'RIGHT'),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story += [meta,Spacer(1,1.5*mm),Paragraph(f"Dear <b>{name}</b>,",st['body'])]
    story.append(Paragraph(
      f"With reference to your selection and completion of the required joining formalities, we are pleased to formally appoint you as <b>{designation}</b> in the <b>{dept}</b> department of <b>{company}</b>, effective from <b>{effective}</b>. This appointment is subject to the terms and conditions stated below and the company policies applicable from time to time.",st['body']))
    rows=[
      [Paragraph('EMPLOYEE ID',st['smallb']),Paragraph('DESIGNATION',st['smallb'])],
      [Paragraph(empid,st['tight']),Paragraph(designation,st['tight'])],
      [Paragraph('DEPARTMENT',st['smallb']),Paragraph('DATE OF JOINING',st['smallb'])],
      [Paragraph(dept,st['tight']),Paragraph(joining,st['tight'])],
      [Paragraph('REPORTING TO',st['smallb']),Paragraph('PROBATION',st['smallb'])],
      [Paragraph(reporting,st['tight']),Paragraph(f"{probation} month(s)",st['tight'])],
    ]
    tb=Table(rows,colWidths=[(w-36*mm)/2]*2)
    tb.setStyle(TableStyle([('BOX',(0,0),(-1,-1),.6,LINE),('INNERGRID',(0,0),(-1,-1),.35,LINE),
      ('BACKGROUND',(0,0),(-1,0),SOFT),
      ('BACKGROUND',(0,2),(-1,2),SOFT),('BACKGROUND',(0,4),(-1,4),SOFT),
      ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
      ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story += [tb,Spacer(1,2.5*mm)]
    clauses=[
      ('1. Nature of Appointment',f'Your appointment is for the position stated above. You will perform the duties ordinarily associated with your role and such other reasonable responsibilities as may be assigned by your reporting senior or management according to business requirements.'),
      ('2. Probation and Confirmation',f'You will remain on probation for <b>{probation} month(s)</b>, unless otherwise confirmed in writing. Confirmation will depend on satisfactory performance, conduct, attendance, completion of joining formalities and compliance with company requirements. The probation period may be extended where reasonably required.'),
      ('3. Duties, Responsibilities and Performance','You are expected to discharge your duties diligently, honestly and professionally; meet reasonable performance standards and timelines; cooperate with colleagues and supervisors; protect the interests and reputation of the company; and follow lawful instructions issued by authorised seniors.'),
      ('4. Working Hours, Attendance and Leave','Office timings, reporting requirements, attendance, late-coming, leave, weekly offs, holidays and related workplace rules will be governed by the company policies in force from time to time. You are responsible for maintaining accurate attendance and obtaining required approvals for leave or absence.'),
      ('5. Place of Posting and Transfer',f'Your present place of posting is <b>{location}</b>. Based on business requirements, the company may reasonably change your duties, reporting relationship, department, work location or assignment, subject to applicable law and company policy.'),
    ]
    for h1,b in clauses: story += [Paragraph(h1,st['head']),Paragraph(b,st['tight'])]
    story.append(PageBreak())
    clauses2=[
      ('6. Confidentiality and Data Protection','You must maintain strict confidentiality of all non-public information relating to the company, its clients, employees, systems, finances, operations and business affairs. Company information, records and credentials may be used only for authorised work and must not be copied, shared or retained without permission. This obligation continues after separation where applicable.'),
      ('7. Company Property and Assets','All documents, files, devices, credentials, records, identity cards and other assets issued or made available to you remain company property. They must be used responsibly, protected from loss or misuse, and returned in proper condition whenever requested or at the time of separation.'),
      ('8. Conduct, Discipline and Professional Standards','You are expected to maintain professional behaviour, respectful communication, workplace discipline, cleanliness and appropriate boundaries. Misconduct, unauthorised absence, falsification of records, misuse of company property or information, or material breach of policy may result in disciplinary action in accordance with company rules and applicable law.'),
      ('9. Accuracy of Information and Documents','This appointment is based on the information and documents provided by you. Material misrepresentation, falsification or withholding of relevant employment information may lead to appropriate action, including withdrawal or termination where permitted by applicable law and company policy.'),
      ('10. Outside Employment and Conflict of Interest','During employment, you must avoid activities or outside engagements that materially conflict with your duties, company interests, confidentiality obligations or working commitments. Any potential conflict should be disclosed to management.'),
      ('11. Policies and Amendments','Your employment is governed by the company policies, procedures and lawful instructions as amended from time to time. Such policies form part of the working conditions of your employment to the extent applicable.'),
      ('12. Separation and Full & Final Settlement','Resignation, termination, notice requirements, handover, clearance, return of company assets and full-and-final settlement will be governed by the applicable employment terms, company policies and law in force at the relevant time.'),
    ]
    for h1,b in clauses2: story += [Paragraph(h1,st['head']),Paragraph(b,st['tight'])]
    if extra: story += [Paragraph('13. Additional Terms',st['head']),Paragraph(extra.replace('\n','<br/>'),st['tight'])]
    story.append(Spacer(1,4*mm))
    story += [
      Paragraph('ACCEPTANCE OF APPOINTMENT',st['title']),
      Paragraph(f"I, <b>{name}</b>, acknowledge that I have read and understood this Appointment Letter and accept the appointment and the terms stated herein. I agree to comply with the applicable policies, procedures and lawful instructions of {company}.",st['body']),
      Spacer(1,3*mm)
    ]
    sig=Table([
      [Paragraph('<b>For Guru Ram Singh Ji Associates</b>',st['tight']),Paragraph('<b>Accepted by Employee</b>',st['tight'])],
      [Spacer(1,11*mm),Spacer(1,11*mm)],
      [Paragraph('Authorised Signatory',st['tight']),Paragraph(name,st['tight'])],
      [Paragraph('Name: __________________________',st['small']),Paragraph('Signature: ______________________',st['small'])],
      [Paragraph('Designation: ___________________',st['small']),Paragraph('Date: ___________________________',st['small'])],
    ],colWidths=[(w-36*mm)*.52,(w-36*mm)*.48])
    sig.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEABOVE',(0,2),(-1,2),.6,LINE),
      ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),6)]))
    story.append(sig)
    doc.build(story); out.seek(0); return out
