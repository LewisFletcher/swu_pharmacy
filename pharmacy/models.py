from django.db import models
from simple_history.models import HistoricalRecords

# Create your models here.

class TrackerModel(models.Model):
    '''Abstract base model for tracking creation and modification timestamps.'''
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created')
    updated_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_updated')

    class Meta:
        abstract = True
    
    def __str__(self):
        return f"{self.__class__.__name__} (ID: {self.id})"

class Address(models.Model):
    '''Model containing address information.'''
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}"

class ClientBusiness(models.Model):
    '''Model containing client business information.'''
    name = models.CharField(max_length=100)
    addresses = models.ManyToManyField(Address, related_name='client_businesses')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Client(models.Model):
    '''Model containing client (customer, rancher, etc.) information.'''
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email_address = models.EmailField(blank=True, null=True)
    species_choices = [
        ('Dairy', 'Dairy'),
        ('Beef', 'Beef'),
        ('Sheep', 'Sheep'),
        ('Goat', 'Goat'),
        ('Other', 'Other'),
    ]
    species = models.CharField(max_length=20, choices=species_choices, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Doctor(TrackerModel):
    '''Model containing doctor (veterinarian) information.'''
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    license_expiration_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class MedicationStrength(models.Model):
    '''Model containing medication strength information.'''
    strength = models.CharField(max_length=50)
    unit = models.CharField(max_length=20)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.strength} {self.unit}"

class MedicationSize(models.Model):
    '''Model containing medication size information.'''
    size = models.CharField(max_length=50)
    unit = models.CharField(max_length=20)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.size} {self.unit}"

class MedicationConcentration(models.Model):
    '''Model containing medication concentration information.'''
    concentration = models.CharField(max_length=50)
    unit = models.CharField(max_length=20)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.concentration} {self.unit}"

class Medication(TrackerModel):
    '''Model containing medication information.'''
    brand_name = models.CharField(max_length=100)
    drug_name = models.CharField(max_length=100)
    active_ingredient = models.CharField(max_length=100)
    strength_options = models.ManyToManyField(MedicationStrength, related_name='medications', blank=True)
    sizes = models.ManyToManyField(MedicationSize, related_name='medications', blank=True)
    concentrations = models.ManyToManyField(MedicationConcentration, related_name='medications', blank=True)
    directions = models.TextField(blank=True, null=True)
    dose = models.CharField(max_length=100, blank=True, null=True)
    milk_withhold_period = models.CharField(max_length=100, blank=True, null=True)
    meat_withhold_period = models.CharField(max_length=100, blank=True, null=True)
    approved_age = models.CharField(max_length=100, blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['brand_name']

    def __str__(self):
        return f"{self.brand_name} ({self.drug_name})"

class Practice(TrackerModel):
    '''Model containing practice/clinic information.'''
    name = models.CharField(max_length=100)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Prescription(TrackerModel):
    '''Model containing prescription information.'''
    date_of_prescription = models.DateField(help_text='Date of treatment, presciption, or dispensing.')
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    strength = models.ForeignKey(MedicationStrength, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    practice = models.ForeignKey(Practice, on_delete=models.SET_NULL, null=True, blank=True)
    animals_treated = models.PositiveIntegerField(help_text='Number of animals treated with this prescription.')
    animal_species = models.CharField(max_length=50, blank=True, null=True)
    dosage_instructions = models.TextField(blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True, help_text='Duration of treatment (e.g., 5 days, 2 weeks).')
    expiration_date = models.DateField(blank=True, null=True, help_text='Expiration date of the prescription.')
    route_of_administration = models.CharField(max_length=100, blank=True, null=True, help_text='Route of administration (e.g., oral, injection).')
    number_of_refills = models.PositiveIntegerField(default=0, help_text='Number of refills allowed for this prescription.')
    cautionary_notes = models.TextField(blank=True, null=True, help_text='Any cautionary notes or warnings related to the prescription.')
    prescription_label = models.FileField(upload_to='prescription_labels/', blank=True, null=True, help_text='The label that will be printed and attached to the prescription container.')
    history = HistoricalRecords()

    class Meta:
        ordering = ['-date_of_prescription', '-created_at']

    def __str__(self):
        return f"Prescription for {self.client.name} - {self.medication.brand_name} ({self.date_of_prescription})"
