from django.db import models
from .user import User

class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    refresh_token = models.CharField(max_length=255)
    browser = models.CharField(max_length=255)
    ip = models.GenericIPAddressField()
    device_name = models.CharField(max_length=255)
    last_used = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.device_name} - {self.ip}"
