from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.utils import ImageReader
PAGE=(545.979,802.143); NAVY=colors.HexColor("#102A53"); GOLD=colors.HexColor("#A47B2C"); TEXT=colors.HexColor("#222B38"); MUTED=colors.HexColor("#5F6B7A"); LINE=colors.HexColor("#D8DEE8"); SOFT=colors.HexColor("#F6F8FB")
def s(v,d="-"):
    x=str(v or "").strip(); return x if x else d
def fd(v):
    try:return datetime.strptime(str(v)[:10],"%Y-%m-%d").strftime("%d %B %Y")
    except:return s(v)
def build_warning_letter_pdf(data,bgpath):
    out=BytesIO();w,h=PAGE
    doc=BaseDocTemplate(out,pagesize=PAGE,leftMargin=18*mm,rightMargin=18*mm,topMargin=44*mm,bottomMargin=18*mm,title="Warning Letter - "+s(data.get("employee_name")))
    bg=ImageReader(str(bgpath))
    def onpage(c,d):
        c.saveState();c.drawImage(bg,0,0,width=w,height=h,mask="auto");c.setFillColor(GOLD);c.setFont("Helvetica-Bold",7);c.drawRightString(w-18*mm,12*mm,f"Page {d.page}");c.restoreState()
    doc.addPageTemplates(PageTemplate(id="p",frames=[Frame(18*mm,18*mm,w-36*mm,h-62*mm,id="f")],onPage=onpage))
    st={
    "title":ParagraphStyle("t",fontName="Helvetica-Bold",fontSize=15,leading=18,textColor=NAVY,alignment=TA_CENTER,spaceAfter=2*mm),
    "ref":ParagraphStyle("r",fontName="Helvetica",fontSize=8.5,leading=11,textColor=MUTED),
    "body":ParagraphStyle("b",fontName="Helvetica",fontSize=9.2,leading=13.5,textColor=TEXT,spaceAfter=2.1*mm),
    "tight":ParagraphStyle("q",fontName="Helvetica",fontSize=8.7,leading=12,textColor=TEXT,spaceAfter=.8*mm),
    "head":ParagraphStyle("h",fontName="Helvetica-Bold",fontSize=9.7,leading=12,textColor=NAVY,spaceBefore=.9*mm,spaceAfter=.6*mm),
    "small":ParagraphStyle("sm",fontName="Helvetica",fontSize=7.4,leading=9,textColor=MUTED),
    "smallb":ParagraphStyle("smb",fontName="Helvetica-Bold",fontSize=7.4,leading=9,textColor=NAVY)}
    name=s(data.get("employee_name")); level=s(data.get("warning_level"),"Written Warning"); subject=s(data.get("warning_subject"))
    deadline=fd(data.get("improvement_deadline")) if data.get("improvement_deadline") else "Immediate and ongoing"
    story=[Paragraph("FORMAL WARNING LETTER",st["title"])]
    meta=Table([[Paragraph("<b>Ref. No.:</b> "+s(data.get("reference_no")),st["ref"]),Paragraph("<b>Date:</b> "+fd(data.get("document_date")),st["ref"])]],colWidths=[(w-36*mm)*.58,(w-36*mm)*.42])
    meta.setStyle(TableStyle([("ALIGN",(1,0),(1,0),"RIGHT")]))
    story += [meta,Spacer(1,2*mm),Paragraph("Dear <b>"+name+"</b>,",st["body"]),
      Paragraph("This letter serves as a <b>"+level+"</b> regarding <b>"+subject+"</b>. Its purpose is to formally record the concern, clarify the expected standard, and provide an opportunity for immediate and sustained improvement.",st["body"])]
    rows=[[Paragraph("EMPLOYEE ID",st["smallb"]),Paragraph("DESIGNATION",st["smallb"])],[Paragraph(s(data.get("login_id")),st["tight"]),Paragraph(s(data.get("designation")),st["tight"])],
      [Paragraph("DEPARTMENT",st["smallb"]),Paragraph("WARNING LEVEL",st["smallb"])],[Paragraph(s(data.get("department")),st["tight"]),Paragraph(level,st["tight"])],
      [Paragraph("INCIDENT / REVIEW DATE",st["smallb"]),Paragraph("IMPROVEMENT BY",st["smallb"])],[Paragraph(fd(data.get("incident_date")),st["tight"]),Paragraph(deadline,st["tight"])]]
    tb=Table(rows,colWidths=[(w-36*mm)/2]*2)
    tb.setStyle(TableStyle([("BOX",(0,0),(-1,-1),.6,LINE),("INNERGRID",(0,0),(-1,-1),.35,LINE),("BACKGROUND",(0,0),(-1,0),SOFT),("BACKGROUND",(0,2),(-1,2),SOFT),("BACKGROUND",(0,4),(-1,4),SOFT),("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
    story += [tb,Spacer(1,1.5*mm)]
    clauses=[("1. Concern / Incident",s(data.get("incident_details"))),("2. Required Corrective Action",s(data.get("corrective_action"))),
      ("3. Improvement Period","You are expected to demonstrate the required improvement by <b>"+deadline+"</b> and maintain the expected standard thereafter. Management may review progress during or after this period."),
      ("4. Further Action",s(data.get("consequence"),"Failure to demonstrate the required improvement, or recurrence of similar conduct, may result in further disciplinary action in accordance with applicable company policy and law.")),
      ("5. Professional Conduct","You are expected to comply with applicable company rules, instructions, workplace standards and lawful directions, and to maintain professional conduct while carrying out your responsibilities.")]
    for h1,b in clauses:story += [Paragraph(h1,st["head"]),Paragraph(b,st["tight"])]
    if s(data.get("additional_remarks"),""):story += [Paragraph("6. Additional Remarks",st["head"]),Paragraph(s(data.get("additional_remarks")).replace("\n","<br/>"),st["tight"])]
    story += [Spacer(1,.8*mm),Paragraph("We expect you to treat this warning seriously and take the necessary corrective steps. Guru Ram Singh Ji Associates remains committed to maintaining clear standards and a professional workplace.",st["body"]),Spacer(1,1.5*mm)]
    sig=Table([[Paragraph("<b>For Guru Ram Singh Ji Associates</b>",st["tight"]),Paragraph("<b>Employee Acknowledgement</b>",st["tight"])],[Spacer(1,9*mm),Spacer(1,9*mm)],[Paragraph("Authorised Signatory",st["tight"]),Paragraph(name,st["tight"])],[Paragraph("Name: __________________________",st["small"]),Paragraph("Signature: ______________________",st["small"])],[Paragraph("Designation: ___________________",st["small"]),Paragraph("Date: ___________________________",st["small"])]],colWidths=[(w-36*mm)*.52,(w-36*mm)*.48])
    sig.setStyle(TableStyle([("LINEABOVE",(0,2),(-1,2),.6,LINE),("LEFTPADDING",(0,0),(-1,-1),0)]));story.append(sig)
    doc.build(story);out.seek(0);return out
