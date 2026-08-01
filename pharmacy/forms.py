from dal_alight.widgets import ModelAlight
from django import forms

from .models import Address, Client, Doctor, Medication, Practice, PracticeInvite, Prescription


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


class NestedAddressFormMixin:
    '''Adds plain street/city/state/zip fields and creates/attaches an Address
    on save, instead of picking an existing Address from a dropdown.'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address_street'] = forms.CharField(label='Street', required=False)
        self.fields['address_city'] = forms.CharField(label='City', required=False)
        self.fields['address_state'] = forms.CharField(label='State', required=False)
        self.fields['address_zip_code'] = forms.CharField(label='Zip Code', required=False)
        address = getattr(self.instance, 'address', None)
        if address:
            self.fields['address_street'].initial = address.street
            self.fields['address_city'].initial = address.city
            self.fields['address_state'].initial = address.state
            self.fields['address_zip_code'].initial = address.zip_code

    def save(self, commit=True):
        instance = super().save(commit=False)
        street = self.cleaned_data.get('address_street', '').strip()
        if street:
            city = self.cleaned_data.get('address_city', '').strip()
            state = self.cleaned_data.get('address_state', '').strip()
            zip_code = self.cleaned_data.get('address_zip_code', '').strip()
            address, _ = Address.objects.get_or_create(
                street=street, city=city, state=state, zip_code=zip_code,
            )
            instance.address = address
        else:
            instance.address = None
        if commit:
            instance.save()
        return instance


class PrescriptionForm(DaisyFormMixin, forms.ModelForm):
    class Meta:
        model = Prescription
        exclude = (
            'created_at', 'updated_at', 'created_by', 'updated_by', 'prescription_label',
            'strength', 'animals_treated', 'route_of_administration', 'cautionary_notes', 'practice',
        )
        widgets = {
            'date_of_prescription': forms.DateInput(attrs={'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
            'medication': ModelAlight(url='pharmacy:medication-autocomplete'),
            'client': ModelAlight(url='pharmacy:client-autocomplete'),
            'doctor': ModelAlight(url='pharmacy:doctor-autocomplete'),
        }


class MedicationForm(DaisyFormMixin, forms.ModelForm):
    class Meta:
        model = Medication
        fields = ('drug_name', 'active_ingredient', 'directions', 'milk_withhold_period', 'meat_withhold_period', 'approved_age')


class DoctorForm(DaisyFormMixin, NestedAddressFormMixin, forms.ModelForm):
    class Meta:
        model = Doctor
        exclude = ('created_at', 'updated_at', 'created_by', 'updated_by', 'address')
        widgets = {
            'license_expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ClientForm(DaisyFormMixin, NestedAddressFormMixin, forms.ModelForm):
    class Meta:
        model = Client
        fields = ('name', 'business_name', 'phone_number', 'email_address', 'species')


class PracticeForm(DaisyFormMixin, NestedAddressFormMixin, forms.ModelForm):
    class Meta:
        model = Practice
        exclude = ('created_at', 'updated_at', 'created_by', 'updated_by', 'address')
        widgets = {
            'default_doctor': ModelAlight(url='pharmacy:doctor-autocomplete'),
        }


class PracticeInviteForm(DaisyFormMixin, forms.ModelForm):
    class Meta:
        model = PracticeInvite
        fields = ('email', 'role')

    def __init__(self, *args, practice=None, inviter=None, **kwargs):
        self.practice = practice
        self.inviter = inviter
        super().__init__(*args, **kwargs)
        if inviter is not None:
            self.fields['role'].choices = [
                (value, label) for value, label in self.fields['role'].choices
                if inviter.can_grant_role(value)
            ]

    def clean_email(self):
        email = self.cleaned_data['email']
        if self.practice and self.practice.invites.filter(email__iexact=email, accepted_at__isnull=True).exists():
            raise forms.ValidationError("There's already a pending invite for this email.")
        return email
