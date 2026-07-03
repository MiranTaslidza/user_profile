from django.db import models
from .user import User


class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # ime i prezima uzima iz ovog modela
    token = models.CharField(max_length=255) # token za verifikaciju email adrese
    expires_at = models.DateTimeField() # datum i vrijeme isteka tokena
    verified = models.BooleanField(default=False) # da li je email adresa verifikovana
    created_at = models.DateTimeField(auto_now_add=True) # datum i vrijeme stvaranja zahtjeva za verifikaciju email adrese
    
    def __str__(self):
        return f"{self.user.username} - {self.token} - {self.verified}"
