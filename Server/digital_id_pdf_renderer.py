import base64
import mimetypes
from io import BytesIO

from playwright.sync_api import sync_playwright
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

# Standard CR80 / bank-card size used by the live Digital ID design.
CARD_W = 85.60 * mm
CARD_H = 53.98 * mm

# Browser render size with the same CR80 aspect ratio.
# A fixed render box prevents any responsive/mobile CSS from changing the
# proportions used for the downloadable PDF.
RENDER_W = 856
RENDER_H = 540


def file_to_data_uri(path):
    if not path:
        return ''
    mime = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    with open(path, 'rb') as fh:
        payload = base64.b64encode(fh.read()).decode('ascii')
    return f'data:{mime};base64,{payload}'


def svg_to_data_uri(svg):
    if svg is None:
        return ''
    if isinstance(svg, str):
        svg = svg.encode('utf-8')
    payload = base64.b64encode(svg).decode('ascii')
    return f'data:image/svg+xml;base64,{payload}'


def _draw_card_image(pdf, image_bytes):
    """Draw a rendered card on a CR80 PDF page without stretching it."""
    image = ImageReader(BytesIO(image_bytes))
    img_w, img_h = image.getSize()

    scale = min(CARD_W / img_w, CARD_H / img_h)
    draw_w = img_w * scale
    draw_h = img_h * scale
    x = (CARD_W - draw_w) / 2
    y = (CARD_H - draw_h) / 2

    pdf.drawImage(
        ImageReader(BytesIO(image_bytes)),
        0, 0,
        width=CARD_W,
        height=CARD_H,
        preserveAspectRatio=False,
        mask='auto',
    )


def build_digital_id_pdf(rendered_html):
    """Render the live master card design and export Front + Back as exact CR80 PDF pages."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context(
                viewport={"width": 1400, "height": 1000},
                device_scale_factor=2,
            )
            page = context.new_page()
            page.set_content(rendered_html, wait_until='load')

            # PDF-only sizing. This does NOT touch the live website CSS.
            # It simply renders both card faces in the same fixed CR80 ratio
            # before Chromium takes the screenshots used for the PDF.
            page.add_style_tag(content=f"""
                html, body {{
                    margin: 0 !important;
                    padding: 0 !important;
                    background: #fff !important;
                }}

                #pdfFront, #pdfBack {{
                    width: {RENDER_W}px !important;
                    height: {RENDER_H}px !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    display: block !important;
                    overflow: hidden !important;
                    background: transparent !important;
                }}

                #pdfFront .digital-id-card,
                #pdfBack .digital-id-card {{
                    position: relative !important;
                    width: {RENDER_W}px !important;
                    height: {RENDER_H}px !important;
                    min-width: {RENDER_W}px !important;
                    max-width: {RENDER_W}px !important;
                    min-height: {RENDER_H}px !important;
                    max-height: {RENDER_H}px !important;
                    aspect-ratio: auto !important;
                    margin: 0 !important;
                    transform: none !important;
                    filter: none !important;
                    cursor: default !important;
                    overflow: hidden !important;
                }}

                #pdfFront .digital-id-face,
                #pdfBack .digital-id-face {{
                    position: absolute !important;
                    inset: 0 !important;
                    width: 100% !important;
                    height: 100% !important;
                    box-sizing: border-box !important;
                    transform: none !important;
                }}

                #pdfFront .digital-id-face[hidden],
                #pdfBack .digital-id-face[hidden] {{
                    display: none !important;
                }}
            """)

            page.wait_for_timeout(250)

            front = page.locator('#pdfFront .digital-id-card')
            back = page.locator('#pdfBack .digital-id-card')

            front_png = front.screenshot(type='png', animations='disabled')
            back_png = back.screenshot(type='png', animations='disabled')
            context.close()
        finally:
            browser.close()

    out = BytesIO()
    pdf = canvas.Canvas(out, pagesize=(CARD_W, CARD_H))

    for image_bytes in (front_png, back_png):
        _draw_card_image(pdf, image_bytes)
        pdf.showPage()

    pdf.save()
    out.seek(0)
    return out
