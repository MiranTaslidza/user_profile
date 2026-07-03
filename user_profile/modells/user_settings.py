from django.db import models
from .user import User

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # povezuje se sa modelom User
    dark_mode = models.BooleanField(default=False)
    currency = models.CharField(max_length=3, default='USD')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Settings for {self.user.username}"
