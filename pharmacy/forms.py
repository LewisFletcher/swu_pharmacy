from dal_alight.widgets import ModelAlight, ModelAlightMultiple
from django import forms
from django.forms import inlineformset_factory
from django.forms.models import BaseInlineFormSet

from .models import Address, Client, ClientBusiness, Doctor, Medication, Practice, PracticeInvite, Prescription


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


class DoctorForm(DaisyFormMixin, NestedAddressFormMixin, forms.ModelForm):
    class Meta:
        model = Doctor
        exclude = ('created_at', 'updated_at', 'created_by', 'updated_by', 'address')
        widgets = {
            'license_expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ClientForm(DaisyFormMixin, forms.ModelForm):
    class Meta:
        model = Client
        fields = ('name', 'phone_number', 'email_address', 'species')


class ClientBusinessForm(DaisyFormMixin, NestedAddressFormMixin, forms.ModelForm):
    class Meta:
        model = ClientBusiness
        fields = ('name', 'phone_number', 'email', 'website')

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('DELETE'):
            return cleaned_data
        street = cleaned_data.get('address_street', '').strip()
        client = getattr(self.instance, 'client', None)
        if street and client and client.pk:
            duplicate = ClientBusiness.objects.filter(
                client=client,
                address__street__iexact=street,
                address__city__iexact=cleaned_data.get('address_city', '').strip(),
                address__state__iexact=cleaned_data.get('address_state', '').strip(),
                address__zip_code__iexact=cleaned_data.get('address_zip_code', '').strip(),
            ).exclude(pk=self.instance.pk).exists()
            if duplicate:
                raise forms.ValidationError("This client already has a business at this address.")
        return cleaned_data


class BaseClientBusinessFormSet(BaseInlineFormSet):
    '''Catches duplicate addresses entered across multiple business rows in
    the same submission (the per-form clean only catches dupes already saved
    in the database).'''

    def clean(self):
        super().clean()
        seen = set()
        for form in self.forms:
            if not hasattr(form, 'cleaned_data') or form.cleaned_data.get('DELETE'):
                continue
            street = form.cleaned_data.get('address_street', '').strip().lower()
            if not street:
                continue
            key = (
                street,
                form.cleaned_data.get('address_city', '').strip().lower(),
                form.cleaned_data.get('address_state', '').strip().lower(),
                form.cleaned_data.get('address_zip_code', '').strip().lower(),
            )
            if key in seen:
                form.add_error('address_street', "You've entered this address for more than one business.")
            seen.add(key)


ClientBusinessFormSet = inlineformset_factory(
    Client,
    ClientBusiness,
    form=ClientBusinessForm,
    formset=BaseClientBusinessFormSet,
    extra=1,
    can_delete=True,
)


class PracticeForm(DaisyFormMixin, NestedAddressFormMixin, forms.ModelForm):
    class Meta:
        model = Practice
        exclude = ('created_at', 'updated_at', 'created_by', 'updated_by', 'address')


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
