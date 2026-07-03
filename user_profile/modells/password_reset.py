from django.db import models
from .user import User

class PasswordReset(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE) # ime i prezima uzima iz ovog modela
    token = models.CharField(max_length=255) # token za verifikaciju resetiranja lozinke
    expires_at = models.DateTimeField() # datum i vrijeme isteka tokena
    used = models.BooleanField(default=False) # da li je token iskorišten
    created_at = models.DateTimeField(auto_now_add=True) # datum i vrijeme stvaranja zahtjeva za resetiranje lozinke
    
    def __str__(self):
        return f"Password reset request for {self.user.username} - Token: {self.token}"
        
    
