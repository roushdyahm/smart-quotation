from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os, io, json
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, Image, HRFlowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.colors import HexColor

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB upload limit

COMPANY = {
    "name":    "Smart Global Trading Ltd",
    "contact": "Ahmed Roushdy – Sales Manager",
    "address": "Muungano House, Argwing Khodek Road, Hurlingham",
    "pobox":   "P.O. Box 66628-00800, Nairobi, Kenya",
    "mobile":  "+254 719 593252 / +254 722 206043",
    "tel":     "+254 20 3500426 / +254 773 333430",
    "email":   "ahmed@smarthotelsupplies.com",
    "web":     "www.smarthotelsupplies.com",
}
VAT_RATE   = 0.16
NAVY       = HexColor("#1B3A6B")
LIGHT_BLUE = HexColor("#E8EEF7")
LOGO_PATH  = os.path.join(os.path.dirname(__file__), "smart_logo.jpg")

# In-memory items store (uploaded by user)
items_store = []

def load_default_items():
    default = os.path.join(os.path.dirname(__file__), "items.csv")
    if os.path.exists(default):
        df = pd.read_csv(default)
        df.columns = [c.strip() for c in df.columns]
        records = []
        for _, row in df.iterrows():
            name  = str(row.iloc[0]).strip()
            price = 0.0
            unit  = "Piece"
            desc  = ""
            for col in df.columns:
                cl = col.lower()
                if "price" in cl:
                    try: price = float(str(row[col]).replace(",","").split()[0])
                    except: pass
                elif "unit" in cl and "price" not in cl:
                    unit = str(row[col])
                elif "desc" in cl:
                    desc = str(row[col])
            records.append({"name": name, "price": price, "unit": unit, "desc": desc})
        return records
    return []

items_store = load_default_items()

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/items")
def get_items():
    return jsonify(items_store)

@app.route("/api/upload-items", methods=["POST"])
def upload_items():
    global items_store
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "No file uploaded"}), 400
    try:
        if f.filename.endswith(".csv"):
            df = pd.read_csv(f)
        else:
            df = pd.read_excel(f)
        df.columns = [c.strip() for c in df.columns]
        records = []
        for _, row in df.iterrows():
            name  = str(row.iloc[0]).strip()
            price = 0.0
            unit  = "Piece"
            desc  = ""
            for col in df.columns:
                cl = col.lower()
                if "price" in cl:
                    try: price = float(str(row[col]).replace(",","").split()[0])
                    except: pass
                elif "unit" in cl and "price" not in cl:
                    unit = str(row[col])
                elif "desc" in cl:
                    desc = str(row[col])
            records.append({"name": name, "price": price, "unit": unit, "desc": desc})
        items_store = records
        return jsonify({"count": len(records), "items": records})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/generate-pdf", methods=["POST"])
def generate_pdf_route():
    data = request.get_json()
    try:
        buf = io.BytesIO()
        _build_pdf(data, buf)
        buf.seek(0)
        fname = f"Quotation_{data.get('quote_no','SG')}.pdf"
        return send_file(buf, mimetype="application/pdf",
                         as_attachment=True, download_name=fname)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def _build_pdf(qd, buf):
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=15*mm, rightMargin=15*mm,
                            topMargin=10*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    _id = [0]
    def sty(base="Normal", **kw):
        _id[0] += 1
        return ParagraphStyle(f"s{_id[0]}", parent=styles[base], **kw)

    story = []
    logo_cell = ""
    if os.path.exists(LOGO_PATH):
        try: logo_cell = Image(LOGO_PATH, width=55*mm, height=22*mm)
        except: logo_cell = Paragraph("<b>SMART</b>", sty(fontSize=20, textColor=NAVY))

    company_lines = [
        Paragraph(f"<b>{COMPANY['name']}</b>",    sty(fontSize=11, textColor=NAVY, spaceAfter=2)),
        Paragraph(COMPANY["contact"],              sty(fontSize=8.5, spaceAfter=1)),
        Paragraph(COMPANY["address"],              sty(fontSize=8, textColor=colors.grey, spaceAfter=1)),
        Paragraph(COMPANY["pobox"],                sty(fontSize=8, textColor=colors.grey, spaceAfter=1)),
        Paragraph(f"M: {COMPANY['mobile']}",       sty(fontSize=8, textColor=colors.grey, spaceAfter=1)),
        Paragraph(f"T: {COMPANY['tel']}",          sty(fontSize=8, textColor=colors.grey, spaceAfter=1)),
        Paragraph(COMPANY["email"],                sty(fontSize=8, spaceAfter=1)),
        Paragraph(COMPANY["web"],                  sty(fontSize=8)),
    ]
    ht = Table([[logo_cell, company_lines]], colWidths=[65*mm, None])
    ht.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                             ("LEFTPADDING",(0,0),(-1,-1),0),
                             ("RIGHTPADDING",(0,0),(-1,-1),0)]))
    story.append(ht)
    story.append(HRFlowable(width="100%", thickness=2, color=NAVY, spaceAfter=6))
    story.append(Paragraph("QUOTATION", sty(fontSize=16, textColor=NAVY,
                                             alignment=TA_CENTER, spaceAfter=4)))
    meta = [
        [Paragraph(f"<b>Quote No:</b> {qd['quote_no']}", sty(fontSize=9)),
         Paragraph(f"<b>Date:</b> {qd['date']}",         sty(fontSize=9, alignment=TA_RIGHT))],
        [Paragraph(f"<b>Valid Until:</b> {qd['valid_until']}", sty(fontSize=9)),
         Paragraph(f"<b>Currency:</b> {qd['currency']}",       sty(fontSize=9, alignment=TA_RIGHT))],
    ]
    mt = Table(meta, colWidths=["50%","50%"])
    mt.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),
                             ("RIGHTPADDING",(0,0),(-1,-1),0),
                             ("BOTTOMPADDING",(0,0),(-1,-1),2)]))
    story.append(mt)
    story.append(Spacer(1,4*mm))

    cust = [[Paragraph("<b>BILL TO</b>", sty(fontSize=9, textColor=NAVY))],
            [Paragraph(f"<b>{qd['customer_name']}</b>", sty(fontSize=10))]]
    for k in ["company","address","phone","email"]:
        if qd.get(k): cust.append([Paragraph(str(qd[k]), sty(fontSize=9))])
    ct = Table(cust, colWidths=["100%"])
    ct.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),LIGHT_BLUE),
                             ("BOX",(0,0),(-1,-1),0.5,NAVY),
                             ("LEFTPADDING",(0,0),(-1,-1),6),
                             ("RIGHTPADDING",(0,0),(-1,-1),6),
                             ("TOPPADDING",(0,0),(-1,-1),3),
                             ("BOTTOMPADDING",(0,0),(-1,-1),3)]))
    story.append(ct)
    story.append(Spacer(1,5*mm))

    cur = qd["currency"]
    col_w = [10*mm,75*mm,20*mm,20*mm,25*mm,25*mm]
    hdrs  = ["#","Description","Unit","Qty",f"Unit Price\n({cur})",f"Total\n({cur})"]
    rows  = [[Paragraph(f"<b>{h}</b>", sty(fontSize=8.5, textColor=colors.white,
                                           alignment=TA_CENTER)) for h in hdrs]]
    for i, item in enumerate(qd["items"], 1):
        tot = float(item["qty"]) * float(item["price"])
        rows.append([
            Paragraph(str(i),               sty(fontSize=8.5, alignment=TA_CENTER)),
            Paragraph(str(item["name"]),    sty(fontSize=8.5)),
            Paragraph(str(item["unit"]),    sty(fontSize=8.5, alignment=TA_CENTER)),
            Paragraph(str(item["qty"]),     sty(fontSize=8.5, alignment=TA_CENTER)),
            Paragraph(f"{float(item['price']):,.2f}", sty(fontSize=8.5, alignment=TA_RIGHT)),
            Paragraph(f"{tot:,.2f}",                  sty(fontSize=8.5, alignment=TA_RIGHT)),
        ])
    it = Table(rows, colWidths=col_w, repeatRows=1)
    it.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,LIGHT_BLUE]),
        ("BOX",(0,0),(-1,-1),0.5,NAVY),
        ("INNERGRID",(0,0),(-1,-1),0.25,colors.lightgrey),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
    ]))
    story.append(it)
    story.append(Spacer(1,4*mm))

    subtotal = sum(float(i["qty"])*float(i["price"]) for i in qd["items"])
    vat_amt  = subtotal * VAT_RATE
    grand    = subtotal + vat_amt
    td = [
        ["", Paragraph("<b>Sub Total:</b>",  sty(fontSize=9, alignment=TA_RIGHT)),
              Paragraph(f"{subtotal:,.2f} {cur}", sty(fontSize=9, alignment=TA_RIGHT))],
        ["", Paragraph("<b>VAT (16%):</b>",  sty(fontSize=9, alignment=TA_RIGHT)),
              Paragraph(f"{vat_amt:,.2f} {cur}",  sty(fontSize=9, alignment=TA_RIGHT))],
        ["", Paragraph("<b>TOTAL:</b>",       sty(fontSize=10, textColor=NAVY, alignment=TA_RIGHT)),
              Paragraph(f"<b>{grand:,.2f} {cur}</b>", sty(fontSize=10, textColor=NAVY, alignment=TA_RIGHT))],
    ]
    tt = Table(td, colWidths=["55%","25%","20%"])
    tt.setStyle(TableStyle([
        ("BACKGROUND",(1,2),(-1,2),LIGHT_BLUE),
        ("BOX",(1,0),(-1,-1),0.5,NAVY),
        ("INNERGRID",(1,0),(-1,-1),0.25,colors.lightgrey),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LINEABOVE",(1,2),(-1,2),1,NAVY),
    ]))
    story.append(tt)

    if qd.get("notes"):
        story.append(Spacer(1,5*mm))
        story.append(HRFlowable(width="100%",thickness=0.5,color=NAVY))
        story.append(Paragraph("<b>Notes / Terms & Conditions:</b>",
                                sty(fontSize=9, textColor=NAVY, spaceBefore=4)))
        story.append(Paragraph(qd["notes"].replace("\n","<br/>"),
                                sty(fontSize=8.5, spaceAfter=4)))

    story.append(Spacer(1,6*mm))
    story.append(HRFlowable(width="100%",thickness=1,color=NAVY))
    story.append(Paragraph(
        f"Thank you for your business! | {COMPANY['email']} | {COMPANY['web']}",
        sty(fontSize=7.5, textColor=colors.grey, alignment=TA_CENTER, spaceBefore=3)
    ))
    doc.build(story)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
