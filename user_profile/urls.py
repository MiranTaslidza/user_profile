from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.all_user, name='all_user'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    
    # verifikacija maila
    path("verify-email/<uidb64>/<token>/", views.verify_email, name="verify_email"),
    path("verification-email-sent/", views.verification_email_sent,name="verification_email_sent"),
    path("resend-verification-email/", views.ResendVerificationEmailView.as_view(), name="resend_verification_email"),
    
    # # url za  zaboravljen password
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name="user_profile/password_reset_form.html", email_template_name="user_profile/password_reset_email.html", subject_template_name="user_profile/password_reset_subject.txt"), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="user_profile/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="user_profile/password_reset_confirm.html"), name="password_reset_confirm" ),
    path("reset/complete/", auth_views.PasswordResetCompleteView.as_view(template_name="user_profile/password_reset_complete.html"), name="password_reset_complete"),
    
]
