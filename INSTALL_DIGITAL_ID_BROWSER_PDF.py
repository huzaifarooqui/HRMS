from pathlib import Path
from datetime import datetime
import shutil
import sys

ROOT = Path(__file__).resolve().parent
SERVER = ROOT / 'Server'
APP = SERVER / 'app.py'
PAGE = SERVER / 'templates' / 'employee_digital_id.html'
PARTIAL = SERVER / 'templates' / '_employee_digital_id_card.html'
PRINT_TEMPLATE = SERVER / 'templates' / 'employee_digital_id_print.html'
RENDERER = SERVER / 'digital_id_pdf_renderer.py'

required = [APP, PAGE, PARTIAL, PRINT_TEMPLATE, RENDERER]
missing = [str(p) for p in required if not p.exists()]
if missing:
    print('ERROR: Required file(s) missing:')
    for p in missing:
        print(' -', p)
    print('\nExtract this patch ZIP into the GRSJ-HRMS_v1.0_Stable root folder, then run again.')
    sys.exit(1)

stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_dir = ROOT / f'DIGITAL_ID_PDF_BACKUP_{stamp}'
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(APP, backup_dir / 'app.py')
shutil.copy2(PAGE, backup_dir / 'employee_digital_id.html')

# 1) Convert employee_digital_id.html to use the reusable master partial.
html = PAGE.read_text(encoding='utf-8')
include_line = "    {% include '_employee_digital_id_card.html' %}"
if "{% include '_employee_digital_id_card.html' %}" not in html:
    start_token = '    <div class="digital-id-card premium-white-id" id="digitalIdCard"'
    start = html.find(start_token)
    if start < 0:
        # Current master may already have no id after a partial-style refactor.
        start_token = '    <div class="digital-id-card premium-white-id"'
        start = html.find(start_token)
    end_marker = '\n    </div>\n  </div>\n  <div class="digital-id-note"'
    end = html.find(end_marker, start)
    if start < 0 or end < 0:
        print('ERROR: Could not locate the current Digital ID card block in employee_digital_id.html.')
        print('No files were patched. Backup folder:', backup_dir)
        sys.exit(1)
    end += len('\n    </div>')
    html = html[:start] + include_line + html[end:]

# Update JS selectors because ids now live on wrapper elements added below.
# We keep the current website flip behaviour by wrapping the include with ids via template replacement.
html = html.replace(include_line,
"""    <div id="digitalIdCardHost">
      {% include '_employee_digital_id_card.html' %}
    </div>""")
html = html.replace("const card  = document.getElementById('digitalIdCard');",
                    "const card  = document.querySelector('#digitalIdCardHost .digital-id-card');")
html = html.replace("const front = document.getElementById('idFront');",
                    "const front = card ? card.querySelector('.premium-id-front') : null;")
html = html.replace("const back  = document.getElementById('idBack');",
                    "const back  = card ? card.querySelector('.premium-id-back') : null;")
PAGE.write_text(html, encoding='utf-8')

# 2) Patch app.py: import browser renderer and replace only the old ReportLab-drawn download function.
app = APP.read_text(encoding='utf-8')
import_line = 'from digital_id_pdf_renderer import file_to_data_uri, svg_to_data_uri, build_digital_id_pdf\n'
anchor = 'from relieving_letter import build_relieving_letter_pdf\n'
if import_line not in app:
    if anchor not in app:
        print('ERROR: Could not locate import anchor in app.py.')
        sys.exit(1)
    app = app.replace(anchor, anchor + import_line, 1)

route_marker = "@app.route('/employee/digital-id/download')"
start = app.find(route_marker)
if start < 0:
    print('ERROR: Digital ID download route was not found in app.py.')
    sys.exit(1)
next_anchor = '\ndef offer_letter_form_data('
end = app.find(next_anchor, start)
if end < 0:
    print('ERROR: Could not determine the end of the existing Digital ID download function.')
    sys.exit(1)

new_route = r'''@app.route('/employee/digital-id/download')
@employee_required
def employee_digital_id_download():
    emp=query("SELECT e.*,d.department_name FROM employees e LEFT JOIN departments d ON d.id=e.department_id WHERE e.id=%s",(session['employee_id'],),one=True)
    if not emp:
        flash('Employee record not found.','danger')
        return redirect(url_for('employee_profile'))

    company=settings()
    verify_url=url_for('verify_employee_id',token=employee_verification_token(emp),_external=True)

    # Make the print HTML fully self-contained so Chromium does not need the employee session
    # to load the employee photo, company logo or QR image.
    logo_src=file_to_data_uri(digital_id_logo_path(company))
    photo_src=file_to_data_uri(digital_id_image_path(emp))
    qr_svg=renderSVG.drawToString(digital_id_qr_drawing(verify_url,34*mm))
    qr_src=svg_to_data_uri(qr_svg)

    css_path=os.path.join(app.static_folder,'css','app.css')
    with open(css_path,'r',encoding='utf-8') as fh:
        css_text=fh.read()

    html=render_template(
        'employee_digital_id_print.html',
        employee=emp,
        company=company,
        valid_till=digital_id_valid_till(emp.get('joining_date')),
        card_logo_src=logo_src,
        card_photo_src=photo_src,
        card_qr_src=qr_src,
        css_text=css_text,
    )

    try:
        out=build_digital_id_pdf(html)
    except Exception as exc:
        app.logger.exception('Digital ID browser PDF generation failed')
        flash(f'Unable to generate Digital ID PDF: {exc}','danger')
        return redirect(url_for('employee_digital_id'))

    filename=f"GRSJ_Digital_ID_{re.sub(r'[^A-Za-z0-9_-]+','_',str(emp.get('login_id') or emp.get('id')))}.pdf"
    return send_file(out,mimetype='application/pdf',as_attachment=True,download_name=filename)
'''

app = app[:start] + new_route + app[end:]
APP.write_text(app, encoding='utf-8')

print('\nSUCCESS: Digital ID Browser PDF patch installed.')
print('Backup created at:', backup_dir)
print('\nNext: restart the GRSJ HRMS server and test Download PDF.')
