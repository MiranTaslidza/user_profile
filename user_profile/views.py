from django.shortcuts import render
from django.urls import reverse_lazy #za preusmjeravanje na drugu stranicu
from django.views.generic.edit import CreateView # za prikaz forme za registraciju korisnika
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http import HttpResponse # za prikaz poruke nakon slanja emaila
from django.contrib.auth.tokens import default_token_generator # za generisanje tokena za verifikaciju email adrese
from django.utils.http import  urlsafe_base64_decode # za kodiranje ID korisnika u base64 format na siguran način za URL
from django.shortcuts import redirect, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic.edit import FormView
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from datetime import timedelta
from django.views import View


# Model obično uvozimo iz models foldera kroz __init__.py ili direktno
from .models.user import User
from .models.email_change import EmailChange
from .models.social_account import SocialAccount

# forme
from .forms.register_form import RegisterForm  # Uvozimo formu iz tvog paketa
from .forms.login_form import CustomLoginForm  # Uvozimo formu za login
from .services.email_service import send_verification_email, send_password_changed_email, send_old_email_change_confirmation, send_new_email_change_confirmation, send_username_changed_email
from .forms.resend_verification_form import ResendVerificationForm
from .forms.email_change_form import EmailChangeForm
from .forms.username_change_form import UsernameChangeForm
from .services.google_oauth_service import get_google_authorization_url, exchange_code_for_token, get_google_user_info




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

    
# google oauth login view
class GoogleLoginView(View):
    """
    Pokreće Google OAuth prijavu.

    Kada korisnik otvori ovaj view,
    Django ga preusmjerava na Google login stranicu.
    """

    def get(self, request):

        # Service kreira Google OAuth URL.
        google_url = get_google_authorization_url()

        # Šaljemo korisnika na Google.
        return redirect(google_url)
    
    
# Google login Callback View.
class GoogleCallbackView(View):
    """
    Prima odgovor koji Google šalje nakon uspješne prijave.

    Google nam šalje privremeni authorization code.
    Taj code mijenjamo za access token,
    a zatim pomoću access tokena uzimamo podatke korisnika.
    """

    def get(self, request):

        # Uzimamo authorization code koji je Google
        # poslao kroz URL:
        #
        # /google/callback/?code=XXXXXXXX
        code = request.GET.get("code")

        # Ako Google nije poslao code,
        # ne možemo nastaviti OAuth proces.
        if not code:
            return redirect("login")

        # Authorization code mijenjamo za Google token.
        token_data = exchange_code_for_token(code)

        # Uzimamo access token iz odgovora Google-a.
        access_token = token_data.get("access_token")

        # Ako nismo dobili access token,
        # OAuth proces nije uspješno završen.
        if not access_token:
            return redirect("login")

        # Pomoću access tokena tražimo podatke
        # o Google korisniku.
        google_user = get_google_user_info(access_token)

        # Za sada samo ispisujemo podatke u terminal.
        # Ovo ćemo kasnije zamijeniti stvarnim loginom
        # i povezivanjem User + SocialAccount modela.
        print("GOOGLE USER:", google_user)

        return redirect("/")
    


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
    
# da korisnik postane stvarno pijavljen GoogleCallbackViewsUser
class GoogleCallbackView(View):

    def get(self, request):

        # Uzimamo authorization code koji Google vraća
        code = request.GET.get("code")

        # Ako code ne postoji, prekidamo login
        if not code:
            messages.error(request, "Google login failed.")
            return redirect("login")

        # Mijenjamo code za access token
        token_data = exchange_code_for_token(code)

        # Uzimamo access token
        access_token = token_data.get("access_token")

        # Ako nema access tokena, login nije uspio
        if not access_token:
            messages.error(request, "Google authentication failed.")
            return redirect("login")

        # Uzimamo podatke Google korisnika
        google_user = get_google_user_info(access_token)

        # Google jedinstveni ID korisnika
        google_id = google_user.get("sub")

        # Email korisnika
        email = google_user.get("email")

        # Da li je Google email verificiran
        email_verified = google_user.get("email_verified", False)

        # Ime korisnika
        first_name = google_user.get("given_name", "")

        # Prezime korisnika
        last_name = google_user.get("family_name", "")

        # Bez Google ID-a ne možemo nastaviti
        if not google_id:
            messages.error(request, "Google user ID is missing.")
            return redirect("login")

        # Ne prihvatamo neverifikovan Google email
        if not email or not email_verified:
            messages.error(request, "Google email is not verified.")
            return redirect("login")

        # Prvo provjeravamo da li Google nalog već postoji
        social_account = SocialAccount.objects.filter(
            provider="google",
            provider_id=google_id
        ).select_related("user").first()

        if social_account:

            # Ako postoji SocialAccount, koristimo povezanog korisnika
            user = social_account.user

        else:

            # Provjeravamo postoji li User sa istim emailom
            user = User.objects.filter(
                email__iexact=email
            ).first()

            if user:

                # Povezujemo postojeći User sa Google nalogom
                SocialAccount.objects.create(
                    user=user,
                    provider="google",
                    provider_id=google_id
                )

            else:

                # Kreiramo osnovni username iz email adrese
                base_username = email.split("@")[0]

                username = base_username

                counter = 1

                # Ako username postoji, dodajemo broj
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1

                # Kreiramo novog korisnika
                user = User.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    is_verified=True
                )

                # Google korisnik nema lokalnu lozinku
                user.set_unusable_password()

                user.save()

                # Kreiramo SocialAccount vezu
                SocialAccount.objects.create(
                    user=user,
                    provider="google",
                    provider_id=google_id
                )

        # Ne dozvoljavamo login neaktivnom korisniku
        if not user.is_active:
            messages.error(request, "This account is inactive.")
            return redirect("login")

        # Prijavljujemo korisnika u Django sesiju
        login(
            request,
            user,
            backend="django.contrib.auth.backends.ModelBackend"
        )

        messages.success(
            request,
            "You have successfully signed in with Google."
        )

        return redirect("all_user")

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
    
# promjena password-a
class CustomPasswordChangeView(PasswordChangeView):
    template_name = "user_profile/password_change_form.html"
    # success_url = reverse_lazy("password_change_done")
    success_url = reverse_lazy("all_user")
    # da bi me poruka prikazivala mmora iči u funkciju
    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Your password has been updated successfully."
        )

        # ovdje postavljam logiku o slanju maila
        send_password_changed_email(
            request=self.request,
            user=self.request.user,
        )

        return response


# promjena e-mail -a

# pokretanje promjene e-mail -a i slanje linka na stari e-mail
class EmailChangeView(LoginRequiredMixin, FormView):
    """
    View za pokretanje promjene email adrese.
    Korisnik unosi novi email i trenutnu lozinku.
    """

    form_class = EmailChangeForm

    template_name = "user_profile/email_change.html"

    success_url = reverse_lazy("all_user")


    def get_form_kwargs(self):
        """
        Šaljemo trenutno prijavljenog korisnika formi.
        """

        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user

        return kwargs


    def form_valid(self, form):
        """
        Ako je forma ispravna:
        - kreira EmailChange
        - šalje potvrdu na stari email
        """


        email_change = EmailChange.objects.create(

            # korisnik koji traži promjenu
            user=self.request.user,

            # trenutni email korisnika
            old_email=self.request.user.email,

            # novi email iz forme
            new_email=form.cleaned_data["new_email"],

            # token za potvrdu starog emaila
            old_email_token=get_random_string(64),

            # token za novi email pripremamo odmah
            # ali ga koristimo tek poslije potvrde starog emaila
            new_email_token=get_random_string(64),

            # zahtjev važi određeni period
            expires_at=timezone.now() + timedelta(hours=24),
        )


        # šaljemo link na STARI email
        send_old_email_change_confirmation(
            self.request,
            email_change,
        )


        messages.success(
            self.request,
            "Confirmation link has been sent to your current email address."
        )


        return super().form_valid(form)


# uzima potvrdu sa starog emaila
class EmailChangeOldVerifyView(View):
    """
    View za potvrdu zahtjeva preko starog emaila.

    Korisnik prvo mora potvrditi da ima pristup staroj email adresi.
    Tek nakon toga šaljemo potvrdu na novi email.
    """

    def get(self, request, token):
        """
        Obrada klika na link iz starog emaila.
        """

        # Pronalazimo aktivni zahtjev za promjenu emaila
        email_change = get_object_or_404(
            EmailChange,
            old_email_token=token,
            is_active=True,
        )


        # Provjera da li je zahtjev istekao
        if email_change.expires_at < timezone.now():

            email_change.is_active = False
            email_change.save()

            messages.error(
                request,
                "This email change request has expired."
            )

            return redirect("all_user")


        # Označavamo da je stari email potvrđen
        email_change.old_email_verified = True

        email_change.save()


        # Nakon potvrde starog emaila
        # šaljemo verifikaciju na novi email
        send_new_email_change_confirmation(
            request,
            email_change,
        )


        messages.success(
            request,
            "Your old email has been confirmed. Check your new email address."
        )


        return redirect("all_user")
    

# završna potvrda novog emaila i promjena korisničkog emaila
class EmailChangeNewVerifyView(View):
    """
    View za potvrdu nove email adrese.

    Ovaj view se poziva kada korisnik klikne
    link koji je dobio na novu email adresu.

    Tek nakon ove potvrde se mijenja User.email.
    """

    def get(self, request, token):
        """
        Obrada klika na link iz novog emaila.
        """


        # Pronalazimo aktivni zahtjev
        # preko tokena nove email adrese.
        email_change = get_object_or_404(
            EmailChange,
            new_email_token=token,
            is_active=True,
        )


        # Provjera isteka zahtjeva.
        if email_change.expires_at < timezone.now():

            email_change.is_active = False
            email_change.save()

            messages.error(
                request,
                "This email change request has expired."
            )

            return redirect("all_user")


        # Sigurnosna provjera:
        # stari email mora biti potvrđen prije novog.
        if not email_change.old_email_verified:

            messages.error(
                request,
                "Old email address has not been verified."
            )

            return redirect("all_user")


        # Označavamo novi email kao potvrđen.
        email_change.new_email_verified = True

        email_change.new_email_verified_at = timezone.now()

        email_change.save()


        # Završna promjena email adrese korisnika.
        user = email_change.user

        user.email = email_change.new_email

        user.save()


        # Zatvaramo zahtjev.
        email_change.used_at = timezone.now()

        email_change.is_active = False

        email_change.save()


        messages.success(
            request,
            "Your email address has been successfully changed."
        )


        return redirect("all_user")
    
    
# promjena username 
    """
    u parametrima
    LoginRequiredMixin -da samo prijavljen korisnik može promijeniti ime
    FormView je samo da koristim formu
    """
class UserNameChange(LoginRequiredMixin, FormView):
    """
    Promjena korisničkog imena.

    LoginRequiredMixin:
    - samo prijavljeni korisnici mogu mijenjati username.

    FormView:
    - koristi Django formu za unos i validaciju podataka.
    """

    form_class = UsernameChangeForm

    template_name = "user_profile/username_change.html"

    success_url = "/"


    def get_form_kwargs(self):
        """
        Šaljemo trenutnog korisnika formi.

        Forma treba korisnika zbog provjere:
        - da novi username nije isti kao trenutni
        - da novi username ne koristi drugi korisnik
        """

        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user

        return kwargs



    def form_valid(self, form):
        """
        Izvršava se kada je forma uspješno prošla validaciju.
        """

        user = self.request.user


        # Čuvamo staro korisničko ime
        # prije nego ga promijenimo.
        old_username = user.username


        # Postavljamo novo korisničko ime.
        user.username = form.cleaned_data["new_username"]


        # Snimamo promjenu u bazu.
        user.save()


        # Šaljemo sigurnosnu obavijest na email.
        send_username_changed_email(
            user,
            old_username
        )


        return super().form_valid(form)