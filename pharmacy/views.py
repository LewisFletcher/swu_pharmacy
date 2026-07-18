from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, TemplateView, UpdateView, View
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin, SingleTableView

from .filters import PrescriptionFilter
from .forms import (
    ClientBusinessFormSet,
    ClientForm,
    DoctorForm,
    MedicationForm,
    PracticeForm,
    PracticeInviteForm,
    PrescriptionForm,
)
from .labels import generate_prescription_label
from .models import Client, Doctor, Medication, Practice, PracticeInvite, Prescription
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
    '''Creates a Client together with its (required, at-least-one) businesses.'''
    model = Client
    form_class = ClientForm
    template_name = "pharmacy/client_form.html"
    extra_context = {"title": "New Client", "cancel_url": "pharmacy:client-list"}

    def get(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        formset = ClientBusinessFormSet(instance=Client())
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def post(self, request, *args, **kwargs):
        self.object = None
        new_client = Client()
        form = ClientForm(request.POST, instance=new_client)
        formset = ClientBusinessFormSet(request.POST, instance=new_client)
        if form.is_valid() and formset.is_valid():
            client = form.save()
            formset.instance = client
            formset.save()
            return redirect("pharmacy:client-list")
        return self.render_to_response(self.get_context_data(form=form, formset=formset))


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    '''Edits a Client together with its businesses.'''
    model = Client
    form_class = ClientForm
    template_name = "pharmacy/client_form.html"
    extra_context = {"title": "Edit Client", "cancel_url": "pharmacy:client-list"}

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        formset = ClientBusinessFormSet(instance=self.object)
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        formset = ClientBusinessFormSet(request.POST, instance=self.object)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect("pharmacy:client-list")
        return self.render_to_response(self.get_context_data(form=form, formset=formset))


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "pharmacy/confirm_delete.html"
    extra_context = {"cancel_url": "pharmacy:client-list"}
    success_url = reverse_lazy("pharmacy:client-list")


# ---- Practice (gate destination, staff management, invites) ----

class PracticeSetupView(LoginRequiredMixin, CreateView):
    '''Where a user with no practice lands (see PracticeRequiredMiddleware)
    so they can create one and become its first staff member.'''
    model = Practice
    form_class = PracticeForm
    template_name = "pharmacy/practice_setup.html"
    extra_context = {"title": "Set Up Your Practice", "submit_label": "Create Practice"}

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.practice_id:
            return redirect("pharmacy:practice-detail")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        user = self.request.user
        user.practice = self.object
        user.practice_role = user.PracticeRole.ADMIN
        user.save(update_fields=["practice", "practice_role"])
        return response

    def get_success_url(self):
        return reverse("landing")


class PracticeUpdateView(LoginRequiredMixin, UpdateView):
    '''Lets a staff member update their own practice's info.'''
    model = Practice
    form_class = PracticeForm
    template_name = "pharmacy/form.html"
    extra_context = {"title": "Edit Practice Info", "cancel_url": "pharmacy:practice-detail"}
    success_url = reverse_lazy("pharmacy:practice-detail")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.practice_id:
            return redirect("pharmacy:practice-setup")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user.practice

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class PracticeDetailView(LoginRequiredMixin, TemplateView):
    template_name = "pharmacy/practice_detail.html"

    def get(self, request, *args, **kwargs):
        if not request.user.practice_id:
            return redirect("pharmacy:practice-setup")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        practice = self.request.user.practice
        context["practice"] = practice
        context["staff"] = practice.staff.all()
        context["pending_invites"] = practice.invites.filter(accepted_at__isnull=True)
        context["invite_form"] = PracticeInviteForm(practice=practice, inviter=self.request.user)
        return context


class PracticeInviteSendView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        practice = request.user.practice
        if not practice:
            return redirect("pharmacy:practice-setup")
        form = PracticeInviteForm(request.POST, practice=practice, inviter=request.user)
        if form.is_valid():
            invite = form.save(commit=False)
            invite.practice = practice
            invite.invited_by = request.user
            invite.save()
            self._send_invite_email(request, invite)
            messages.success(request, f"Invited {invite.email} to join {practice.name}.")
        else:
            for error in form.errors.get("email", []):
                messages.error(request, error)
        return redirect("pharmacy:practice-detail")

    def _send_invite_email(self, request, invite):
        accept_url = request.build_absolute_uri(
            reverse("pharmacy:practice-invite-accept", args=[invite.token])
        )
        send_mail(
            subject=f"You've been invited to join {invite.practice.name} on SWU Pharm",
            message=(
                f"{invite.invited_by} has invited you to join {invite.practice.name} "
                f"on SWU Pharm.\n\nAccept the invite here:\n{accept_url}\n"
            ),
            from_email=None,
            recipient_list=[invite.email],
        )


class PracticeInviteAcceptView(View):
    '''Reachable while logged out (see EXEMPT_PATH_PREFIXES) so a brand-new
    invitee can follow the link, sign up, and land back here to join.'''

    def get(self, request, *args, **kwargs):
        token = kwargs["token"]
        invite = PracticeInvite.objects.filter(token=token).first()

        if invite is None:
            messages.error(request, "That invite link is invalid.")
            return redirect("landing" if request.user.is_authenticated else "account_login")
        if invite.is_accepted:
            messages.info(request, "That invite has already been used.")
            return redirect("landing" if request.user.is_authenticated else "account_login")

        if not request.user.is_authenticated:
            return redirect(f"{reverse('account_signup')}?next={request.path}")

        request.user.practice = invite.practice
        request.user.practice_role = invite.role
        request.user.save(update_fields=["practice", "practice_role"])
        invite.accepted_at = timezone.now()
        invite.save(update_fields=["accepted_at"])
        messages.success(request, f"You've joined {invite.practice.name}.")
        return redirect("landing")


class PracticeStaffRemoveView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        practice = request.user.practice
        if not practice:
            return redirect("pharmacy:practice-setup")
        User = get_user_model()
        member = get_object_or_404(User, pk=kwargs["user_id"], practice=practice)
        if member == request.user:
            messages.error(request, "You can't remove yourself from the practice.")
        elif not request.user.can_manage(member):
            messages.error(request, "You don't have permission to remove that person.")
        else:
            member.practice = None
            member.save(update_fields=["practice"])
            messages.success(request, f"Removed {member} from {practice.name}.")
        return redirect("pharmacy:practice-detail")


class PracticeStaffRoleChangeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        practice = request.user.practice
        if not practice:
            return redirect("pharmacy:practice-setup")
        User = get_user_model()
        member = get_object_or_404(User, pk=kwargs["user_id"], practice=practice)
        new_role = request.POST.get("role")
        valid_roles = {value for value, _ in User.PracticeRole.choices}

        if member == request.user:
            messages.error(request, "You can't change your own role.")
        elif new_role not in valid_roles:
            messages.error(request, "That's not a valid role.")
        elif not request.user.can_manage(member):
            messages.error(request, "You don't have permission to change that person's role.")
        elif not request.user.can_grant_role(new_role):
            messages.error(request, "You can't grant a role higher than your own.")
        else:
            member.practice_role = new_role
            member.save(update_fields=["practice_role"])
            messages.success(request, f"Updated {member}'s role to {member.get_practice_role_display()}.")
        return redirect("pharmacy:practice-detail")
