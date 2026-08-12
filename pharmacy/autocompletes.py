from django.contrib.auth.mixins import LoginRequiredMixin
from dal_alight.views import AlightListView, AlightQuerySetView

from .models import (
    Client,
    Doctor,
    Medication,
    Practice,
)


class ClientAutocomplete(LoginRequiredMixin, AlightQuerySetView):
    model = Client
    search_fields = ['name']


class ClientBusinessAutocomplete(LoginRequiredMixin, AlightListView):
    '''Combined client-or-business picker: a client's own name is always a
    result, plus one result per business they have (see Client.businesses).
    Values are "c-<client_pk>" or "b-<business_pk>" -- see
    forms.PrescriptionForm.clean_client_selection() for the other side.'''

    def get_list(self):
        items = []
        for client in Client.objects.all().prefetch_related('businesses'):
            items.append((f'c-{client.pk}', client.name))
            for business in client.businesses.all():
                items.append((f'b-{business.pk}', f'{business.name} — {client.name}'))
        return items


class DoctorAutocomplete(LoginRequiredMixin, AlightQuerySetView):
    model = Doctor
    search_fields = ['name', 'license_number']


class MedicationAutocomplete(LoginRequiredMixin, AlightQuerySetView):
    model = Medication
    search_fields = ['drug_name', 'active_ingredient']


class PracticeAutocomplete(LoginRequiredMixin, AlightQuerySetView):
    model = Practice
    search_fields = ['name']
