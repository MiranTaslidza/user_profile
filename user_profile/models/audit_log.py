from django.db import models
from .user import User

class AuditLog(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE) # povezuje se sa modelom User
    action = models.CharField(max_length=255) # opis akcije koja je izvršena
    created_at = models.DateTimeField(auto_now_add=True) # datum i vrijeme kada je akcija izvršena
    ip = models.GenericIPAddressField() # IP adresa sa koje je akcija izvršena
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}"
