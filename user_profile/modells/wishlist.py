from django.db import models
from .user import User

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # povezuje se sa modelom User
    name = models.CharField(max_length=255) # ime liste zelja
    created_at = models.DateTimeField(auto_now_add=True) # datum i vrijeme kada je lista zelja kreirana
    
    def __str__(self):
        return f"Wishlist '{self.name}' for {self.user.username}"