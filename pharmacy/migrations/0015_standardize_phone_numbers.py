from django.db import migrations

from pharmacy.phone import normalize_us_phone

PHONE_MODELS = ['Client', 'ClientBusiness', 'Doctor', 'Practice']


def standardize_phone_numbers(apps, schema_editor):
    '''Best-effort cleanup of existing data to "(555) 123-4567". Records
    whose phone_number doesn't reduce to a valid 10-digit US number are
    left alone rather than raised on -- this is a one-time tidy-up, not a
    hard constraint.'''
    for model_name in PHONE_MODELS:
        Model = apps.get_model('pharmacy', model_name)
        for obj in Model.objects.exclude(phone_number__isnull=True).exclude(phone_number__exact=''):
            try:
                normalized = normalize_us_phone(obj.phone_number)
            except ValueError:
                continue
            if normalized != obj.phone_number:
                obj.phone_number = normalized
                obj.save(update_fields=['phone_number'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0014_remove_historicalprescription_prescription_label_and_more'),
    ]

    operations = [
        migrations.RunPython(standardize_phone_numbers, noop),
    ]
