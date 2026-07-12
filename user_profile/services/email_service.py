from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse

# funkcija za slanje emaila
def send_verification_email(request, user): 
    uid = urlsafe_base64_encode(force_bytes(user.pk)) # kodiranje ID korisnika u base64 format kako bi se mogao sigurno koristiti u URL-u.
    token = default_token_generator.make_token(user) # generisanje tokena za verifikaciju korisnika. Token se koristi za potvrdu identiteta korisnika prilikom verifikacije email adrese.

    # kreiranje URL-a za verifikaciju email adrese. Koristi se funkcija reverse za generisanje URL-a na osnovu imena rute "verify_email" i prosleđuje se uid i token kao parametri.
    verification_path = reverse(
        "verify_email",
        kwargs={
            "uidb64": uid,
            "token": token,
        },
    )

    # kreiranje punog URL-a za verifikaciju email adrese. Funkcija build_absolute_uri generiše apsolutni URL na osnovu relativnog puta verification_path. Ovaj URL će biti poslat korisniku u emailu kako bi mogao potvrditi svoju email adresu.
    verification_url = request.build_absolute_uri(verification_path)

    # kreiranje poruke za email verifikaciju. Poruka sadrži pozdrav korisniku, uputstvo da klikne na link za verifikaciju i sam link (verification_url). Takođe, uključuje napomenu da ako korisnik nije napravio račun, može zanemariti poruku.
    subject = "Potvrda email adrese"

    # kreiranje poruke za email verifikaciju. Poruka sadrži pozdrav korisniku, uputstvo da klikne na link za verifikaciju i sam link (verification_url). Takođe, uključuje napomenu da ako korisnik nije napravio račun, može zanemariti poruku.
    message = (
        f"Pozdrav {user.username},\n\n"
        "Kliknite na sljedeći link kako biste potvrdili email adresu:\n\n"
        f"{verification_url}\n\n"
        "Ako niste napravili ovaj račun, zanemarite poruku."
    )

    # slanje emaila korisniku sa linkom za verifikaciju. Funkcija send_mail šalje email sa zadatim subjectom, porukom, adresom pošiljaoca (DEFAULT_FROM_EMAIL iz settings.py) i listom primalaca (u ovom slučaju samo korisnikova email adresa). Ako dođe do greške prilikom slanja emaila, postavlja se fail_silently na False kako bi se greška prijavila.
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

