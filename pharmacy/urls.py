from django.urls import path

from . import autocompletes, views

app_name = "pharmacy"

urlpatterns = [
    # Autocompletes
    path("autocomplete/client/", autocompletes.ClientAutocomplete.as_view(), name="client-autocomplete"),
    path("autocomplete/doctor/", autocompletes.DoctorAutocomplete.as_view(), name="doctor-autocomplete"),
    path("autocomplete/medication/", autocompletes.MedicationAutocomplete.as_view(), name="medication-autocomplete"),
    path("autocomplete/practice/", autocompletes.PracticeAutocomplete.as_view(), name="practice-autocomplete"),
    path("autocomplete/strength/", autocompletes.MedicationStrengthAutocomplete.as_view(), name="strength-autocomplete"),
    path("autocomplete/size/", autocompletes.MedicationSizeAutocomplete.as_view(), name="size-autocomplete"),
    path("autocomplete/concentration/", autocompletes.MedicationConcentrationAutocomplete.as_view(), name="concentration-autocomplete"),

    # Prescriptions
    path("prescriptions/", views.PrescriptionListView.as_view(), name="prescription-list"),
    path("prescriptions/add/", views.PrescriptionCreateView.as_view(), name="prescription-add"),
    path("prescriptions/add/review/", views.PrescriptionReviewView.as_view(), name="prescription-review"),
    path("prescriptions/<int:pk>/", views.PrescriptionDetailView.as_view(), name="prescription-detail"),
    path("prescriptions/<int:pk>/print/", views.PrescriptionPrintView.as_view(), name="prescription-print"),
    path("prescriptions/<int:pk>/edit/", views.PrescriptionUpdateView.as_view(), name="prescription-edit"),
    path("prescriptions/<int:pk>/delete/", views.PrescriptionDeleteView.as_view(), name="prescription-delete"),

    # Medications
    path("medications/", views.MedicationListView.as_view(), name="medication-list"),
    path("medications/add/", views.MedicationCreateView.as_view(), name="medication-add"),
    path("medications/<int:pk>/edit/", views.MedicationUpdateView.as_view(), name="medication-edit"),
    path("medications/<int:pk>/delete/", views.MedicationDeleteView.as_view(), name="medication-delete"),

    # Doctors
    path("doctors/", views.DoctorListView.as_view(), name="doctor-list"),
    path("doctors/add/", views.DoctorCreateView.as_view(), name="doctor-add"),
    path("doctors/<int:pk>/edit/", views.DoctorUpdateView.as_view(), name="doctor-edit"),
    path("doctors/<int:pk>/delete/", views.DoctorDeleteView.as_view(), name="doctor-delete"),

    # Clients
    path("clients/", views.ClientListView.as_view(), name="client-list"),
    path("clients/add/", views.ClientCreateView.as_view(), name="client-add"),
    path("clients/<int:pk>/edit/", views.ClientUpdateView.as_view(), name="client-edit"),
    path("clients/<int:pk>/delete/", views.ClientDeleteView.as_view(), name="client-delete"),

    # Practice (gate destination, staff management, invites)
    path("practice/setup/", views.PracticeSetupView.as_view(), name="practice-setup"),
    path("practice/", views.PracticeDetailView.as_view(), name="practice-detail"),
    path("practice/edit/", views.PracticeUpdateView.as_view(), name="practice-edit"),
    path("practice/invite/", views.PracticeInviteSendView.as_view(), name="practice-invite-send"),
    path("practice/invite/<str:token>/", views.PracticeInviteAcceptView.as_view(), name="practice-invite-accept"),
    path("practice/staff/<int:user_id>/remove/", views.PracticeStaffRemoveView.as_view(), name="practice-staff-remove"),
    path("practice/staff/<int:user_id>/role/", views.PracticeStaffRoleChangeView.as_view(), name="practice-staff-role"),
]
