from io import BytesIO
from datetime import datetime
from decimal import Decimal, InvalidOperation
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
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
GREEN=colors.HexColor('#1F7A4D')

def safe(v,fallback='-'):
    s=str(v or '').strip()
    return s if s else fallback

def money(v):
    try:
        d=Decimal(str(v or 0))
    except (InvalidOperation, ValueError, TypeError):
        d=Decimal('0')
    return f"Rs. {d:,.2f}"

def month_label(v):
    try:return datetime.strptime(str(v),'%Y-%m').strftime('%B %Y')
    except:return safe(v)

def build_pay_slip_pdf(data,background_path):
    out=BytesIO(); w,h=LETTERHEAD_PAGE
    doc=BaseDocTemplate(out,pagesize=LETTERHEAD_PAGE,leftMargin=18*mm,rightMargin=18*mm,
        topMargin=44*mm,bottomMargin=18*mm,
        title=f"Pay Slip - {safe(data.get('employee_name'))} - {month_label(data.get('salary_month'))}",
        author=safe(data.get('company_name'),'Guru Ram Singh Ji Associates'))
    bg=ImageReader(str(background_path))
    def page_bg(c,d):
        c.saveState(); c.drawImage(bg,0,0,width=w,height=h,mask='auto')
        c.setFillColor(GOLD); c.setFont('Helvetica-Bold',7)
        c.drawRightString(w-18*mm,12*mm,f"Page {d.page}"); c.restoreState()
    frame=Frame(18*mm,18*mm,w-36*mm,h-62*mm,id='payslipBody',showBoundary=0)
    doc.addPageTemplates(PageTemplate(id='letterhead',frames=[frame],onPage=page_bg))

    st={
      'title':ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=15,leading=18,textColor=NAVY,alignment=TA_CENTER,spaceAfter=2*mm),
      'sub':ParagraphStyle('sub',fontName='Helvetica-Bold',fontSize=10.5,leading=13,textColor=GOLD,alignment=TA_CENTER,spaceAfter=4*mm),
      'body':ParagraphStyle('body',fontName='Helvetica',fontSize=8.8,leading=12,textColor=TEXT),
      'small':ParagraphStyle('small',fontName='Helvetica',fontSize=7.3,leading=9,textColor=MUTED),
      'smallb':ParagraphStyle('smallb',fontName='Helvetica-Bold',fontSize=7.3,leading=9,textColor=NAVY),
      'amount':ParagraphStyle('amount',fontName='Helvetica-Bold',fontSize=8.8,leading=11,textColor=TEXT,alignment=TA_RIGHT),
      'net':ParagraphStyle('net',fontName='Helvetica-Bold',fontSize=11,leading=14,textColor=GREEN),
    }

    name=safe(data.get('employee_name')); empid=safe(data.get('login_id'))
    des=safe(data.get('designation')); dept=safe(data.get('department'))
    salmonth=month_label(data.get('salary_month'))
    gross=Decimal(str(data.get('monthly_salary') or 0))
    earned=Decimal(str(data.get('earned_salary') or 0))
    att_ded=max(Decimal('0'),gross-earned)
    other_earn=Decimal(str(data.get('incentive') or 0))
    other_ded=Decimal(str(data.get('other_deductions') or 0))
    total_earn=earned+other_earn
    total_ded=att_ded+other_ded
    net=max(Decimal('0'),gross+other_earn-total_ded)

    story=[Paragraph('PAY SLIP',st['title']),Paragraph(salmonth.upper(),st['sub'])]

    details=[
      [Paragraph('EMPLOYEE NAME',st['smallb']),Paragraph('EMPLOYEE ID',st['smallb'])],
      [Paragraph(name,st['body']),Paragraph(empid,st['body'])],
      [Paragraph('DESIGNATION',st['smallb']),Paragraph('DEPARTMENT',st['smallb'])],
      [Paragraph(des,st['body']),Paragraph(dept,st['body'])],
      [Paragraph('SALARY MONTH',st['smallb']),Paragraph('TOTAL CALENDAR DAYS',st['smallb'])],
      [Paragraph(salmonth,st['body']),Paragraph(str(data.get('total_days') or 0),st['body'])],
    ]
    tb=Table(details,colWidths=[(w-36*mm)/2]*2)
    tb.setStyle(TableStyle([
      ('BOX',(0,0),(-1,-1),.6,LINE),('INNERGRID',(0,0),(-1,-1),.35,LINE),
      ('BACKGROUND',(0,0),(-1,0),SOFT),('BACKGROUND',(0,2),(-1,2),SOFT),('BACKGROUND',(0,4),(-1,4),SOFT),
      ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
      ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
      ('VALIGN',(0,0),(-1,-1),'MIDDLE')
    ]))
    story += [tb,Spacer(1,4*mm)]

    att=[
      [Paragraph('<b>Attendance Summary</b>',st['body']),'','',''],
      [Paragraph('Present',st['smallb']),Paragraph('Late',st['smallb']),Paragraph('Half Day',st['smallb']),Paragraph('Absent / Leave',st['smallb'])],
      [Paragraph(str(data.get('present') or 0),st['body']),Paragraph(str(data.get('late') or 0),st['body']),
       Paragraph(str(data.get('half_days') or 0),st['body']),Paragraph(str(data.get('absent') or 0),st['body'])],
      [Paragraph('Payable Days',st['smallb']),Paragraph(str(data.get('final_days') or 0),st['body']),Paragraph('Holiday Credit',st['smallb']),Paragraph(str(data.get('holidays') or 0),st['body'])],
    ]
    at=Table(att,colWidths=[(w-36*mm)/4]*4)
    at.setStyle(TableStyle([
      ('SPAN',(0,0),(-1,0)),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EEF3FA')),
      ('BOX',(0,0),(-1,-1),.6,LINE),('INNERGRID',(0,1),(-1,-1),.35,LINE),
      ('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
      ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
    ]))
    story += [at,Spacer(1,4*mm)]

    payroll=[
      [Paragraph('<b>EARNINGS</b>',st['body']),Paragraph('<b>AMOUNT</b>',st['body']),
       Paragraph('<b>DEDUCTIONS</b>',st['body']),Paragraph('<b>AMOUNT</b>',st['body'])],
      [Paragraph('Monthly Gross Salary',st['body']),Paragraph(money(gross),st['amount']),
       Paragraph('Attendance Deduction',st['body']),Paragraph(money(att_ded),st['amount'])],
      [Paragraph('Incentive',st['body']),Paragraph(money(other_earn),st['amount']),
       Paragraph('Other Deductions',st['body']),Paragraph(money(other_ded),st['amount'])],
      [Paragraph('<b>Total Earnings</b>',st['body']),Paragraph(f"<b>{money(gross+other_earn)}</b>",st['amount']),
       Paragraph('<b>Total Deductions</b>',st['body']),Paragraph(f"<b>{money(total_ded)}</b>",st['amount'])],
    ]
    pt=Table(payroll,colWidths=[(w-36*mm)*.29,(w-36*mm)*.21,(w-36*mm)*.29,(w-36*mm)*.21])
    pt.setStyle(TableStyle([
      ('BOX',(0,0),(-1,-1),.6,LINE),('INNERGRID',(0,0),(-1,-1),.35,LINE),
      ('BACKGROUND',(0,0),(-1,0),NAVY),('TEXTCOLOR',(0,0),(-1,0),colors.white),
      ('BACKGROUND',(0,3),(-1,3),SOFT),
      ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
      ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
      ('VALIGN',(0,0),(-1,-1),'MIDDLE')
    ]))
    story += [pt,Spacer(1,4*mm)]

    netbox=Table([[Paragraph('NET PAYABLE',st['smallb']),Paragraph(money(net),st['net'])]],
                 colWidths=[(w-36*mm)*.62,(w-36*mm)*.38])
    netbox.setStyle(TableStyle([
      ('BOX',(0,0),(-1,-1),1,GOLD),('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#FBF7EE')),
      ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),10),
      ('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
      ('ALIGN',(1,0),(1,0),'RIGHT')
    ]))
    story += [netbox,Spacer(1,4*mm)]
    story.append(Paragraph(
      'This pay slip is system-generated from the employee salary and attendance records available in GRSJ HRMS for the selected month. Statutory deductions or adjustments not configured in HRMS should be recorded through the authorised payroll process.',st['small']))
    if safe(data.get('remarks'),'') not in ('','-'):
        story += [Spacer(1,2*mm),Paragraph(f"<b>Remarks:</b> {safe(data.get('remarks'))}",st['small'])]

    doc.build(story); out.seek(0); return out
