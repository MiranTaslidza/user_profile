from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from django.template.loader import render_to_string


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


# slanje poruke na promjenu lozinke
def send_password_changed_email(request, user):
    reset_url = request.build_absolute_uri(
        reverse("password_reset")
    )

    subject = "Your password has been changed"

    message = f"""
        Hello {user.username},

        This email confirms that your account password has been changed.

        If this was you, no further action is required.

        If you do not recognize this activity, you should reset your password immediately using the link below:

        {reset_url}

        If you need additional assistance, please contact support.

        Best regards,
        Security Team
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    
    
# promjena  email slanje podataka na stari email
def send_old_email_change_confirmation(request, email_change):
    """
    Šalje potvrdu na staru email adresu.

    Ovo je prvi sigurnosni korak kod promjene emaila.
    Korisnik prvo mora dokazati da još uvijek ima pristup starom emailu.
    """

    # Pravimo URL za potvrdu starog emaila.
    #
    # Koristimo old_email_token jer se ovaj link odnosi
    # samo na potvrdu starog emaila.
    verification_url = request.build_absolute_uri(
        reverse(
            "email_change_old_verify",
            kwargs={
                "token": email_change.old_email_token
            },
        )
    )


    # Podaci koji će biti poslani HTML template-u.
    context = {
        "user": email_change.user,
        "email_change": email_change,
        "verification_url": verification_url,
    }


    # HTML sadržaj emaila.
    html_message = render_to_string(
        "user_profile/email_change_old_confirmation.html",
        context,
    )


    # Tekstualna verzija emaila.
    text_message = (
        f"Hello {email_change.user.username},\n\n"
        "A request was made to change your email address.\n\n"
        "If you requested this change, confirm it using this link:\n\n"
        f"{verification_url}\n\n"
        "If you did not request this change, ignore this message."
    )


    # Kreiranje email poruke.
    email = EmailMultiAlternatives(
        subject="Confirm email change request",
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email_change.old_email],
    )


    # Dodavanje HTML verzije.
    email.attach_alternative(
        html_message,
        "text/html",
    )


    # Slanje emaila.
    email.send()
    
# slanje emaila na novi mail
def send_new_email_change_confirmation(request, email_change):
    """
    Šalje verifikaciju na novu email adresu.

    Ova funkcija se poziva tek nakon što je korisnik
    potvrdio stari email.
    """

    # Pravljenje linka za potvrdu nove email adrese.
    verification_url = request.build_absolute_uri(
        reverse(
            "email_change_new_verify",
            kwargs={
                "token": email_change.new_email_token
            },
        )
    )


    # Podaci koji se šalju HTML template-u.
    context = {
        "user": email_change.user,
        "email_change": email_change,
        "verification_url": verification_url,
    }


    # HTML sadržaj emaila.
    html_message = render_to_string(
        "email_change_new_confirmation.html",
        context,
    )


    # Tekstualna verzija emaila.
    text_message = (
        f"Hello {email_change.user.username},\n\n"
        "Confirm your new email address using this link:\n\n"
        f"{verification_url}"
    )


    # Kreiranje email poruke.
    email = EmailMultiAlternatives(
        subject="Confirm your new email address",
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email_change.new_email],
    )


    # Dodavanje HTML verzije.
    email.attach_alternative(
        html_message,
        "text/html",
    )


    # Slanje emaila.
    email.send()
    
# slanje emaila na novi email
def send_new_email_change_confirmation(request, email_change):
    """
    Šalje verifikaciju na novu email adresu.

    Ova funkcija se poziva tek nakon što je korisnik
    potvrdio stari email.
    """

    # Pravljenje linka za potvrdu nove email adrese.
    verification_url = request.build_absolute_uri(
        reverse(
            "email_change_new_verify",
            kwargs={
                "token": email_change.new_email_token
            },
        )
    )


    # Podaci koji se šalju HTML template-u.
    context = {
        "user": email_change.user,
        "email_change": email_change,
        "verification_url": verification_url,
    }


    # HTML sadržaj emaila.
    html_message = render_to_string(
        "user_profile/email_change_new_confirmation.html",
        context,
    )


    # Tekstualna verzija emaila.
    text_message = (
        f"Hello {email_change.user.username},\n\n"
        "Confirm your new email address using this link:\n\n"
        f"{verification_url}\n\n"
        "If you did not request this change, ignore this email."
    )


    # Kreiranje email poruke.
    email = EmailMultiAlternatives(
        subject="Confirm your new email address",
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email_change.new_email],
    )


    # Dodavanje HTML verzije.
    email.attach_alternative(
        html_message,
        "text/html",
    )


    # Slanje emaila.
    email.send()
    
# slanje e-mail obavijesti za promjenu korisničkog imena
def send_username_changed_email(user, old_username):
    
    subject = "Your username has been changed"

    message = f"""
        Hello {user.first_name},

        This message confirms that your account username has been changed.

        Previous username:
        {old_username}

        New username:
        {user.username}

        If this was you, no further action is required.

        If you do not recognize this activity, please change your password immediately
        and contact support.

        Best regards,
        Security Team
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )