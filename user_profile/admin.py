from django.contrib import admin
from .models import User, Profile, UserSettings, Notification, SocialAccount, LoginHistory, AuditLog, Address

# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(UserSettings)
admin.site.register(Notification)
admin.site.register(SocialAccount)
admin.site.register(LoginHistory)
admin.site.register(AuditLog)
admin.site.register(Address)
