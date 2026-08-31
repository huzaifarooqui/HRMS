from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.utils import ImageReader

LETTERHEAD_PAGE=(545.979,802.143)
NAVY=colors.HexColor('#102A53')
GOLD=colors.HexColor('#A47B2C')
TEXT=colors.HexColor('#222B38')
MUTED=colors.HexColor('#5F6B7A')
LINE=colors.HexColor('#D8DEE8')
SOFT=colors.HexColor('#F6F8FB')

def safe(v,fallback='-'):
    s=str(v or '').strip()
    return s if s else fallback

def fmt_date(v):
    if hasattr(v,'strftime'):
        return v.strftime('%d %B %Y')
    if isinstance(v,str) and v:
        try:
            return datetime.strptime(v[:10],'%Y-%m-%d').strftime('%d %B %Y')
        except ValueError:
            return v
    return '-'

def build_experience_letter_pdf(data,background_path):
    out=BytesIO()
    w,h=LETTERHEAD_PAGE

    doc=BaseDocTemplate(
        out,pagesize=LETTERHEAD_PAGE,
        leftMargin=18*mm,rightMargin=18*mm,
        topMargin=44*mm,bottomMargin=18*mm,
        title=f"Experience Letter - {safe(data.get('employee_name'))}",
        author=safe(data.get('company_name'),'Guru Ram Singh Ji Associates')
    )

    bg=ImageReader(str(background_path))

    def page_bg(c,d):
        c.saveState()
        c.drawImage(bg,0,0,width=w,height=h,mask='auto')
        c.setFillColor(GOLD)
        c.setFont('Helvetica-Bold',7)
        c.drawRightString(w-18*mm,12*mm,f"Page {d.page}")
        c.restoreState()

    frame=Frame(18*mm,18*mm,w-36*mm,h-62*mm,id='experienceBody',showBoundary=0)
    doc.addPageTemplates(PageTemplate(id='letterhead',frames=[frame],onPage=page_bg))

    st={
        'title':ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=15,leading=18,textColor=NAVY,alignment=TA_CENTER,spaceAfter=3*mm),
        'ref':ParagraphStyle('ref',fontName='Helvetica',fontSize=8.5,leading=11,textColor=MUTED),
        'body':ParagraphStyle('body',fontName='Helvetica',fontSize=9.4,leading=14,textColor=TEXT,spaceAfter=2.5*mm),
        'tight':ParagraphStyle('tight',fontName='Helvetica',fontSize=8.9,leading=12.5,textColor=TEXT,spaceAfter=1.6*mm),
        'head':ParagraphStyle('head',fontName='Helvetica-Bold',fontSize=9.8,leading=12,textColor=NAVY,spaceBefore=1.7*mm,spaceAfter=1.1*mm),
        'small':ParagraphStyle('small',fontName='Helvetica',fontSize=7.5,leading=9.5,textColor=MUTED),
        'smallb':ParagraphStyle('smallb',fontName='Helvetica-Bold',fontSize=7.5,leading=9.5,textColor=NAVY),
    }

    name=safe(data.get('employee_name'))
    empid=safe(data.get('login_id'))
    designation=safe(data.get('designation'),'Employee')
    department=safe(data.get('department'),'General')
    join_date=fmt_date(data.get('joining_date'))
    last_day=fmt_date(data.get('last_working_date'))
    issue_date=fmt_date(data.get('document_date'))
    ref=safe(data.get('reference_no'))
    company=safe(data.get('company_name'),'Guru Ram Singh Ji Associates')
    role_summary=safe(
        data.get('role_summary'),
        f'During the course of employment, {name} was responsible for the duties and responsibilities associated with the role of {designation}, together with other reasonable assignments entrusted by the reporting senior or management.'
    )
    conduct=safe(
        data.get('conduct_remarks'),
        'During the tenure with the organisation, the employee carried out assigned responsibilities professionally and maintained appropriate workplace conduct.'
    )
    additional=safe(data.get('additional_remarks'),'')

    story=[Paragraph('EXPERIENCE LETTER',st['title'])]

    meta=Table(
        [[Paragraph(f"<b>Ref. No.:</b> {ref}",st['ref']),Paragraph(f"<b>Date:</b> {issue_date}",st['ref'])]],
        colWidths=[(w-36*mm)*0.58,(w-36*mm)*0.42]
    )
    meta.setStyle(TableStyle([
        ('ALIGN',(1,0),(1,0),'RIGHT'),
        ('BOTTOMPADDING',(0,0),(-1,-1),5)
    ]))
    story += [meta,Spacer(1,2*mm)]

    story.append(Paragraph('<b>TO WHOMSOEVER IT MAY CONCERN</b>',ParagraphStyle(
        'whom',parent=st['body'],fontName='Helvetica-Bold',fontSize=10.3,
        leading=13,textColor=NAVY,alignment=TA_CENTER,spaceAfter=4*mm
    )))

    story.append(Paragraph(
        f"This is to certify that <b>{name}</b> (Employee ID: <b>{empid}</b>) was employed with <b>{company}</b> from <b>{join_date}</b> to <b>{last_day}</b>. At the time of separation, the employee was serving as <b>{designation}</b> in the <b>{department}</b> department.",
        st['body']
    ))

    details=[
        [Paragraph('EMPLOYEE NAME',st['smallb']),Paragraph('EMPLOYEE ID',st['smallb'])],
        [Paragraph(name,st['tight']),Paragraph(empid,st['tight'])],
        [Paragraph('DESIGNATION',st['smallb']),Paragraph('DEPARTMENT',st['smallb'])],
        [Paragraph(designation,st['tight']),Paragraph(department,st['tight'])],
        [Paragraph('DATE OF JOINING',st['smallb']),Paragraph('LAST WORKING DAY',st['smallb'])],
        [Paragraph(join_date,st['tight']),Paragraph(last_day,st['tight'])],
    ]
    tb=Table(details,colWidths=[(w-36*mm)/2]*2)
    tb.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),.6,LINE),
        ('INNERGRID',(0,0),(-1,-1),.35,LINE),
        ('BACKGROUND',(0,0),(-1,0),SOFT),
        ('BACKGROUND',(0,2),(-1,2),SOFT),
        ('BACKGROUND',(0,4),(-1,4),SOFT),
        ('LEFTPADDING',(0,0),(-1,-1),8),
        ('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),5),
        ('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE')
    ]))
    story += [tb,Spacer(1,4*mm)]

    story += [
        Paragraph('Role & Responsibilities',st['head']),
        Paragraph(role_summary,st['body']),
        Paragraph('Performance & Conduct',st['head']),
        Paragraph(conduct,st['body']),
    ]

    if additional:
        story += [
            Paragraph('Additional Remarks',st['head']),
            Paragraph(additional.replace('\n','<br/>'),st['body'])
        ]

    story += [
        Spacer(1,2*mm),
        Paragraph(
            f"We appreciate the contribution made during the period of association with {company} and wish {name} success in future professional endeavours.",
            st['body']
        ),
        Spacer(1,8*mm)
    ]

    sig=Table([
        [Paragraph('<b>For Guru Ram Singh Ji Associates</b>',st['tight'])],
        [Spacer(1,16*mm)],
        [Paragraph('Authorised Signatory',st['tight'])],
        [Paragraph('Name: ______________________________',st['small'])],
        [Paragraph('Designation: _________________________',st['small'])],
    ],colWidths=[(w-36*mm)*0.55])
    sig.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LINEABOVE',(0,2),(0,2),.6,LINE),
        ('LEFTPADDING',(0,0),(-1,-1),0),
        ('RIGHTPADDING',(0,0),(-1,-1),6)
    ]))
    story.append(sig)

    doc.build(story)
    out.seek(0)
    return out
