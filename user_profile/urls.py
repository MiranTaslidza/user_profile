from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.all_user, name='all_user'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path("verify-email/<uidb64>/<token>/", views.verify_email, name="verify_email"),
    path("verification-email-sent/", views.verification_email_sent,name="verification_email_sent"),
    path("resend-verification-email/", views.ResendVerificationEmailView.as_view(), name="resend_verification_email"),

]
