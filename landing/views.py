from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from pharmacy.models import Client, Doctor, Medication, Prescription


LICENSE_ALERT_WINDOW_DAYS = 30


@login_required
def landing(request):
    recent_prescriptions = Prescription.objects.select_related(
        "client", "medication", "doctor"
    )[:8]
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    alert_cutoff = today + timedelta(days=LICENSE_ALERT_WINDOW_DAYS)
    license_alerts = [
        {"doctor": doctor, "days_left": (doctor.license_expiration_date - today).days}
        for doctor in Doctor.objects.filter(
            license_expiration_date__isnull=False,
            license_expiration_date__lte=alert_cutoff,
        ).order_by("license_expiration_date")
    ]

    context = {
        "recent_prescriptions": recent_prescriptions,
        "prescription_count": Prescription.objects.count(),
        "prescriptions_this_week": Prescription.objects.filter(
            date_of_prescription__gte=week_ago
        ).count(),
        "client_count": Client.objects.count(),
        "medication_count": Medication.objects.count(),
        "doctor_count": Doctor.objects.count(),
        "license_alerts": license_alerts,
    }
    return render(request, "landing/index.html", context)
