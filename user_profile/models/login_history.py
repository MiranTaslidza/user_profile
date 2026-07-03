from django.db import models
from .user import User

class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # ime i prezima uzima iz ovog modela 
    ip_address = models.GenericIPAddressField()
    browser = models.CharField(max_length=255)
    operating_system = models.CharField(max_length=255)
    login_time = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.ip_address} - {self.login_time} - {'Success' if self.success else 'Failed'}"
