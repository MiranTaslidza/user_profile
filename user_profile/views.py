from django.shortcuts import render
from django.urls import reverse_lazy #za preusmjeravanje na drugu stranicu
from django.views.generic.edit import CreateView # za prikaz forme za registraciju korisnika
from django.contrib.auth.views import LoginView # za prikaz forme za login korisnika
from django.http import HttpResponse # za prikaz poruke nakon slanja emaila
from django.contrib.auth.tokens import default_token_generator # za generisanje tokena za verifikaciju email adrese
from django.utils.http import  urlsafe_base64_decode # za kodiranje ID korisnika u base64 format na siguran način za URL
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic.edit import FormView

# Model obično uvozimo iz models foldera kroz __init__.py ili direktno
from .models.user import User

# forme
from .forms.register_form import RegisterForm  # Uvozimo formu iz tvog paketa
from .forms.login_form import CustomLoginForm  # Uvozimo formu za login
from .services.email_service import send_verification_email
from .forms.resend_verification_form import ResendVerificationForm



# prikaz svih korisnika
def all_user(request):
    
    users = User.objects.all()  # Dohvat svih korisnika iz baze podataka
    
    # ukoliko nema nijedan korisnik, prikazujemo poruku
    if not users.exists():
        return render(request, 'user_profile/all_user.html', {'message': 'No users found.'})
    
    
    return render(request, 'user_profile/all_user.html', {'users': users})




# login class login view
class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'user_profile/login.html'
    # preusmejrenje rediract ide ovako akonema ovoga ide na account/profile to jeste vodi na profilnu stranicu.
    def get_success_url(self):
        return reverse_lazy('all_user')
    


# funkcija za verifikaciju emaila
def verify_email(request, uidb64, token):
    try:
        # Dekodira ID korisnika iz URL-a
        uid = urlsafe_base64_decode(uidb64).decode()

        # Pronalazi korisnika u bazi
        user = User.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Provjerava da li korisnik postoji i da li je token ispravan
    if user is not None and default_token_generator.check_token(user, token):

        user.is_verified = True
        user.save()

        messages.success(
            request,
            "Email je uspješno verifikovan. Možete se prijaviti."
        )

        return redirect("login")

    return HttpResponse("Verifikacioni link nije ispravan ili je istekao.")
    


# prikaz forme za registraciju korisnika
class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = "user_profile/register.html"

    def form_valid(self, form):
        # Sačuvaj korisnika
        self.object = form.save()
        

        # Pošalji verifikacijski email
        send_verification_email(
            self.request,
            self.object,
        )

        # Preusmjeri korisnika na stranicu sa obavještenjem
        return redirect("verification_email_sent")
    
    
# verifikacijski email template
def verification_email_sent(request):
    return render(
        request,
        "user_profile/verification_email_sent.html"
    )
    


# resend verifikacijski mail
class ResendVerificationEmailView(FormView):
    template_name = "user_profile/resend_verification_email.html"
    form_class = ResendVerificationForm
    success_url = reverse_lazy("verification_email_sent")

    def form_valid(self, form):
        email = form.cleaned_data["email"]

        user = User.objects.filter(
            email__iexact=email,
            is_verified=False,
        ).first()

        if user is not None:
            send_verification_email(
                self.request,
                user,
            )

        messages.success(
            self.request,
            "Ako postoji neverifikovan račun sa tom email adresom, "
            "novi verifikacijski email je poslan."
        )

        return super().form_valid(form)
    
# zaboravljen password

