def generate_prescription_label(prescription):
    '''Generate the printable label for a dispensed prescription.

    Called once, right after a Prescription is confirmed and saved (see
    PrescriptionReviewView.post in views.py). `prescription` is the saved
    instance, so all FKs (medication, client, doctor, practice, strength)
    are available.

    Implement this to build the label file (e.g. a PDF/image) and assign it
    to `prescription.prescription_label`, then save the instance, for
    example:

        from django.core.files.base import ContentFile
        pdf_bytes = ...  # render the label
        prescription.prescription_label.save(
            f"prescription-{prescription.pk}.pdf",
            ContentFile(pdf_bytes),
            save=True,
        )
    '''
    pass
