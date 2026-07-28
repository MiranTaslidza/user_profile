from django.db import models
from .user import User


class EmailChange(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    old_email = models.EmailField()
    new_email = models.EmailField()

    # potvrda starog emaila
    old_email_token = models.CharField(max_length=255, unique=True)
    old_email_verified = models.BooleanField(default=False)
    old_email_verified_at = models.DateTimeField(null=True, blank=True)

    # potvrda novog emaila
    new_email_token = models.CharField(max_length=255, unique=True)
    new_email_verified = models.BooleanField(default=False)
    new_email_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField( auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return (
            f"{self.user.username} "
            f"email change "
            f"{self.old_email} → {self.new_email}"
        )
