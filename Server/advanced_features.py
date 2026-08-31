"""GRSJ HRMS v1.2 Advanced Intelligence & Automation Pack.
Adds enterprise-style command center, employee 360, deterministic HR assistant,
automation rules, payroll ledger (no overtime), scheduled-report configuration,
security hardening hooks, health insights and richer audit context.
"""
import os, re, calendar
from datetime import datetime, date, timedelta
from functools import wraps
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash


def register_advanced_features(app, query, admin_required, role_required, current_admin_role, audit_log, settings):
    # Lightweight in-process login throttle. It is deliberately conservative and resets after a short window.
    login_attempts = {}
    WINDOW = 10 * 60
    MAX_FAILS = 8

    def record_security(event_type, details=''):
        try:
            query("INSERT INTO security_events(event_type,admin_id,ip_address,user_agent,details) VALUES(%s,%s,%s,%s,%s)",
                  (event_type, session.get('admin_id'), request.remote_addr, (request.headers.get('User-Agent') or '')[:500], details[:500]), commit=True)
        except Exception:
            pass

    def score_employee(eid):
        emp = query("SELECT id,first_name,last_name,joining_date,status,employment_stage FROM employees WHERE id=%s", (eid,), one=True) or {}
        month = date.today().strftime('%Y-%m')
        a = query("""SELECT COUNT(*) total,SUM(status='Present') present,SUM(status='Late') late,
                            SUM(status='Half Day') half_day,SUM(status='Absent') absent
                     FROM attendance WHERE employee_id=%s AND DATE_FORMAT(attendance_date,'%%Y-%%m')=%s""", (eid, month), one=True) or {}
        total = int(a.get('total') or 0); present=int(a.get('present') or 0); late=int(a.get('late') or 0); half=int(a.get('half_day') or 0); absent=int(a.get('absent') or 0)
        docs = query("""SELECT COUNT(*) total,SUM(expiry_date IS NOT NULL AND expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(),INTERVAL 30 DAY)) expiring
                        FROM employee_documents WHERE employee_id=%s AND COALESCE(document_status,'Active')<>'Deleted'""", (eid,), one=True) or {}
        score = None if total == 0 else 100
        if score is not None: score -= min(late * 2, 20)
        if score is not None: score -= min(absent * 4, 24)
        if score is not None: score -= min(half * 2, 10)
        if score is not None and total and (present / total) < .8: score -= 15
        if score is not None and int(docs.get('expiring') or 0): score -= 5
        if score is not None: score=max(0,min(100,score))
        band='No attendance data' if score is None else ('Excellent' if score>=90 else 'Good' if score>=75 else 'Needs Attention' if score>=60 else 'Critical Review')
        return {'score':score,'band':band,'total':total,'present':present,'late':late,'half_day':half,'absent':absent,'doc_expiring':int(docs.get('expiring') or 0),'employee':emp}

    @app.route('/admin/command-center')
    @admin_required
    def admin_command_center():
        month=date.today().strftime('%Y-%m')
        active=int((query("SELECT COUNT(*) c FROM employees WHERE status='Active'",one=True) or {}).get('c') or 0)
        today=query("""SELECT COUNT(*) total,SUM(status='Present') present,SUM(status='Late') late,SUM(status='Half Day') half_day,SUM(status='Absent') absent
                       FROM attendance WHERE attendance_date=CURDATE()""",one=True) or {}
        pending=int((query("SELECT COUNT(*) c FROM approval_requests WHERE status='Pending'",one=True) or {}).get('c') or 0)
        docs=int((query("SELECT COUNT(*) c FROM employee_documents WHERE COALESCE(document_status,'Active')<>'Deleted' AND expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(),INTERVAL 30 DAY)",one=True) or {}).get('c') or 0)
        feedback=int((query("SELECT COUNT(*) c FROM employee_feedback WHERE status='New'",one=True) or {}).get('c') or 0)
        open_cases=int((query("SELECT COUNT(*) c FROM hr_cases WHERE status='Open'",one=True) or {}).get('c') or 0)
        upcoming=query("SELECT holiday_name,holiday_date FROM holidays WHERE status='Active' AND holiday_date>=CURDATE() ORDER BY holiday_date LIMIT 5")
        birthdays=query("SELECT id,first_name,last_name,dob FROM employees WHERE status='Active' AND dob IS NOT NULL AND DATE_FORMAT(dob,'%%m-%%d') BETWEEN DATE_FORMAT(CURDATE(),'%%m-%%d') AND DATE_FORMAT(DATE_ADD(CURDATE(),INTERVAL 30 DAY),'%%m-%%d') ORDER BY DATE_FORMAT(dob,'%%m-%%d') LIMIT 8")
        top=query("SELECT id FROM employees WHERE status='Active' ORDER BY first_name LIMIT 30")
        scores=[score_employee(r['id']) for r in top]
        # Use the exact same attendance scoring inputs as the Employee Dashboard leaderboard.
        leaderboard=query("""SELECT e.id,e.login_id,CONCAT(e.first_name,' ',COALESCE(e.last_name,'')) employee_name,e.photo,
                              COUNT(a.id) marked,SUM(a.status='Present') on_time,SUM(a.status='Late') late,
                              SUM(a.status='Half Day') half_days,
                              ROUND(COALESCE(SUM(CASE a.status WHEN 'Present' THEN 100 WHEN 'Late' THEN 80 WHEN 'Half Day' THEN 50 WHEN 'Holiday' THEN 100 ELSE 0 END)/NULLIF(COUNT(a.id),0),0),1) score
                       FROM employees e LEFT JOIN attendance a ON a.employee_id=e.id AND DATE_FORMAT(a.attendance_date,'%%Y-%%m')=%s
                       WHERE e.status='Active' GROUP BY e.id ORDER BY score DESC,on_time DESC,late ASC,employee_name LIMIT 30""",(month,))
        lb={r['id']:r for r in leaderboard}
        for item in scores:
            row=lb.get(item['employee']['id']) or {}
            item['marked']=int(row.get('marked') or 0)
            item['on_time']=int(row.get('on_time') or 0)
            item['late']=int(row.get('late') or 0)
            item['half_days']=int(row.get('half_days') or 0)
            item['score']=float(row.get('score')) if row.get('score') is not None and int(row.get('marked') or 0) else None
            item['band']='No attendance data' if not item['marked'] else item['band']
        scores.sort(key=lambda x:(x['marked']==0, x['score'] if x['score'] is not None else 999))
        attention=scores[:6]
        return render_template('admin_command_center.html',active=active,today=date.today(),attendance_today=today,pending=pending,docs=docs,feedback=feedback,open_cases=open_cases,upcoming=upcoming,birthdays=birthdays,attention=attention,month=month)

    def _safe_hr_context(question):
        q=question.strip()
        l=q.lower()
        ctx=[]
        # Employee-specific attendance context for natural language HR questions.
        candidate=None
        # Match against real employee names instead of trying to parse every language with regex.
        for e in query("SELECT id,first_name,last_name,designation FROM employees WHERE status='Active' ORDER BY CHAR_LENGTH(CONCAT(first_name,' ',COALESCE(last_name,''))) DESC"):
            full=((e.get('first_name') or '')+' '+(e.get('last_name') or '')).strip()
            if full and full.casefold() in q.casefold():
                candidate=e; break
        if candidate and any(k in l for k in ('late','tardy','delay','der','late hua','late aaya','late ayi')):
            rows=query("SELECT attendance_date,late_minutes,status FROM attendance WHERE employee_id=%s AND DATE_FORMAT(attendance_date,'%%Y-%%m')=%s AND (status='Late' OR COALESCE(late_minutes,0)>0) ORDER BY attendance_date",(candidate['id'],date.today().strftime('%Y-%m')))
            ctx.append({'type':'employee_late_records','employee':(candidate.get('first_name') or '')+' '+(candidate.get('last_name') or ''),'month':date.today().strftime('%B %Y'),'late_days':len(rows),'records':[{'date':str(r['attendance_date']),'late_minutes':int(r.get('late_minutes') or 0),'status':r.get('status')} for r in rows]})
        if any(k in l for k in ('birthday','birthdays','janamdin','cumple','anniversaire','geburtstag')):
            ctx.append({'type':'birthdays','people':dashboard_birthdays(True)})
        if any(k in l for k in ('pending','approval')):
            ctx.append({'type':'pending_approvals','rows':query("SELECT title,current_stage,status,created_at FROM approval_requests WHERE status='Pending' ORDER BY created_at LIMIT 20")})
        if any(k in l for k in ('document','expire','expiry')):
            ctx.append({'type':'expiring_documents','rows':query("SELECT CONCAT(e.first_name,' ',COALESCE(e.last_name,'')) employee_name,ed.title,ed.expiry_date FROM employee_documents ed JOIN employees e ON e.id=ed.employee_id WHERE ed.expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(),INTERVAL 60 DAY) AND COALESCE(ed.document_status,'Active')<>'Deleted' ORDER BY ed.expiry_date LIMIT 20")})
        if any(k in l for k in ('absent','absence')):
            ctx.append({'type':'absent_summary','rows':query("SELECT CONCAT(e.first_name,' ',COALESCE(e.last_name,'')) employee_name,COUNT(*) total FROM attendance a JOIN employees e ON e.id=a.employee_id WHERE a.status='Absent' AND DATE_FORMAT(a.attendance_date,'%%Y-%%m')=%s GROUP BY a.employee_id ORDER BY total DESC LIMIT 20",(date.today().strftime('%Y-%m'),))})
        return ctx

    def _call_general_ai(question, context):
        import urllib.request, urllib.error, json as _json
        key=os.getenv('OPENAI_API_KEY','').strip()
        if not key: return None
        model=os.getenv('OPENAI_MODEL','gpt-5-mini').strip()
        system=("You are Ask GRSJ AI, the private intelligent assistant inside GRSJ HRMS. "
                "Understand and reply in the user's language automatically (Hindi, Hinglish, Urdu, English and other languages). "
                "Be concise but useful. You can explain concepts, troubleshoot software/HRMS issues, draft messages and documents, "
                "and answer HR questions using the supplied live HRMS context. Never invent company data. If data is unavailable, say so. "
                "Protect confidential information and only reveal HR data appropriate for the logged-in admin. Do not claim to have performed an action unless it was actually performed.")
        payload={'model':model,'messages':[{'role':'system','content':system},{'role':'user','content':question+'\n\nLIVE HRMS CONTEXT (use only if relevant):\n'+_json.dumps(context,default=str,ensure_ascii=False)}],'temperature':0.2}
        req=urllib.request.Request('https://api.openai.com/v1/chat/completions',data=_json.dumps(payload).encode('utf-8'),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
        try:
            with urllib.request.urlopen(req,timeout=25) as r:
                obj=_json.loads(r.read().decode('utf-8')); return obj['choices'][0]['message']['content'].strip()
        except Exception:
            return None

    @app.route('/admin/ask-grsj', methods=['GET','POST'])
    @admin_required
    def admin_ask_grsj():
        q=(request.values.get('q') or '').strip()
        answer=None; data=[]; context=[]
        if q:
            context=_safe_hr_context(q)
            # Deterministic answers keep core HR questions working even without an AI API key.
            if context and context[0].get('type')=='employee_late_records':
                c=context[0]; answer=f"{c['employee'].strip()} was late on {c['late_days']} day{'s' if c['late_days']!=1 else ''} in {c['month']}."; data=[{'date':r['date'],'late_minutes':r['late_minutes'],'status':r['status']} for r in c['records']]
            elif context and context[0].get('type')=='birthdays':
                people=context[0]['people']; answer="Today's birthdays: "+', '.join(p['name'] for p in people if p['days_until']==0) if any(p['days_until']==0 for p in people) else 'No birthday falls today. Upcoming: '+', '.join(f"{p['name']} in {p['days_until']} days" for p in people[:6])
            elif context and context[0].get('type')=='pending_approvals':
                data=context[0]['rows']; answer=f"There are {len(data)} pending approval request{'s' if len(data)!=1 else ''}."
            elif context and context[0].get('type')=='expiring_documents':
                data=context[0]['rows']; answer=f"I found {len(data)} document record{'s' if len(data)!=1 else ''} expiring within the next 60 days."
            elif context and context[0].get('type')=='absent_summary':
                data=context[0]['rows']; answer=f"Here is the absence summary for {date.today():%B %Y}."
            else:
                answer=_call_general_ai(q,context)
                if answer is None: answer="I can answer general questions and GRSJ HRMS questions, but the general AI agent is not connected yet. Add OPENAI_API_KEY to the server environment to enable full multilingual AI assistance."
        return render_template('admin_ask_grsj.html',q=q,answer=answer,data=data)

    @app.route('/admin/employees/<int:eid>/360')
    @admin_required
    def employee_360(eid):
        emp=query("""SELECT e.*,d.department_name FROM employees e LEFT JOIN departments d ON d.id=e.department_id WHERE e.id=%s""",(eid,),one=True)
        if not emp:return ('Not found',404)
        score=score_employee(eid)
        docs=query("SELECT * FROM employee_documents WHERE employee_id=%s AND COALESCE(document_status,'Active')<>'Deleted' ORDER BY uploaded_at DESC",(eid,))
        leaves=query("SELECT * FROM leave_requests WHERE employee_id=%s ORDER BY created_at DESC LIMIT 10",(eid,))
        attendance=query("SELECT attendance_date,status,check_in,check_out,late_minutes FROM attendance WHERE employee_id=%s ORDER BY attendance_date DESC LIMIT 12",(eid,))
        cases=query("SELECT case_no,case_type,title,severity,status,created_at FROM hr_cases WHERE employee_id=%s ORDER BY created_at DESC LIMIT 10",(eid,))
        lifecycle=query("SELECT event_type,title,effective_date,details FROM employee_lifecycle WHERE employee_id=%s ORDER BY effective_date DESC,id DESC LIMIT 15",(eid,))
        assets=query("SELECT asset_type,asset_name,status,issue_date,return_date FROM employee_assets WHERE employee_id=%s ORDER BY created_at DESC LIMIT 10",(eid,))
        return render_template('employee_360.html',employee=emp,score=score,docs=docs,leaves=leaves,attendance=attendance,cases=cases,lifecycle=lifecycle,assets=assets)

    @app.route('/admin/workforce-map')
    @admin_required
    def admin_workforce_map():
        rows=query("""SELECT a.employee_id,a.status,a.check_in,a.check_in_lat,a.check_in_lng,CONCAT(e.first_name,' ',COALESCE(e.last_name,'')) employee_name,e.designation
                         FROM attendance a JOIN employees e ON e.id=a.employee_id
                         WHERE a.attendance_date=CURDATE() AND a.check_in_lat IS NOT NULL AND a.check_in_lng IS NOT NULL
                         ORDER BY a.check_in""")
        points=[{'name':r['employee_name'],'designation':r.get('designation') or 'Employee','status':r.get('status'),'check_in':str(r.get('check_in') or ''),'lat':float(r['check_in_lat']),'lng':float(r['check_in_lng'])} for r in rows]
        return render_template('admin_workforce_map.html',points=points)

    @app.route('/admin/automation', methods=['GET','POST'])
    @admin_required
    @role_required('Super Admin','Owner','HR')
    def admin_automation():
        if request.method=='POST':
            f=request.form
            action=f.get('action','create')
            try:
                if action=='toggle':
                    query("UPDATE automation_rules SET is_active=1-is_active WHERE id=%s",(int(f.get('rule_id')),),commit=True)
                else:
                    query("INSERT INTO automation_rules(name,trigger_type,threshold_value,action_type,action_message,is_active,created_by) VALUES(%s,%s,%s,%s,%s,1,%s)",(f.get('name'),f.get('trigger_type'),int(f.get('threshold_value') or 0),f.get('action_type'),(f.get('action_message') or '')[:500],session['admin_id']),commit=True)
                audit_log('UPDATE_AUTOMATION_RULE','AutomationRule',None,{'action':action});flash('Automation rule updated.','success')
            except Exception as e:flash(f'Automation update failed: {e}','danger')
            return redirect(url_for('admin_automation'))
        rules=query("SELECT r.*,a.full_name FROM automation_rules r LEFT JOIN admins a ON a.id=r.created_by ORDER BY r.is_active DESC,r.created_at DESC")
        schedules=query("SELECT * FROM scheduled_reports ORDER BY is_active DESC,created_at DESC")
        return render_template('admin_automation.html',rules=rules,schedules=schedules)

    @app.route('/admin/automation/schedule', methods=['POST'])
    @admin_required
    @role_required('Super Admin','Owner','HR')
    def admin_schedule_report():
        f=request.form
        query("INSERT INTO scheduled_reports(name,report_type,frequency,day_of_month,day_of_week,recipient_role,is_active,created_by) VALUES(%s,%s,%s,NULLIF(%s,''),NULLIF(%s,''),%s,1,%s)",(f.get('name'),f.get('report_type'),f.get('frequency'),f.get('day_of_month',''),f.get('day_of_week',''),f.get('recipient_role','HR'),session['admin_id']),commit=True)
        audit_log('CREATE_SCHEDULED_REPORT','ScheduledReport');flash('Scheduled report rule saved.','success');return redirect(url_for('admin_automation'))

    @app.route('/admin/payroll')
    @admin_required
    @role_required('Super Admin','Owner','HR')
    def admin_payroll():
        month=(request.args.get('month') or date.today().strftime('%Y-%m'))[:7]
        rows=query("""SELECT p.*,CONCAT(e.first_name,' ',COALESCE(e.last_name,'')) employee_name,e.login_id,e.designation
                     FROM payroll_records p JOIN employees e ON e.id=p.employee_id WHERE p.salary_month=%s ORDER BY e.first_name""",(month,))
        return render_template('admin_payroll.html',month=month,rows=rows)

    @app.post('/admin/payroll/generate')
    @admin_required
    @role_required('Super Admin','Owner','HR')
    def admin_payroll_generate():
        month=(request.form.get('month') or date.today().strftime('%Y-%m'))[:7]
        try: year,mon=map(int,month.split('-'))
        except: flash('Invalid payroll month.','danger'); return redirect(url_for('admin_payroll',month=month))
        total_days=calendar.monthrange(year,mon)[1]; start=date(year,mon,1); end=date(year,mon,total_days)
        emps=query("SELECT * FROM employees WHERE status='Active' ORDER BY first_name")
        for e in emps:
            rows=query("SELECT status FROM attendance WHERE employee_id=%s AND attendance_date BETWEEN %s AND %s",(e['id'],start,end))
            present=sum(r['status']=='Present' for r in rows);late=sum(r['status']=='Late' for r in rows);half=sum(r['status']=='Half Day' for r in rows);absent=sum(r['status']=='Absent' for r in rows)
            holidays=sum(r['status']=='Holiday' for r in rows)
            groups3,rem=divmod(late,3); late_credit=groups3*2.0+(1.5 if rem==2 else 1.0 if rem==1 else 0.0)
            final_days=present+holidays+half*.5+late_credit
            gross=float(e.get('salary') or 0); earned=gross/total_days*final_days if total_days else 0
            query("""INSERT INTO payroll_records(employee_id,salary_month,total_days,present_days,late_days,half_days,absent_days,final_days,gross_salary,net_salary,status,generated_by)
                      VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'Draft',%s)
                      ON DUPLICATE KEY UPDATE total_days=VALUES(total_days),present_days=VALUES(present_days),late_days=VALUES(late_days),half_days=VALUES(half_days),absent_days=VALUES(absent_days),final_days=VALUES(final_days),gross_salary=VALUES(gross_salary),net_salary=VALUES(net_salary),generated_by=VALUES(generated_by),generated_at=CURRENT_TIMESTAMP""",
                  (e['id'],month,total_days,present,late,half,absent,final_days,gross,earned,session['admin_id']),commit=True)
        audit_log('GENERATE_PAYROLL','Payroll',None,{'month':month,'overtime_included':False});flash(f'Payroll ledger generated for {month}. No overtime calculation is included.','success');return redirect(url_for('admin_payroll',month=month))

    @app.post('/admin/system-health/verify-backup')
    @admin_required
    def verify_backup():
        root=os.path.join(app.config.get('DATA_ROOT',os.path.dirname(__file__)),'backups')
        files=[]
        if os.path.isdir(root):
            for dp,_,fn in os.walk(root):
                for n in fn:
                    path=os.path.join(dp,n)
                    if os.path.isfile(path):files.append((path,os.path.getsize(path)))
        ok=bool(files and any(size>0 for _,size in files))
        audit_log('VERIFY_BACKUP','System',None,{'files':len(files),'ok':ok})
        flash('Backup verification passed: usable non-empty backup files found.' if ok else 'Backup verification could not confirm a usable backup.','success' if ok else 'danger')
        return redirect(url_for('admin_system_health'))

    @app.route('/service-worker.js')
    def service_worker():
        from flask import Response
        js = '''const CACHE='grsj-static-v1';
const ASSETS=['/static/css/app.css','/static/js/app.js','/static/icons/icon-192.png','/static/icons/icon-512.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{const u=new URL(e.request.url); if(e.request.method!=='GET'||u.origin!==location.origin||!u.pathname.startsWith('/static/')) return; e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(x=>{const copy=x.clone();caches.open(CACHE).then(c=>c.put(e.request,copy));return x}).catch(()=>r)));});'''
        return Response(js,mimetype='application/javascript')

    @app.before_request
    def login_throttle_guard():
        if request.path=='/admin/login' and request.method=='POST':
            key=request.remote_addr or 'unknown'; now=datetime.utcnow().timestamp(); vals=[t for t in login_attempts.get(key,[]) if now-t<WINDOW]; login_attempts[key]=vals
            if len(vals)>=MAX_FAILS:
                from flask import make_response
                return make_response('Too many failed login attempts. Please wait a few minutes and try again.',429)

    def automation_tick():
        try:
            rules=query("SELECT * FROM automation_rules WHERE is_active=1")
            for r in rules:
                trig=r.get('trigger_type'); threshold=int(r.get('threshold_value') or 0)
                hit=False; detail=''
                if trig=='Late Count':
                    row=query("SELECT COUNT(*) c FROM attendance WHERE status='Late' AND attendance_date>=DATE_SUB(CURDATE(),INTERVAL 30 DAY)",one=True); val=int((row or {}).get('c') or 0); hit=val>=threshold; detail=f'{val} late records in the last 30 days.'
                elif trig=='Document Expiry':
                    row=query("SELECT COUNT(*) c FROM employee_documents WHERE COALESCE(document_status,'Active')<>'Deleted' AND expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(),INTERVAL 30 DAY)",one=True); val=int((row or {}).get('c') or 0); hit=val>=threshold; detail=f'{val} documents expire within 30 days.'
                elif trig=='Pending Approval':
                    row=query("SELECT COUNT(*) c FROM approval_requests WHERE status='Pending'",one=True); val=int((row or {}).get('c') or 0); hit=val>=threshold; detail=f'{val} approvals are pending.'
                elif trig=='Feedback':
                    row=query("SELECT COUNT(*) c FROM employee_feedback WHERE status='New'",one=True); val=int((row or {}).get('c') or 0); hit=val>=threshold; detail=f'{val} new feedback items are waiting.'
                elif trig=='Backup Check':
                    root=os.path.join(app.config.get('DATA_ROOT',os.path.dirname(__file__)),'backups'); hit=not os.path.isdir(root) or not any(os.path.getsize(os.path.join(dp,n))>0 for dp,_,fn in os.walk(root) for n in fn if os.path.isfile(os.path.join(dp,n))); detail='No usable non-empty backup file was detected.'
                if hit:
                    recent=query("SELECT id FROM admin_notifications WHERE title=%s AND created_at>=DATE_SUB(NOW(),INTERVAL 24 HOUR) LIMIT 1",(r['name'],),one=True)
                    if not recent:
                        role='All' if r.get('action_type')=='Notify HR' else ('Manager' if r.get('action_type')=='Notify Manager' else 'All')
                        msg=((r.get('action_message') or 'Automation rule triggered.')+' '+detail)[:500]
                        query("INSERT INTO admin_notifications(admin_role,title,message,notification_type) VALUES(%s,%s,%s,'Automation')",(role,r['name'],msg),commit=True)
                        audit_log('AUTOMATION_TRIGGER','AutomationRule',r['id'],{'trigger':trig,'detail':detail})
        except Exception:
            pass
    app.config['_automation_tick']=automation_tick

    # Security headers on every response; safe for the existing server-rendered UI.
    @app.after_request
    def security_headers(response):
        # Record failed admin login responses and temporarily throttle abusive clients.
        if request.path=='/admin/login' and request.method=='POST' and response.status_code==200:
            key=request.remote_addr or 'unknown'; now=datetime.utcnow().timestamp(); old=login_attempts.get(key,[]); old=[t for t in old if now-t<WINDOW]; old.append(now); login_attempts[key]=old
            if len(old)>=MAX_FAILS:
                record_security('LOGIN_THROTTLE',f'Failed admin login threshold reached from {key}')
        response.headers.setdefault('X-Content-Type-Options','nosniff')
        response.headers.setdefault('X-Frame-Options','SAMEORIGIN')
        response.headers.setdefault('Referrer-Policy','strict-origin-when-cross-origin')
        response.headers.setdefault('Permissions-Policy','geolocation=(self),camera=(self),microphone=()')
        response.headers.setdefault('Cache-Control','no-store' if request.path.startswith(('/admin','/employee','/api')) else 'public, max-age=300')
        return response

    return {'score_employee':score_employee}
