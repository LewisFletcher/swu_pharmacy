from dal_alight.widgets import ModelAlight, ModelAlightMultiple
from django import forms

from .models import Client, Doctor, Medication, Prescription


class DaisyFormMixin:
    '''Applies DaisyUI input classes to every field's widget automatically.'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            existing = widget.attrs.get('class', '')
            if isinstance(widget, forms.CheckboxInput):
                css_class = 'checkbox'
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css_class = 'select w-full'
            elif isinstance(widget, forms.Textarea):
                css_class = 'textarea w-full'
            elif isinstance(widget, forms.ClearableFileInput):
                css_class = 'file-input w-full'
            else:
                css_class = 'input w-full'
            widget.attrs['class'] = f'{existing} {css_class}'.strip()


class PrescriptionForm(DaisyFormMixin, forms.ModelForm):
    class Meta:
        model = Prescription
        exclude = ('created_at', 'updated_at', 'created_by', 'updated_by', 'prescription_label')
        widgets = {
            'date_of_prescription': forms.DateInput(attrs={'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
            'medication': ModelAlight(url='pharmacy:medication-autocomplete'),
            'strength': ModelAlight(url='pharmacy:strength-autocomplete'),
            'client': ModelAlight(url='pharmacy:client-autocomplete'),
            'doctor': ModelAlight(url='pharmacy:doctor-autocomplete'),
            'practice': ModelAlight(url='pharmacy:practice-autocomplete'),
        }


class MedicationForm(DaisyFormMixin, forms.ModelForm):
    class Meta:
        model = Medication
        exclude = ('created_at', 'updated_at', 'created_by', 'updated_by')
        widgets = {
            'strength_options': ModelAlightMultiple(url='pharmacy:strength-autocomplete'),
            'sizes': ModelAlightMultiple(url='pharmacy:size-autocomplete'),
            'concentrations': ModelAlightMultiple(url='pharmacy:concentration-autocomplete'),
        }


class DoctorForm(DaisyFormMixin, forms.ModelForm):
    class Meta:
        model = Doctor
        exclude = ('created_at', 'updated_at', 'created_by', 'updated_by')
        widgets = {
            'license_expiration_date': forms.DateInput(attrs={'type': 'date'}),
            'address': ModelAlight(url='pharmacy:address-autocomplete'),
        }


class ClientForm(DaisyFormMixin, forms.ModelForm):
    class Meta:
        model = Client
        fields = ('name', 'phone_number', 'email_address', 'species')
