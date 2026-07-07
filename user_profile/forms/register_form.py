from django import forms
# za  registraciju korisnika profesionalno se koristi 
from django.contrib.auth.forms import UserCreationForm
from user_profile.models.user import User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    
    # sakrivanje helpp teksta ipostavljanje klase form-control za polja lozinke
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ručno dodajemo polja za lozinku u polja koja forma renderira
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
        # Ovdje uklanjamo help_text kako bi se sakrio dok korisnik ne pogriješi
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None