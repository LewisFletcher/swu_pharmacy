from django.core.files.base import ContentFile

from .pdf import render_prescription_label_pdf


def generate_prescription_label(prescription):
    '''Generate the printable label for a dispensed prescription and save it
    to `prescription.prescription_label`.

    Called once, right after a Prescription is confirmed and saved (see
    PrescriptionReviewView.post in views.py). This is a snapshot of the
    label as of creation time -- it isn't regenerated on later edits.
    Printing (PrescriptionPrintView) always renders fresh from current
    data instead of reading this file back, so edits are still reflected
    when actually printing.
    '''
    pdf_bytes = render_prescription_label_pdf(prescription)
    prescription.prescription_label.save(
        f"prescription-{prescription.pk}.pdf",
        ContentFile(pdf_bytes),
        save=True,
    )
