from django.db import models
from .user import User

class BlockedUser(models.Model):

    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocker') # korisnik koji blokira
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked') # korisnik koji je blokiran
    created_at = models.DateTimeField(auto_now_add=True) # datum i vrijeme kada je korisnik blokiran
    
    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username} at {self.created_at}"
