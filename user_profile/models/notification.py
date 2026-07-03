from django.db import models
from .user import User

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # ime i prezima uzima iz ovog modela 
    title = models.CharField(max_length=255) # naslov notifikacije
    message = models.TextField() # sadržaj notifikacije
    is_read = models.BooleanField(default=False) # da li je notifikacija pročitana
    created_at = models.DateTimeField(auto_now_add=True) # datum i vrijeme stvaranja notifikacije
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"
