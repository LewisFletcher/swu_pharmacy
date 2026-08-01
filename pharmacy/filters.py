import django_filters
from django import forms

from accounts.models import User
from .models import Client, Doctor, Medication, Prescription

DAISY_INPUT = {"class": "input w-full"}
DAISY_SELECT = {"class": "select w-full"}


class PrescriptionFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(
        field_name="date_of_prescription", lookup_expr="gte",
        label="From", widget=forms.DateInput(attrs={"type": "date", **DAISY_INPUT}),
    )
    date_to = django_filters.DateFilter(
        field_name="date_of_prescription", lookup_expr="lte",
        label="To", widget=forms.DateInput(attrs={"type": "date", **DAISY_INPUT}),
    )
    created_by = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(), widget=forms.Select(attrs=DAISY_SELECT),
    )
    doctor = django_filters.ModelChoiceFilter(
        queryset=Doctor.objects.all(), widget=forms.Select(attrs=DAISY_SELECT),
    )
    client = django_filters.ModelChoiceFilter(
        queryset=Client.objects.all(), widget=forms.Select(attrs=DAISY_SELECT),
    )
    medication = django_filters.ModelChoiceFilter(
        queryset=Medication.objects.all(), widget=forms.Select(attrs=DAISY_SELECT),
    )

    class Meta:
        model = Prescription
        fields = ["date_from", "date_to", "created_by", "doctor", "client", "medication"]
