from django.db import models
from .user import User

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # ime i prezima uzima iz ovog modela 
    country = models.CharField(max_length=100, blank=True) # država
    city = models.CharField(max_length=100, blank=True) # grad
    postal_code = models.CharField(max_length=10, blank=True) #poštarski kod
    street = models.CharField(max_length=100, blank=True) # ulica 
    number =models.CharField(blank=True) # broj ulice
    is_default = models.BooleanField(default=False) # glavna ili zadana adresa
    
    def __str__(self):
        return f"{self.city}, {self.street} {self.number}"