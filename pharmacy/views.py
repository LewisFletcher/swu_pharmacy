from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, TemplateView, UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin, SingleTableView

from .filters import PrescriptionFilter
from .forms import ClientForm, DoctorForm, MedicationForm, PrescriptionForm
from .labels import generate_prescription_label
from .models import Client, Doctor, Medication, Prescription
from .tables import ClientTable, DoctorTable, MedicationTable, PrescriptionTable

PENDING_PRESCRIPTION_SESSION_KEY = "pending_prescription"


class TrackedCreateView(LoginRequiredMixin, CreateView):
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class TrackedUpdateView(LoginRequiredMixin, UpdateView):
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class TrackedDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "pharmacy/confirm_delete.html"


# ---- Prescriptions (the dispensed-prescription historical view) ----

class PrescriptionListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    model = Prescription
    table_class = PrescriptionTable
    filterset_class = PrescriptionFilter
    template_name = "pharmacy/prescription_list.html"
    paginate_by = 25
    extra_context = {"title": "Dispensed Prescriptions", "add_url": "pharmacy:prescription-add"}


class PrescriptionDetailView(LoginRequiredMixin, DetailView):
    model = Prescription
    template_name = "pharmacy/prescription_detail.html"


class PrescriptionPrintView(LoginRequiredMixin, DetailView):
    model = Prescription
    template_name = "pharmacy/prescription_print.html"
    context_object_name = "prescription"


class PrescriptionCreateView(LoginRequiredMixin, CreateView):
    '''Step 1: collect prescription details, then hand off to the review step
    instead of saving directly.'''
    model = Prescription
    form_class = PrescriptionForm
    template_name = "pharmacy/form.html"
    extra_context = {
        "title": "New Prescription",
        "cancel_url": "pharmacy:prescription-list",
        "submit_label": "Create Prescription",
    }

    def get(self, request, *args, **kwargs):
        if request.GET.get("edit") != "1":
            request.session.pop(PENDING_PRESCRIPTION_SESSION_KEY, None)
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial.update(self.request.session.get(PENDING_PRESCRIPTION_SESSION_KEY) or {})
        return initial

    def form_valid(self, form):
        self.request.session[PENDING_PRESCRIPTION_SESSION_KEY] = form.data.dict()
        return redirect("pharmacy:prescription-review")


class PrescriptionReviewView(LoginRequiredMixin, TemplateView):
    '''Step 2: show the label that will be generated; confirm to actually save.'''
    template_name = "pharmacy/prescription_review.html"

    def _get_pending_form(self):
        pending = self.request.session.get(PENDING_PRESCRIPTION_SESSION_KEY)
        if not pending:
            return None
        form = PrescriptionForm(data=pending)
        return form if form.is_valid() else None

    def get(self, request, *args, **kwargs):
        form = self._get_pending_form()
        if form is None:
            return redirect("pharmacy:prescription-add")
        preview = Prescription(**form.cleaned_data)
        return self.render_to_response({"preview": preview})

    def post(self, request, *args, **kwargs):
        form = self._get_pending_form()
        if form is None:
            return redirect("pharmacy:prescription-add")
        prescription = form.save(commit=False)
        prescription.created_by = request.user
        prescription.updated_by = request.user
        prescription.save()
        generate_prescription_label(prescription)
        del request.session[PENDING_PRESCRIPTION_SESSION_KEY]
        return redirect("pharmacy:prescription-detail", pk=prescription.pk)


class PrescriptionUpdateView(TrackedUpdateView):
    model = Prescription
    form_class = PrescriptionForm
    template_name = "pharmacy/form.html"
    extra_context = {"title": "Edit Prescription", "cancel_url": "pharmacy:prescription-list"}
    success_url = reverse_lazy("pharmacy:prescription-list")


class PrescriptionDeleteView(TrackedDeleteView):
    model = Prescription
    extra_context = {"cancel_url": "pharmacy:prescription-list"}
    success_url = reverse_lazy("pharmacy:prescription-list")


# ---- Medications ----

class MedicationListView(LoginRequiredMixin, SingleTableView):
    model = Medication
    table_class = MedicationTable
    template_name = "pharmacy/list.html"
    extra_context = {"title": "Medications", "add_url": "pharmacy:medication-add"}
    paginate_by = 25


class MedicationCreateView(TrackedCreateView):
    model = Medication
    form_class = MedicationForm
    template_name = "pharmacy/form.html"
    extra_context = {"title": "New Medication", "cancel_url": "pharmacy:medication-list"}
    success_url = reverse_lazy("pharmacy:medication-list")


class MedicationUpdateView(TrackedUpdateView):
    model = Medication
    form_class = MedicationForm
    template_name = "pharmacy/form.html"
    extra_context = {"title": "Edit Medication", "cancel_url": "pharmacy:medication-list"}
    success_url = reverse_lazy("pharmacy:medication-list")


class MedicationDeleteView(TrackedDeleteView):
    model = Medication
    extra_context = {"cancel_url": "pharmacy:medication-list"}
    success_url = reverse_lazy("pharmacy:medication-list")


# ---- Doctors ----

class DoctorListView(LoginRequiredMixin, SingleTableView):
    model = Doctor
    table_class = DoctorTable
    template_name = "pharmacy/list.html"
    extra_context = {"title": "Doctors", "add_url": "pharmacy:doctor-add"}
    paginate_by = 25


class DoctorCreateView(TrackedCreateView):
    model = Doctor
    form_class = DoctorForm
    template_name = "pharmacy/form.html"
    extra_context = {"title": "New Doctor", "cancel_url": "pharmacy:doctor-list"}
    success_url = reverse_lazy("pharmacy:doctor-list")


class DoctorUpdateView(TrackedUpdateView):
    model = Doctor
    form_class = DoctorForm
    template_name = "pharmacy/form.html"
    extra_context = {"title": "Edit Doctor", "cancel_url": "pharmacy:doctor-list"}
    success_url = reverse_lazy("pharmacy:doctor-list")


class DoctorDeleteView(TrackedDeleteView):
    model = Doctor
    extra_context = {"cancel_url": "pharmacy:doctor-list"}
    success_url = reverse_lazy("pharmacy:doctor-list")


# ---- Clients ----

class ClientListView(LoginRequiredMixin, SingleTableView):
    model = Client
    table_class = ClientTable
    template_name = "pharmacy/list.html"
    extra_context = {"title": "Clients", "add_url": "pharmacy:client-add"}
    paginate_by = 25


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "pharmacy/form.html"
    extra_context = {"title": "New Client", "cancel_url": "pharmacy:client-list"}
    success_url = reverse_lazy("pharmacy:client-list")


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "pharmacy/form.html"
    extra_context = {"title": "Edit Client", "cancel_url": "pharmacy:client-list"}
    success_url = reverse_lazy("pharmacy:client-list")


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "pharmacy/confirm_delete.html"
    extra_context = {"cancel_url": "pharmacy:client-list"}
    success_url = reverse_lazy("pharmacy:client-list")
