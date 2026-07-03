from django.db import models
from .user import User

class EmailChange(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE) # ime i prezima uzima iz ovog modela
    old_email = models.EmailField() # stara email adresa
    new_email = models.EmailField() # nova email adresa
    token = models.CharField(max_length=255) # token za verifikaciju promjene email adrese
    verified = models.BooleanField(default=False) # da li je promjena email adrese verifikovana
    created_at = models.DateTimeField(auto_now_add=True) # datum i vrijeme stvaranja zahtjeva za promjenu email adrese
    expires_at = models.DateTimeField() # Da token ne važi zauvijek.
    used_at = models.DateTimeField(null=True, blank=True) # kada je prmjena izvršena
    is_active = models.BooleanField(default=True) # da se može poništiti zahtjev
    
    def __str__(self):
        return f"{self.user.username} requested email change from {self.old_email} to {self.new_email} at {self.created_at}"
