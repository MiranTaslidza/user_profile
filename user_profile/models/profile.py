from django.db import models
from django.conf import settings
from .user import User


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    birthday = models.DateField(null=True, blank=True)
    website = models.URLField(blank=True)

    # Jezik čuvamo kao kod jezika, npr. en, bs, de.
    # choices uzimamo iz Django LANGUAGES postavke.
    language = models.CharField(
        max_length=10,
        choices=settings.LANGUAGES,
        default='en'
    )

    # Vremensku zonu čuvamo kao IANA naziv,
    # npr. Europe/Sarajevo, Europe/Berlin, America/New_York.
    timezone = models.CharField(
        max_length=64,
        default='Europe/Sarajevo'
    )

    GENDER_CHOICES = [
        ('male', 'Mr'),
        ('female', 'Ms'),
        ('other', 'Other'),
    ]

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='other'
    )

    def __str__(self):
        return f"Profile of {self.user.username}"