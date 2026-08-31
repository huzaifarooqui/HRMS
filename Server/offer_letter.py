from io import BytesIO
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, PageBreak
)
from reportlab.lib.utils import ImageReader

# Keep the exact proportions of the company-supplied letterhead PDF.
LETTERHEAD_PAGE = (545.979, 802.143)
NAVY = colors.HexColor('#102A53')
GOLD = colors.HexColor('#C59137')
TEXT = colors.HexColor('#222B38')
MUTED = colors.HexColor('#5F6B7A')
LINE = colors.HexColor('#D8DEE8')
SOFT = colors.HexColor('#F6F8FB')


def money(value):
    try:
        val=Decimal(str(value or 0))
    except (InvalidOperation, ValueError, TypeError):
        val=Decimal('0')
    return f"Rs. {val:,.0f}"


def safe_text(value, fallback='-'):
    text=str(value or '').strip()
    return text if text else fallback


def fmt_date(value):
    if hasattr(value,'strftime'):
        return value.strftime('%d %B %Y')
    if isinstance(value,str) and value:
        try:return datetime.strptime(value[:10],'%Y-%m-%d').strftime('%d %B %Y')
        except ValueError:return value
    return '-'


def build_offer_letter_pdf(data, background_path):
    out=BytesIO()
    page_w,page_h=LETTERHEAD_PAGE

    class OfferDoc(BaseDocTemplate):
        pass

    doc=OfferDoc(out,pagesize=LETTERHEAD_PAGE,
                 leftMargin=18*mm,rightMargin=18*mm,
                 topMargin=44*mm,bottomMargin=25*mm,
                 title=f"Offer Letter - {safe_text(data.get('employee_name'))}",
                 author=safe_text(data.get('company_name'),'Guru Ram Singh Ji Associates'))

    bg=ImageReader(str(background_path))
    def page_bg(canvas,doc):
        canvas.saveState()
        canvas.drawImage(bg,0,0,width=page_w,height=page_h,mask='auto')
        canvas.setFillColor(colors.HexColor('#8A6A2B'))
        canvas.setFont('Helvetica-Bold',7)
        canvas.drawRightString(page_w-18*mm, 20.5*mm, f"Page {doc.page}")
        canvas.restoreState()

    frame=Frame(18*mm,25*mm,page_w-36*mm,page_h-69*mm,id='offerBody',showBoundary=0)
    doc.addPageTemplates(PageTemplate(id='letterhead',frames=[frame],onPage=page_bg))

    styles={
        'title':ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=15,leading=18,textColor=NAVY,alignment=TA_CENTER,spaceAfter=3*mm),
        'ref':ParagraphStyle('ref',fontName='Helvetica',fontSize=8.5,leading=11,textColor=MUTED),
        'body':ParagraphStyle('body',fontName='Helvetica',fontSize=9.3,leading=14,textColor=TEXT,spaceAfter=2.2*mm),
        'bodytight':ParagraphStyle('bodytight',fontName='Helvetica',fontSize=8.7,leading=12.2,textColor=TEXT,spaceAfter=1.4*mm),
        'head':ParagraphStyle('head',fontName='Helvetica-Bold',fontSize=9.5,leading=12,textColor=NAVY,spaceBefore=1.5*mm,spaceAfter=1.2*mm),
        'small':ParagraphStyle('small',fontName='Helvetica',fontSize=7.6,leading=10,textColor=MUTED),
        'smallbold':ParagraphStyle('smallbold',fontName='Helvetica-Bold',fontSize=7.6,leading=10,textColor=NAVY),
        'accept':ParagraphStyle('accept',fontName='Helvetica',fontSize=8.4,leading=12,textColor=TEXT),
    }

    employee_name=safe_text(data.get('employee_name'))
    designation=safe_text(data.get('designation'),'Employee')
    department=safe_text(data.get('department'),'General')
    joining=fmt_date(data.get('joining_date'))
    issue=fmt_date(data.get('document_date'))
    acceptance=fmt_date(data.get('acceptance_date'))
    probation=safe_text(data.get('probation_months'),'3')
    location=safe_text(data.get('work_location'))
    reporting=safe_text(data.get('reporting_to'),'Management')
    monthly=data.get('monthly_salary') or 0
    try: annual=Decimal(str(monthly))*12
    except: annual=Decimal('0')
    ref=safe_text(data.get('reference_no'))
    extra=safe_text(data.get('additional_terms'),'')
    company=safe_text(data.get('company_name'),'Guru Ram Singh Ji Associates')

    story=[]
    story.append(Paragraph('OFFER OF EMPLOYMENT',styles['title']))
    meta=Table([
        [Paragraph(f"<b>Ref. No.:</b> {ref}",styles['ref']),Paragraph(f"<b>Date:</b> {issue}",styles['ref'])]
    ],colWidths=[(page_w-36*mm)*0.58,(page_w-36*mm)*0.42])
    meta.setStyle(TableStyle([('ALIGN',(1,0),(1,0),'RIGHT'),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story += [meta,Spacer(1,1.5*mm)]

    story.append(Paragraph(f"Dear <b>{employee_name}</b>,",styles['body']))
    story.append(Paragraph(
        f"We are pleased to offer you employment with <b>{company}</b> for the position of <b>{designation}</b> in the <b>{department}</b> department. Based on our discussions and your profile, we believe your skills and contribution will be valuable to the organisation.",styles['body']))

    summary_data=[
        [Paragraph('POSITION',styles['smallbold']),Paragraph('DEPARTMENT',styles['smallbold'])],
        [Paragraph(designation,styles['bodytight']),Paragraph(department,styles['bodytight'])],
        [Paragraph('DATE OF JOINING',styles['smallbold']),Paragraph('WORK LOCATION',styles['smallbold'])],
        [Paragraph(joining,styles['bodytight']),Paragraph(location,styles['bodytight'])],
        [Paragraph('REPORTING TO',styles['smallbold']),Paragraph('PROBATION',styles['smallbold'])],
        [Paragraph(reporting,styles['bodytight']),Paragraph(f"{probation} month(s)",styles['bodytight'])],
    ]
    summary=Table(summary_data,colWidths=[(page_w-36*mm)/2]*2)
    summary.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),colors.white),('BOX',(0,0),(-1,-1),0.6,LINE),
        ('INNERGRID',(0,0),(-1,-1),0.35,LINE),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('BACKGROUND',(0,0),(-1,0),SOFT),('BACKGROUND',(0,2),(-1,2),SOFT),('BACKGROUND',(0,4),(-1,4),SOFT),
    ]))
    story += [summary,Spacer(1,2.5*mm)]

    # Annexure - I: salary structure follows the company reference screenshot.
    # For a gross monthly salary, Basic = 50%, HRA = 48.5%, Advance Monthly
    # Statutory Bonus = 1.5%. PF/ESIC are shown as '-' unless a future payroll
    # rule explicitly supplies those statutory values.
    try:
        gross=Decimal(str(monthly or 0))
    except (InvalidOperation, ValueError, TypeError):
        gross=Decimal('0')
    basic=(gross*Decimal('0.50')).quantize(Decimal('1'))
    bonus=(gross*Decimal('0.015')).quantize(Decimal('1'))
    hra=gross-basic-bonus
    annual_gross=gross*12

    def amt(v):
        try:return f"{Decimal(str(v)):,.0f}"
        except:return '-'

    story.append(Paragraph('1. Compensation',styles['head']))
    story.append(Paragraph('Your detailed salary structure forms part of this offer and is set out in <b>Annexure - I</b>. Statutory contributions and deductions will apply only where applicable under prevailing law and company payroll rules.',styles['bodytight']))
    story.append(PageBreak())
    annexure_parts=[]
    annexure_parts.append(Paragraph('<b>Annexure - I</b>',ParagraphStyle(
        'annexTitle',parent=styles['body'],fontName='Helvetica-Bold',
        fontSize=10,leading=12,textColor=colors.HexColor('#B42318'),
        alignment=TA_CENTER,spaceAfter=2.2*mm)))
    annexure_parts.append(Paragraph(f"<b>Name</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {employee_name}",styles['bodytight']))
    annexure_parts.append(Spacer(1,1*mm))
    annexure_parts.append(Paragraph(f"<b>Salary Components of {employee_name}</b>",ParagraphStyle(
        'salaryTitle',parent=styles['bodytight'],fontName='Helvetica-Bold',
        alignment=TA_CENTER,backColor=colors.HexColor('#D9D9D9'),
        borderColor=colors.black,borderWidth=.5,borderPadding=4,spaceAfter=0)))

    salary_rows=[
        [Paragraph('<b>Details</b>',styles['bodytight']),Paragraph('Monthly',styles['bodytight']),Paragraph('Annually',styles['bodytight'])],
        [Paragraph('Basic',styles['bodytight']),amt(basic),amt(basic*12)],
        [Paragraph('HRA',styles['bodytight']),amt(hra),amt(hra*12)],
        [Paragraph('Advance Monthly Statutory Bonus',styles['bodytight']),amt(bonus),amt(bonus*12)],
        ['', '', ''],
        [Paragraph('<b>Gross Salary</b>',styles['bodytight']),Paragraph(f"<b>{amt(gross)}</b>",styles['bodytight']),Paragraph(f"<b>{amt(annual_gross)}</b>",styles['bodytight'])],
        [Paragraph('Provident Fund @ 12% Employer Contribution',styles['bodytight']),'-','-'],
        [Paragraph('ESIC @ 3.25% Employer Contribution',styles['bodytight']),'-','-'],
        ['', '', ''],
        [Paragraph('<b>Cost to Company (CTC)</b>',styles['bodytight']),Paragraph(f"<b>{amt(gross)}</b>",styles['bodytight']),Paragraph(f"<b>{amt(annual_gross)}</b>",styles['bodytight'])],
        ['', '', ''],
        [Paragraph('Provident Fund @ 12% Employer Contribution',styles['bodytight']),'-','-'],
        [Paragraph('Provident Fund @ 12% Employee Contribution',styles['bodytight']),'-','-'],
        ['', '', ''],
        [Paragraph('<b>Total Deduction</b>',styles['bodytight']),'-','-'],
        ['', '', ''],
        [Paragraph('<b>In Hand (Take Home Salary)</b>',styles['bodytight']),Paragraph(f"<b>{amt(gross)}</b>",styles['bodytight']),Paragraph(f"<b>{amt(annual_gross)}</b>",styles['bodytight'])],
    ]
    salary_table=Table(salary_rows,colWidths=[(page_w-36*mm)*0.55,(page_w-36*mm)*0.20,(page_w-36*mm)*0.25],repeatRows=1)
    salary_table.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),0.6,colors.black),('INNERGRID',(0,0),(-1,-1),0.35,colors.black),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ALIGN',(1,0),(-1,-1),'RIGHT'),
        ('ALIGN',(1,0),(-1,0),'CENTER'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#F0F0F0')),
        ('BACKGROUND',(0,5),(-1,5),colors.HexColor('#F0F0F0')),
        ('BACKGROUND',(0,9),(-1,9),colors.HexColor('#F0F0F0')),
        ('BACKGROUND',(0,14),(-1,14),colors.HexColor('#F0F0F0')),
        ('BACKGROUND',(0,16),(-1,16),colors.HexColor('#F0F0F0')),
        ('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),
        ('TOPPADDING',(0,0),(-1,-1),2.5),('BOTTOMPADDING',(0,0),(-1,-1),2.5),
        ('SPAN',(0,4),(-1,4)),('SPAN',(0,8),(-1,8)),('SPAN',(0,10),(-1,10)),
        ('SPAN',(0,13),(-1,13)),('SPAN',(0,15),(-1,15)),
    ]))
    annexure_parts.append(salary_table)
    annexure_parts.append(Paragraph('The salary structure above is subject to statutory applicability, deductions and company payroll rules in force from time to time.',styles['small']))
    story.append(KeepTogether(annexure_parts))
    story.append(Spacer(1,2.5*mm))

    story.append(Paragraph('2. Probation and Confirmation',styles['head']))
    story.append(Paragraph(f"You will initially be on probation for <b>{probation} month(s)</b> from your date of joining. Confirmation of employment will be subject to satisfactory performance, conduct, attendance and completion of required joining formalities. The company may extend the probation period where reasonably required.",styles['bodytight']))

    story.append(Paragraph('3. Working Hours, Attendance and Conduct',styles['head']))
    story.append(Paragraph('Your working hours, reporting requirements, attendance, leave, weekly offs and workplace conduct will be governed by the company rules and policies in force from time to time. You are expected to maintain professional behaviour, confidentiality and due care of company property and information.',styles['bodytight']))

    story.append(PageBreak())
    story.append(Paragraph('4. Confidentiality and Company Information',styles['head']))
    story.append(Paragraph('During and after your employment, you must keep confidential all non-public business, client, employee, financial, technical, operational and commercial information that comes to your knowledge through your work. Such information may be used only for authorised company purposes and must not be disclosed without written permission.',styles['body']))

    story.append(Paragraph('5. Documents and Background Information',styles['head']))
    story.append(Paragraph('This offer is based on the information and documents provided by you. You are required to submit all documents requested for employment records and verification. Material misrepresentation, falsification or withholding of relevant information may lead to withdrawal of this offer or appropriate action under company policy.',styles['body']))

    story.append(Paragraph('6. Company Policies and Changes',styles['head']))
    story.append(Paragraph('Your employment will be subject to the policies, procedures, rules and lawful instructions of the company as amended from time to time. The company may reasonably revise duties, reporting relationships, work location or internal policies according to business requirements.',styles['body']))

    story.append(Paragraph('7. Separation',styles['head']))
    story.append(Paragraph('Resignation, termination, notice requirements, handover, return of company assets and full-and-final settlement will be governed by the employment terms and company policies applicable at the relevant time, together with applicable law.',styles['body']))

    if extra:
        story.append(Paragraph('8. Additional Terms',styles['head']))
        story.append(Paragraph(extra.replace('\n','<br/>'),styles['body']))
        final_no=9
    else:
        final_no=8

    story.append(Paragraph(f'{final_no}. Acceptance of Offer',styles['head']))
    story.append(Paragraph(f"Please confirm your acceptance of this offer on or before <b>{acceptance}</b>. Your acceptance signifies that you have read and understood the terms stated in this letter. This offer is subject to completion of the company\'s joining requirements.",styles['body']))
    story.append(Spacer(1,2*mm))
    story.append(Paragraph('We look forward to welcoming you to Guru Ram Singh Ji Associates and wish you a successful association with us.',styles['body']))
    story.append(Spacer(1,4*mm))

    sig=Table([
        [Paragraph('<b>For Guru Ram Singh Ji Associates</b>',styles['accept']),Paragraph('<b>Accepted by Employee</b>',styles['accept'])],
        [Spacer(1,16*mm),Spacer(1,16*mm)],
        [Paragraph('Authorised Signatory',styles['accept']),Paragraph(employee_name,styles['accept'])],
        [Paragraph('Date: ____________________',styles['small']),Paragraph('Signature: ____________________',styles['small'])],
    ],colWidths=[(page_w-36*mm)*0.52,(page_w-36*mm)*0.48])
    sig.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEABOVE',(0,2),(0,2),0.6,LINE),('LINEABOVE',(1,2),(1,2),0.6,LINE),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),6)]))
    story.append(sig)

    doc.build(story)
    out.seek(0)
    return out
