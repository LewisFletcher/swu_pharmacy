from dal_alight.widgets import ListAlight, ModelAlight
from django import forms

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
    '''`client`/`client_business` aren't real form fields -- a single
    `client_selection` field lets staff search by either the client's own
    name or any of their business names (see ClientBusinessAutocomplete),
    and clean/save resolve it back to the two underlying FKs.'''

    client_selection = forms.CharField(
        label='Client', widget=ListAlight(url='pharmacy:client-business-autocomplete'),
    )

    field_order = [
        'date_of_prescription', 'medication', 'quantity', 'client_selection',
        'doctor', 'animal_species', 'dosage_instructions', 'duration',
        'expiration_date', 'number_of_refills',
    ]

    class Meta:
        model = Prescription
        exclude = (
            'created_at', 'updated_at', 'created_by', 'updated_by',
            'strength', 'animals_treated', 'route_of_administration', 'cautionary_notes', 'practice',
            'client', 'client_business',
        )
        widgets = {
            'date_of_prescription': forms.DateInput(attrs={'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
            'medication': ModelAlight(url='pharmacy:medication-autocomplete'),
            'doctor': ModelAlight(url='pharmacy:doctor-autocomplete'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._resolved_client = None
        self._resolved_client_business = None
        selected = None
        if self.instance.pk:
            if self.instance.client_business_id:
                business = self.instance.client_business
                selected = (f'b-{business.pk}', f'{business.name} — {business.client.name}')
            elif self.instance.client_id:
                selected = (f'c-{self.instance.client_id}', self.instance.client.name)
        if selected:
            self.fields['client_selection'].initial = selected[0]
            self.fields['client_selection'].widget.choices = [selected]

    def clean_client_selection(self):
        value = self.cleaned_data.get('client_selection', '')
        kind, _, raw_id = value.partition('-')
        error = forms.ValidationError('Select a valid client or business.')
        if kind == 'b':
            try:
                business = ClientBusiness.objects.select_related('client').get(pk=raw_id)
            except (ClientBusiness.DoesNotExist, ValueError):
                raise error
            self._resolved_client = business.client
            self._resolved_client_business = business
        elif kind == 'c':
            try:
                self._resolved_client = Client.objects.get(pk=raw_id)
            except (Client.DoesNotExist, ValueError):
                raise error
            self._resolved_client_business = None
        else:
            raise error
        return value

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.client = self._resolved_client
        instance.client_business = self._resolved_client_business
        if commit:
            instance.save()
        return instance


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
        fields = ('name', 'phone_number', 'email_address', 'species')


class ClientBusinessForm(DaisyFormMixin, NestedAddressFormMixin, forms.ModelForm):
    class Meta:
        model = ClientBusiness
        fields = ('name', 'phone_number', 'email', 'website')

    def __init__(self, *args, client=None, **kwargs):
        self.client = client
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        client = self.client or getattr(self.instance, 'client', None)
        street = cleaned_data.get('address_street', '').strip()
        if client and street:
            existing = ClientBusiness.objects.filter(
                client=client,
                address__street=street,
                address__city=cleaned_data.get('address_city', '').strip(),
                address__state=cleaned_data.get('address_state', '').strip(),
                address__zip_code=cleaned_data.get('address_zip_code', '').strip(),
            ).exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('This client already has a business at that address.')
        return cleaned_data


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
