from django.db import models
from .user import User

class SocialAccount(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)

    provider = models.CharField(max_length=50)

    provider_id = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = (
            "provider",
            "provider_id",
        )


    def __str__(self):
        return f"{self.user.username} - {self.provider}"
    