from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Korisničko ime ili email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Lozinka'})
    )

    def clean(self):
        username_or_email = self.cleaned_data.get("username")

        try:
            validate_email(username_or_email)
        except ValidationError:
            # Korisnik nije unio email.
            pass
        else:
            # Korisnik je unio email.
            User = get_user_model()

            if user := User.objects.filter(email=username_or_email).first():
                self.cleaned_data["username"] = user.username
                

        cleaned_data = super().clean()

        if self.user_cache and not self.user_cache.is_verified:
            raise ValidationError(
                "You must first verify your email address."
            )

        return cleaned_data
    
        