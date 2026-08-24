from django import forms
from zoneinfo import available_timezones

from user_profile.models.profile import Profile


class ProfileUpdateForm(forms.ModelForm):

    # Polja iz User modela
    first_name = forms.CharField(
        max_length=150,
        required=False
    )

    last_name = forms.CharField(
        max_length=150,
        required=False
    )

    # Timezone pravimo kao dropdown.
    # Lista se automatski uzima iz dostupnih IANA vremenskih zona.
    timezone = forms.ChoiceField(
        choices=[
            (timezone, timezone)
            for timezone in sorted(available_timezones())
        ]
    )

    class Meta:
        model = Profile

        fields = [
            'first_name',
            'last_name',
            'bio',
            'phone',
            'birthday',
            'website',
            'language',
            'timezone',
            'gender',
        ]

        widgets = {
            'bio': forms.Textarea(
                attrs={
                    'rows': 4,
                }
            ),

            'birthday': forms.DateInput(
                attrs={
                    'type': 'date',
                }
            ),
        }


    def __init__(self, *args, **kwargs):
        """
        Kada se forma otvori, popunjavamo first_name i last_name
        iz povezanog User modela.
        """

        super().__init__(*args, **kwargs)

        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name


    def save(self, commit=True):
        """
        Profile polja sprema ModelForm automatski.

        first_name i last_name pripadaju User modelu,
        pa njih spremamo posebno.
        """

        profile = super().save(commit=False)

        user = profile.user

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            profile.save()

        return profile