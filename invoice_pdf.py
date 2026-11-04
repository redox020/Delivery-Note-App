"""Invoice PDF builder for PDH & NAS Enterprise (pure functions, no Streamlit)."""
from decimal import Decimal, ROUND_HALF_UP

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from fpdf.fonts import FontFace

# ---------------------------------------------------------
# Fixed company details (change here if they ever change)
# ---------------------------------------------------------
COMPANY_NAME = "PDH & NAS ENTERPRISE"
COMPANY_REG = "R52343/2025"
COMPANY_ADDR = ["Lot 5, Blok R, Tingkat Bawah", "Bandar Ramai-Ramai ,Jalan Leila"]
COMPANY_CITY = ("90000 Sandakan,", "SABAH")
COMPANY_PHONE = "Hp: 014-9583177"

BANK_ACCOUNT_NAME = "PDH & NAS ENTERPRISE"
BANK_ACCOUNT_NO = "10030000560710"
BANK_NAME = "BANK MUAMALAT"

MALAY_MONTHS = ["JANUARI", "FEBRUARI", "MAC", "APRIL", "MEI", "JUN", "JULAI",
                "OGOS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DISEMBER"]

_ONES = ["", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh",
         "lapan", "sembilan", "sepuluh", "sebelas"]


def malay_date(d):
    return f"{d.day:02d} {MALAY_MONTHS[d.month - 1]} {d.year}"


def _words(n):
    """Integer -> Malay words (lowercase), n >= 1."""
    if n < 12:
        return _ONES[n]
    if n < 20:
        return _ONES[n - 10] + " belas"
    if n < 100:
        rest = _ONES[n % 10]
        return _ONES[n // 10] + " puluh" + (" " + rest if rest else "")
    if n < 1000:
        head = "seratus" if n < 200 else _ONES[n // 100] + " ratus"
        rest = _words(n % 100) if n % 100 else ""
        return head + (" " + rest if rest else "")
    if n < 1_000_000:
        head = "seribu" if n < 2000 else _words(n // 1000) + " ribu"
        rest = _words(n % 1000) if n % 1000 else ""
        return head + (" " + rest if rest else "")
    if n < 1_000_000_000:
        head = _words(n // 1_000_000) + " juta"
        rest = _words(n % 1_000_000) if n % 1_000_000 else ""
        return head + (" " + rest if rest else "")
    raise ValueError("Amount too large")


def amount_in_words(total):
    """Decimal total -> e.g. 'EMPAT RIBU ... SATU DAN SEN SEMBILAN PULUH EMPAT'."""
    total = Decimal(total).quantize(Decimal("0.01"), ROUND_HALF_UP)
    ringgit, sen = int(total), int((total - int(total)) * 100)
    if not ringgit and not sen:
        return "KOSONG"
    if not ringgit:
        return ("SEN " + _words(sen)).upper()
    text = _words(ringgit)
    if sen:
        text += " dan sen " + _words(sen)
    else:
        text += " sahaja"
    return text.upper()


def money(d):
    return f"{Decimal(d):,.2f}"


def _clean(text):
    """Core PDF fonts only support Latin-1; swap common symbols."""
    text = str(text).replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    return text.encode("latin-1", "replace").decode("latin-1")


def compute_items(items):
    """items: list of dicts with qty, price (Decimals). Adds 'amount'. Returns total."""
    total = Decimal("0")
    for it in items:
        it["amount"] = (Decimal(it["qty"]) * Decimal(it["price"])).quantize(
            Decimal("0.01"), ROUND_HALF_UP)
        total += it["amount"]
    return total


def build_invoice_pdf(date, invoice_no, customer_lines, items):
    """Return PDF as bytes."""
    total = compute_items(items)

    pdf = FPDF(format="A4")
    pdf.set_margins(15, 12, 15)
    pdf.set_auto_page_break(True, margin=15)
    pdf.add_page()
    L, W = 15, 180  # left margin, usable width

    def line(txt="", style="", size=11, align="L", h=5, w=0):
        pdf.set_font("Helvetica", style, size)
        pdf.cell(w, h, _clean(txt), align=align, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ---- Company header ----
    line(COMPANY_NAME, "B", 12, "C")
    line(COMPANY_REG, "B", 12, "C")
    for a in COMPANY_ADDR:
        line(a, "", 11, "C")
    pdf.set_font("Helvetica", "", 11)
    w1 = pdf.get_string_width(COMPANY_CITY[0] + " ")
    pdf.set_font("Helvetica", "B", 11)
    w2 = pdf.get_string_width(COMPANY_CITY[1])
    pdf.set_x(L + (W - w1 - w2) / 2)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(w1, 5, COMPANY_CITY[0])
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(w2, 5, COMPANY_CITY[1], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    line(COMPANY_PHONE, "", 10, "R")
    pdf.ln(1)
    line("INVOIS", "B", 14, "R", h=8)
    pdf.ln(1)

    # ---- Customer + invoice info boxes ----
    line("Pelanggan;", "", 10)
    top = pdf.get_y() + 1
    box_h = 30
    pdf.rect(L, top, 95, box_h)
    pdf.rect(L + 105, top, 75, 20)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(L + 3, top + 2)
    pdf.multi_cell(90, 5, _clean("\n".join(customer_lines)), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_xy(L + 108, top + 3)
    pdf.cell(70, 5, _clean(f"Tarikh: {malay_date(date)}"))
    pdf.set_xy(L + 108, top + 11)
    pdf.cell(70, 5, _clean(f"No Invois: {invoice_no}"))
    pdf.set_xy(L, top + box_h + 8)

    # ---- Items table ----
    pdf.set_font("Helvetica", "", 10)
    head = FontFace(emphasis="", fill_color=None)
    with pdf.table(col_widths=(10, 92, 22, 28, 28),
                   text_align=("CENTER", "LEFT", "CENTER", "CENTER", "RIGHT"),
                   line_height=5, padding=2, headings_style=head) as table:
        r = table.row()
        for t in ("Bil", "Keterangan Kerja", "Kuantiti", "Harga Seunit\n(RM)", "Jumlah\n(RM)"):
            r.cell(_clean(t), align="C")
        for i, it in enumerate(items, 1):
            r = table.row()
            r.cell(str(i), align="C")
            r.cell(_clean(it["description"]), align="L")
            qty = f"{Decimal(it['qty']).normalize():f}"
            unit = f"\n({it['unit']})" if it.get("unit") else ""
            r.cell(_clean(qty + unit), align="C")
            r.cell(money(it["price"]), align="C")
            r.cell(money(it["amount"]), align="R")
        r = table.row()
        r.cell("JUMLAH KESELURUHAN (RM)", colspan=4, align="C",
               style=FontFace(emphasis="BOLD"))
        r.cell(money(total), align="R", style=FontFace(emphasis="BOLD"))

    # ---- Amount in words + bank details ----
    pdf.ln(5)
    lab = 40
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(lab, 5, "Ringgit Malaysia", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.multi_cell(0, 5, ": " + amount_in_words(total), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    for label, val in (("Nama Akaun", BANK_ACCOUNT_NAME),
                       ("No. Akaun", BANK_ACCOUNT_NO),
                       ("Nama Bank", BANK_NAME)):
        pdf.cell(lab, 5, label, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(0, 5, ": " + val, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ---- Signature blocks (blank space left for chop + signature) ----
    if pdf.get_y() > 215:
        pdf.add_page()
    pdf.ln(12)
    y = pdf.get_y()
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_xy(L, y)
    pdf.cell(80, 5, "PDH&NAS Enterprise;")
    pdf.set_xy(L + 110, y)
    pdf.cell(70, 5, "Diterima Oleh;")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(L, y + 22)
    pdf.cell(80, 5, "." * 55)
    pdf.set_xy(L + 110, y + 22)
    pdf.cell(70, 5, "." * 55)
    pdf.set_xy(L, y + 27)
    pdf.cell(80, 5, "Tarikh:")
    pdf.set_xy(L + 110, y + 27)
    pdf.cell(70, 5, "Tarikh:")

    return bytes(pdf.output())
