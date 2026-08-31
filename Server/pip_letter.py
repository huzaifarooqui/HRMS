from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.utils import ImageReader

PAGE=(545.979,802.143)
NAVY=colors.HexColor('#102A53'); GOLD=colors.HexColor('#A47B2C'); TEXT=colors.HexColor('#222B38')
MUTED=colors.HexColor('#5F6B7A'); LINE=colors.HexColor('#D8DEE8'); SOFT=colors.HexColor('#F6F8FB')

def s(v,d='-'):
    x=str(v or '').strip(); return x if x else d

def fd(v):
    try:return datetime.strptime(str(v)[:10],'%Y-%m-%d').strftime('%d %B %Y')
    except:return s(v)

def build_pip_letter_pdf(data,bgpath):
    out=BytesIO(); w,h=PAGE
    doc=BaseDocTemplate(out,pagesize=PAGE,leftMargin=18*mm,rightMargin=18*mm,topMargin=44*mm,bottomMargin=18*mm,
                        title='Performance Improvement Plan - '+s(data.get('employee_name')))
    bg=ImageReader(str(bgpath))
    def onpage(c,d):
        c.saveState(); c.drawImage(bg,0,0,width=w,height=h,mask='auto'); c.setFillColor(GOLD); c.setFont('Helvetica-Bold',7)
        c.drawRightString(w-18*mm,12*mm,f'Page {d.page}'); c.restoreState()
    doc.addPageTemplates(PageTemplate(id='p',frames=[Frame(18*mm,18*mm,w-36*mm,h-62*mm,id='f')],onPage=onpage))
    st={
      'title':ParagraphStyle('t',fontName='Helvetica-Bold',fontSize=15,leading=18,textColor=NAVY,alignment=TA_CENTER,spaceAfter=2*mm),
      'ref':ParagraphStyle('r',fontName='Helvetica',fontSize=8.5,leading=11,textColor=MUTED),
      'body':ParagraphStyle('b',fontName='Helvetica',fontSize=9.2,leading=13.5,textColor=TEXT,spaceAfter=2.1*mm),
      'tight':ParagraphStyle('q',fontName='Helvetica',fontSize=8.7,leading=12,textColor=TEXT,spaceAfter=.8*mm),
      'head':ParagraphStyle('h',fontName='Helvetica-Bold',fontSize=9.7,leading=12,textColor=NAVY,spaceBefore=.9*mm,spaceAfter=.6*mm),
      'small':ParagraphStyle('sm',fontName='Helvetica',fontSize=7.4,leading=9,textColor=MUTED),
      'smallb':ParagraphStyle('smb',fontName='Helvetica-Bold',fontSize=7.4,leading=9,textColor=NAVY)}
    name=s(data.get('employee_name'))
    story=[Paragraph('PERFORMANCE IMPROVEMENT PLAN (PIP)',st['title'])]
    meta=Table([[Paragraph('<b>Ref. No.:</b> '+s(data.get('reference_no')),st['ref']),Paragraph('<b>Date:</b> '+fd(data.get('document_date')),st['ref'])]],colWidths=[(w-36*mm)*.58,(w-36*mm)*.42])
    meta.setStyle(TableStyle([('ALIGN',(1,0),(1,0),'RIGHT')]))
    story += [meta,Spacer(1,2*mm),Paragraph('Dear <b>'+name+'</b>,',st['body']),
              Paragraph('This Performance Improvement Plan is being issued to clearly identify the performance areas requiring improvement, define measurable expectations and provide a structured review period with appropriate management support.',st['body'])]
    rows=[
      [Paragraph('EMPLOYEE ID',st['smallb']),Paragraph('DESIGNATION',st['smallb'])],
      [Paragraph(s(data.get('login_id')),st['tight']),Paragraph(s(data.get('designation')),st['tight'])],
      [Paragraph('DEPARTMENT',st['smallb']),Paragraph('PIP PERIOD',st['smallb'])],
      [Paragraph(s(data.get('department')),st['tight']),Paragraph(fd(data.get('period_start'))+' to '+fd(data.get('period_end')),st['tight'])],
      [Paragraph('REVIEW FREQUENCY',st['smallb']),Paragraph('FINAL REVIEW DATE',st['smallb'])],
      [Paragraph(s(data.get('review_frequency'),'Weekly'),st['tight']),Paragraph(fd(data.get('review_date')),st['tight'])]
    ]
    tb=Table(rows,colWidths=[(w-36*mm)/2]*2)
    tb.setStyle(TableStyle([('BOX',(0,0),(-1,-1),.6,LINE),('INNERGRID',(0,0),(-1,-1),.35,LINE),('BACKGROUND',(0,0),(-1,0),SOFT),('BACKGROUND',(0,2),(-1,2),SOFT),('BACKGROUND',(0,4),(-1,4),SOFT),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    story += [tb,Spacer(1,1.5*mm)]
    clauses=[
      ('1. Performance Concerns',s(data.get('performance_concerns'))),
      ('2. Required Performance Standard / Expectations',s(data.get('expectations'))),
      ('3. Improvement Actions & Measurable Deliverables',s(data.get('action_plan'))),
      ('4. Support / Resources from Management',s(data.get('management_support'),'Management will provide reasonable guidance, feedback and access to the resources required to meet the stated expectations.')),
      ('5. Monitoring & Review','Progress will be reviewed '+s(data.get('review_frequency'),'weekly').lower()+'. The employee is expected to participate in review discussions and demonstrate sustained improvement throughout the PIP period.'),
      ('6. Consequence of Insufficient Improvement',s(data.get('consequence'),'Failure to demonstrate sufficient and sustained improvement during the PIP period may lead to further performance-management or disciplinary action, subject to applicable company policy and law.'))
    ]
    for head,body in clauses:
        story += [Paragraph(head,st['head']),Paragraph(body.replace('\n','<br/>'),st['tight'])]
    if s(data.get('additional_remarks'),''):
        story += [Paragraph('7. Additional Remarks',st['head']),Paragraph(s(data.get('additional_remarks')).replace('\n','<br/>'),st['tight'])]
    story += [Spacer(1,1.2*mm),Paragraph('This PIP is intended to provide a fair, documented and measurable opportunity to improve performance. It does not alter any other applicable terms of employment unless expressly stated in writing.',st['body']),Spacer(1,1.5*mm)]
    sig=Table([[Paragraph('<b>For Guru Ram Singh Ji Associates</b>',st['tight']),Paragraph('<b>Employee Acknowledgement</b>',st['tight'])],[Spacer(1,9*mm),Spacer(1,9*mm)],[Paragraph('Authorised Signatory',st['tight']),Paragraph(name,st['tight'])],[Paragraph('Name: __________________________',st['small']),Paragraph('Signature: ______________________',st['small'])],[Paragraph('Designation: ___________________',st['small']),Paragraph('Date: ___________________________',st['small'])]],colWidths=[(w-36*mm)*.52,(w-36*mm)*.48])
    sig.setStyle(TableStyle([('LINEABOVE',(0,2),(-1,2),.6,LINE),('LEFTPADDING',(0,0),(-1,-1),0)])); story.append(sig)
    doc.build(story); out.seek(0); return out
