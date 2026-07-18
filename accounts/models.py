from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# Override user model

class User(AbstractUser):
    pass