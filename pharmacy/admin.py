from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    Address,
    Client,
    ClientBusiness,
    Doctor,
    Medication,
    MedicationConcentration,
    MedicationSize,
    MedicationStrength,
    Practice,
    PracticeInvite,
    Prescription,
)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('street', 'city', 'state', 'zip_code')
    search_fields = ('street', 'city', 'state', 'zip_code')


@admin.register(ClientBusiness)
class ClientBusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'address', 'phone_number', 'email', 'website')
    search_fields = ('name', 'email', 'client__name')
    autocomplete_fields = ('client', 'address')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'phone_number', 'email_address')
    list_filter = ('species',)
    search_fields = ('name', 'email_address', 'phone_number')


@admin.register(Doctor)
class DoctorAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'license_number', 'license_expiration_date', 'phone_number')
    search_fields = ('name', 'license_number', 'email')


@admin.register(MedicationStrength)
class MedicationStrengthAdmin(SimpleHistoryAdmin):
    list_display = ('strength', 'unit')
    search_fields = ('strength', 'unit')


@admin.register(MedicationSize)
class MedicationSizeAdmin(SimpleHistoryAdmin):
    list_display = ('size', 'unit')
    search_fields = ('size', 'unit')


@admin.register(MedicationConcentration)
class MedicationConcentrationAdmin(SimpleHistoryAdmin):
    list_display = ('concentration', 'unit')
    search_fields = ('concentration', 'unit')


@admin.register(Medication)
class MedicationAdmin(SimpleHistoryAdmin):
    list_display = ('drug_name', 'active_ingredient')
    search_fields = ('drug_name', 'active_ingredient')
    filter_horizontal = ('strength_options', 'sizes', 'concentrations')


@admin.register(Practice)
class PracticeAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email', 'website')
    search_fields = ('name', 'email')


@admin.register(PracticeInvite)
class PracticeInviteAdmin(admin.ModelAdmin):
    list_display = ('email', 'practice', 'role', 'invited_by', 'created_at', 'accepted_at')
    list_filter = ('practice', 'role')
    search_fields = ('email', 'practice__name')


@admin.register(Prescription)
class PrescriptionAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'date_of_prescription',
        'medication',
        'client',
        'doctor',
        'quantity',
        'created_by',
        'created_at',
    )
    list_filter = ('date_of_prescription', 'doctor', 'created_by')
    search_fields = ('client__name', 'medication__drug_name')
    date_hierarchy = 'date_of_prescription'
    autocomplete_fields = ('medication', 'client', 'client_business', 'doctor', 'practice', 'strength')


admin.site.site_header = "SWU Pharm Admin"
admin.site.site_title = "SWU Pharm Admin"
admin.site.index_title = "Administration"
