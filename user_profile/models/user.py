from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    # Tvoja polja...
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username