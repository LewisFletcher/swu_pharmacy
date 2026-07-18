from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from pharmacy.models import Client, Doctor, Medication, Prescription


@login_required
def landing(request):
    recent_prescriptions = Prescription.objects.select_related(
        "client", "medication", "doctor"
    )[:8]
    week_ago = timezone.now().date() - timedelta(days=7)

    context = {
        "recent_prescriptions": recent_prescriptions,
        "prescription_count": Prescription.objects.count(),
        "prescriptions_this_week": Prescription.objects.filter(
            date_of_prescription__gte=week_ago
        ).count(),
        "client_count": Client.objects.count(),
        "medication_count": Medication.objects.count(),
        "doctor_count": Doctor.objects.count(),
    }
    return render(request, "landing/index.html", context)
