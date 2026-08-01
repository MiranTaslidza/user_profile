from django import forms
from user_profile.models.user import User


class UsernameChangeForm(forms.Form):

    new_username = forms.CharField(
        max_length=150
    )

    current_password = forms.CharField(
        widget=forms.PasswordInput
    )


    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user


    def clean_new_username(self):

        new_username = self.cleaned_data["new_username"]

        if new_username == self.user.username:
            raise forms.ValidationError(
                "The new username is the same as your current username."
            )


        if User.objects.filter(
            username=new_username
        ).exclude(
            id=self.user.id
        ).exists():

            raise forms.ValidationError(
                "This username is already in use."
            )


        return new_username