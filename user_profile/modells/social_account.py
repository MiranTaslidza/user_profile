from django.db import models
from .user import User

Class SocialAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # povezuje se sa modelom User
    provider = models.CharField(max_length=255) # ime provajdera (npr. Google, Facebook)
    provider_id = models.CharField(max_length=255) # ID korisnika kod provajdera
    created_at = models.DateTimeField(auto_now_add=True) # datum i vrijeme kada je račun dodan
    
    def __str__(self):
        return f"{self.user.username} - {self.provider} - {self.provider_id}"
    