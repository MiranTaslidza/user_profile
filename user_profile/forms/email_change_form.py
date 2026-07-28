from django import forms
from django.contrib.auth import get_user_model


User = get_user_model()


class EmailChangeForm(forms.Form):
    """
    Forma za pokretanje promjene email adrese.
    Korisnik unosi novu email adresu i potvrđuje trenutnom lozinkom.
    """

    new_email = forms.EmailField(
        label="New email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter new email address",
                "autocomplete": "email",
            }
        )
    )

    current_password = forms.CharField(
        label="Current password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter current password",
                "autocomplete": "current-password",
            }
        )
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Trenutno prijavljeni korisnik
        self.user = user


    def clean_new_email(self):
        """
        Provjera nove email adrese.
        """

        new_email = self.cleaned_data["new_email"].lower().strip()

        if self.user.email.lower() == new_email:
            raise forms.ValidationError(
                "New email must be different from current email."
            )

        if User.objects.filter(email__iexact=new_email).exists():
            raise forms.ValidationError(
                "This email address is already in use."
            )

        return new_email


    def clean_current_password(self):
        """
        Provjera trenutne lozinke.
        """

        password = self.cleaned_data["current_password"]

        if not self.user.check_password(password):
            raise forms.ValidationError(
                "Incorrect password."
            )

        return password