GRSJ HRMS - DIGITAL ID BROWSER PDF PATCH

PURPOSE
- Makes the downloaded Digital ID PDF use the same master HTML/CSS card design as the website.
- Front and Back are captured by Chromium using Playwright.
- The PDF contains 2 pages: Front and Back.
- ReportLab is used only to package the two browser-rendered card images into exact CR80 ID-card sized PDF pages.

INSTALL
1. Extract this ZIP directly into your current GRSJ-HRMS_v1.0_Stable folder.
   After extraction you should see:
     GRSJ-HRMS_v1.0_Stable\INSTALL_DIGITAL_ID_BROWSER_PDF.bat
     GRSJ-HRMS_v1.0_Stable\Server\digital_id_pdf_renderer.py
     GRSJ-HRMS_v1.0_Stable\Server\templates\_employee_digital_id_card.html
     GRSJ-HRMS_v1.0_Stable\Server\templates\employee_digital_id_print.html

2. Double-click INSTALL_DIGITAL_ID_BROWSER_PDF.bat

3. The installer automatically backs up app.py and employee_digital_id.html before changing them.

4. Restart GRSJ HRMS server.

5. Login as an employee, open Digital ID Card and click Download PDF.

NOTE
Playwright and Chromium must already be installed in the project venv. This package assumes the earlier installation step has been completed.
