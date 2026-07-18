import django_tables2 as tables

from .models import Client, Doctor, Medication, Prescription


def actions_column(edit_url_name, delete_url_name):
    template = (
        '<div class="flex gap-2 justify-end">'
        f'<a href="{{% url "{edit_url_name}" record.pk %}}" class="btn btn-xs btn-outline">Edit</a>'
        f'<a href="{{% url "{delete_url_name}" record.pk %}}" class="btn btn-xs btn-outline btn-error">Delete</a>'
        '</div>'
    )
    return tables.TemplateColumn(template, verbose_name="", orderable=False)


class PrescriptionTable(tables.Table):
    date_of_prescription = tables.Column(verbose_name="Date")
    created_by = tables.Column(verbose_name="Created By")
    created_at = tables.Column(verbose_name="Created At")
    detail = tables.TemplateColumn(
        '<a href="{% url "pharmacy:prescription-detail" record.pk %}" class="btn btn-xs btn-outline">View</a>',
        verbose_name="", orderable=False,
    )
    actions = actions_column("pharmacy:prescription-edit", "pharmacy:prescription-delete")

    class Meta:
        model = Prescription
        fields = (
            "date_of_prescription",
            "medication",
            "client",
            "doctor",
            "quantity",
            "animals_treated",
            "created_by",
            "created_at",
        )
        sequence = fields + ("detail", "actions")
        order_by = "-date_of_prescription"


class MedicationTable(tables.Table):
    actions = actions_column("pharmacy:medication-edit", "pharmacy:medication-delete")

    class Meta:
        model = Medication
        fields = ("brand_name", "drug_name", "active_ingredient")
        sequence = fields + ("actions",)


class DoctorTable(tables.Table):
    actions = actions_column("pharmacy:doctor-edit", "pharmacy:doctor-delete")

    class Meta:
        model = Doctor
        fields = ("name", "license_number", "license_expiration_date", "phone_number")
        sequence = fields + ("actions",)


class ClientTable(tables.Table):
    actions = actions_column("pharmacy:client-edit", "pharmacy:client-delete")

    class Meta:
        model = Client
        fields = ("name", "species", "phone_number", "email_address")
        sequence = fields + ("actions",)
