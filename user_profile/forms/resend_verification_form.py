from django import forms


class ResendVerificationForm(forms.Form):
    email = forms.EmailField(
        label="Email adresa",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Unesite email adresu",
            }
        ),
    )
    