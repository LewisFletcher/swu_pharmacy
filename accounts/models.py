from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# Override user model

class User(AbstractUser):
    practice = models.ForeignKey(
        'pharmacy.Practice', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff'
    )
