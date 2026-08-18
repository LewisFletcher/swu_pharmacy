'''Shared display formatting, used by tables.py, templatetags, and pdf.py's
callers alike so the "business first" convention stays consistent.'''


def client_display(prescription):
    '''"Business — Client" if tied to a specific business, else just the
    client's name.'''
    if not prescription or not prescription.client:
        return "—"
    if prescription.client_business:
        return f"{prescription.client_business.name} — {prescription.client.name}"
    return prescription.client.name
