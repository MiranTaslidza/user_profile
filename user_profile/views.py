from django.shortcuts import render

# Model obično uvozimo iz models foldera kroz __init__.py ili direktno
from .models.user import User
from .forms.register_form import RegisterForm  # Uvozimo formu iz tvog paketa

from django.urls import reverse_lazy #za preusmjeravanje na drugu stranicu
from django.views.generic.edit import CreateView # za prikaz forme za registraciju korisnika




# prikaz svih korisnika
def all_user(request):
    
    users = User.objects.all()  # Dohvat svih korisnika iz baze podataka
    
    # ukoliko nema nijedan korisnik, prikazujemo poruku
    if not users.exists():
        return render(request, 'user_profile/all_user.html', {'message': 'No users found.'})
    
    
    return render(request, 'user_profile/all_user.html', {'users': users})

# prikaz forme za registraciju korisnika class wiews
class RegisterView(CreateView):
    model = User # uzimam  sve iz modela user
    form_class = RegisterForm # uzimam frmu iz register form
    template_name = 'user_profile/register.html' # proslijeđujem podatke u template register.html
    success_url = reverse_lazy('all_user')  # Preusmjeravanje na prikaz svih korisnika nakon registracije
    