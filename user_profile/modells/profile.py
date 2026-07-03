from django.db import models
from .user import User

class Profile (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # ime i prezima uzima iz ovog modela 
    avatar = models.ImageField(upload_to='profile_pictures/', blank=True, null=True) # slika
    bio = models.TextField() # biografija
    phone = models.CharField(max_length=20, blank=True) # telefon
    birthday = models.DateField(null=True, blank=True) # datum rođenja
    website = models.URLField(blank=True) # web stranica
    
    LANG_CHOICES = [
        ('en', 'English'),
        ('bs', 'Bosanski'),
        ('de', 'German')
    ]
    language = models.CharField(
        max_length=10,
        choices=LANG_CHOICES,
        default='english'
        ) # ovo se bira iz liste
    
    TIMEZONE_CHOICES = [
        ('Africa/Abidjan', 'Africa/Abidjan'),
        ('Africa/Cairo', 'Africa/Cairo'),
        ('America/Argentina/Buenos_Aires', 'America/Argentina/Buenos_Aires'),
        ('America/Chicago', 'America/Chicago'),
        ('America/New_York', 'America/New_York'),
        ('Asia/Dubai', 'Asia/Dubai'),
        ('Asia/Tokyo', 'Asia/Tokyo'),
        ('Australia/Sydney', 'Australia/Sydney'),
        ('Europe/Berlin', 'Europe/Berlin'),
        ('Europe/London', 'Europe/London'),
        ('Europe/Paris', 'Europe/Paris'),
        ('Europe/Sarajevo', 'Europe/Sarajevo'),
        ('Europe/Zagreb', 'Europe/Zagreb'),
        ('Pacific/Honolulu', 'Pacific/Honolulu'),
        ('UTC', 'UTC'),
    ]
    timezone = models.CharField(
        max_length=65,
        choices=TIMEZONE_CHOICES,
        default='Europe/Sarajevo'
    ) # time zone se bira iz liste
    
    GENDER_CHOICES = [
        ('male', 'Mr'),
        ('female', 'Ms'),
        ('other', 'other')
    ]
    
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='other'
    )
    
    def __str__(self):
        return f"Profile of {self.user.username}"


    
