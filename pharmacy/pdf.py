'''Prescription label PDF generation.

Sized for the practice's Dymo LabelWriter 550. The stated label size
(49mm x 89mm) doesn't match a standard Dymo SKU exactly -- the closest are
the 30252 "address" label (28mm x 89mm) or the 99014 "large shipping" label
(54mm x 101mm). If it turns out to be one of those, just adjust the two
constants below; everything else is computed from them.

Layout follows common pharmacy-label conventions: sans-serif type, drug
name largest/boldest, safety-critical withdrawal times bolded, contact/
date info smallest at the bottom. Body text is nominally 9-10pt; true
10-12pt "ideal" sizing isn't achievable for every field at this physical
size, so the most safety-critical items (drug name, withdrawal times) get
priority for size, and free-text fields that vary a lot in length (dosage
instructions) shrink to fit rather than clip.
'''

from io import BytesIO

from reportlab.lib.colors import black
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

LABEL_WIDTH_MM = 89
LABEL_HEIGHT_MM = 49
MARGIN_MM = 2.5

FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_ITALIC = "Helvetica-Oblique"


def _fit_paragraph(text, base_size, max_width, max_height, bold=False, min_size=6.0):
    '''Build a Paragraph that fits within max_height, shrinking the font
    size in steps if it doesn't fit at base_size. Returns (paragraph, height).'''
    font_name = FONT_BOLD if bold else FONT
    size = base_size
    paragraph = None
    height = 0
    while size >= min_size:
        style = ParagraphStyle(
            "fit", fontName=font_name, fontSize=size, leading=size * 1.18, alignment=TA_LEFT,
        )
        paragraph = Paragraph(text, style)
        _, height = paragraph.wrap(max_width, max_height)
        if height <= max_height:
            return paragraph, height
        size -= 0.5
    return paragraph, height


def render_prescription_label_pdf(prescription):
    '''Render a single prescription label to PDF bytes.'''
    buffer = BytesIO()
    width = LABEL_WIDTH_MM * mm
    height = LABEL_HEIGHT_MM * mm
    c = canvas.Canvas(buffer, pagesize=(width, height))

    margin = MARGIN_MM * mm
    content_width = width - 2 * margin
    x = margin
    y = height - margin

    medication = prescription.medication
    practice = prescription.practice
    doctor = prescription.doctor

    def draw_line(text, font=FONT, size=8, gap_after=None, color=black):
        '''Draw one line of plain text, top-down, advancing y.'''
        nonlocal y
        c.setFont(font, size)
        c.setFillColor(color)
        y -= size
        c.drawString(x, y, text)
        y -= gap_after if gap_after is not None else size * 0.4

    # --- Header: practice + doctor phone ---
    header_bits = []
    if practice and practice.name:
        header_bits.append(practice.name)
    if doctor and doctor.phone_number:
        header_bits.append(doctor.phone_number)
    if header_bits:
        draw_line(" • ".join(header_bits), font=FONT_BOLD, size=8)

    # --- Client + species ---
    client_bits = [prescription.client.name if prescription.client else "—"]
    if prescription.animal_species:
        client_bits.append(prescription.animal_species)
    draw_line("   ".join(client_bits), font=FONT_BOLD, size=9.5)

    # --- Drug name (most prominent line on the label) ---
    drug_line = medication.drug_name if medication else "—"
    if medication and medication.active_ingredient:
        drug_line += f" ({medication.active_ingredient})"
    draw_line(drug_line, font=FONT_BOLD, size=12, gap_after=3)

    # --- Quantity / strength ---
    qty_bits = [f"Qty: {prescription.quantity}"]
    if prescription.strength_id:
        qty_bits.append(f"Strength: {prescription.strength}")
    draw_line("     ".join(qty_bits), size=8.5, gap_after=4)

    top_block_bottom = y

    # --- Fixed bottom section, computed bottom-up so we know how much
    # flexible space is left in the middle for dosage instructions ---
    footer_bits = [prescription.date_of_prescription.strftime("%m/%d/%Y")]
    if prescription.expiration_date:
        footer_bits.append(f"Exp: {prescription.expiration_date.strftime('%m/%d/%Y')}")
    if doctor:
        footer_bits.append(doctor.name)
    footer_text = "  •  ".join(footer_bits)

    duration_bits = []
    if prescription.duration:
        duration_bits.append(f"Duration: {prescription.duration}")
    duration_bits.append(f"Refills: {prescription.number_of_refills}")
    duration_text = "     ".join(duration_bits)

    milk = medication.milk_withhold_period if medication else None
    meat = medication.meat_withhold_period if medication else None
    withdrawal_text = None
    if milk or meat:
        parts = []
        if milk:
            parts.append(f"Milk: {milk}")
        if meat:
            parts.append(f"Meat/Slaughter: {meat}")
        withdrawal_text = "WITHDRAWAL - " + "  •  ".join(parts)

    caution_text = prescription.cautionary_notes or None

    FOOTER_SIZE = 7
    DURATION_SIZE = 8
    WITHDRAWAL_SIZE = 8.5
    CAUTION_SIZE = 7.5
    LINE_GAP = 2

    fixed_bottom_height = FOOTER_SIZE + LINE_GAP + DURATION_SIZE + LINE_GAP
    if withdrawal_text:
        fixed_bottom_height += WITHDRAWAL_SIZE + LINE_GAP
    caution_height = 0
    caution_paragraph = None
    if caution_text:
        caution_paragraph, caution_height = _fit_paragraph(
            f"Caution: {caution_text}", CAUTION_SIZE, content_width,
            max_height=CAUTION_SIZE * 1.18 * 2, bold=False, min_size=6,
        )
        fixed_bottom_height += caution_height + LINE_GAP

    bottom_margin_y = margin

    # --- Flexible middle: dosage instructions get whatever space is left ---
    flexible_height = top_block_bottom - bottom_margin_y - fixed_bottom_height
    flexible_height = max(flexible_height, 10)
    dosage_text = prescription.dosage_instructions or "See package insert for directions."
    dosage_paragraph, dosage_height = _fit_paragraph(
        dosage_text, 9.5, content_width, flexible_height, bold=False, min_size=6,
    )
    dosage_paragraph.drawOn(c, x, top_block_bottom - dosage_height)
    y = top_block_bottom - dosage_height - LINE_GAP

    # --- Duration / refills ---
    draw_line(duration_text, font=FONT, size=DURATION_SIZE, gap_after=LINE_GAP)

    # --- Withdrawal times (bold, safety-critical) ---
    if withdrawal_text:
        draw_line(withdrawal_text, font=FONT_BOLD, size=WITHDRAWAL_SIZE, gap_after=LINE_GAP)

    # --- Cautionary notes ---
    if caution_paragraph:
        caution_paragraph.drawOn(c, x, y - caution_height)
        y -= caution_height + LINE_GAP

    # --- Footer: date / expiration / doctor ---
    c.setFont(FONT_ITALIC, FOOTER_SIZE)
    c.setFillColor(black)
    c.drawString(x, margin, footer_text)

    c.showPage()
    c.save()
    return buffer.getvalue()
