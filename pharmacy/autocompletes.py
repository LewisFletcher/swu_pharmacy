from django.contrib.auth.mixins import LoginRequiredMixin
from dal_alight.views import AlightQuerySetView

from .models import (
    Client,
    Doctor,
    Medication,
    MedicationConcentration,
    MedicationSize,
    MedicationStrength,
    Practice,
)


class ClientAutocomplete(LoginRequiredMixin, AlightQuerySetView):
    model = Client
    search_fields = ['name']


class DoctorAutocomplete(LoginRequiredMixin, AlightQuerySetView):
    model = Doctor
    search_fields = ['name', 'license_number']


class MedicationAutocomplete(LoginRequiredMixin, AlightQuerySetView):
    model = Medication
    search_fields = ['brand_name', 'drug_name', 'active_ingredient']


class PracticeAutocomplete(LoginRequiredMixin, AlightQuerySetView):
    model = Practice
    search_fields = ['name']


class MedicationStrengthAutocomplete(LoginRequiredMixin, AlightQuerySetView):
    model = MedicationStrength
    search_fields = ['strength', 'unit']


class MedicationSizeAutocomplete(LoginRequiredMixin, AlightQuerySetView):
    model = MedicationSize
    search_fields = ['size', 'unit']


class MedicationConcentrationAutocomplete(LoginRequiredMixin, AlightQuerySetView):
    model = MedicationConcentration
    search_fields = ['concentration', 'unit']
