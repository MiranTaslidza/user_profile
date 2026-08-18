import requests
from django.conf import settings


# Google OAuth endpoint na koji šaljemo korisnika
GOOGLE_AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"

# Google endpoint koji koristimo za razmjenu authorization code-a
# za access token
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

# Google endpoint sa kojeg uzimamo podatke o prijavljenom korisniku
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


def get_google_authorization_url():
    """
    Kreira URL na koji ćemo poslati korisnika
    kada klikne na "Login with Google".
    """

    params = {
        # Client ID naše Django aplikacije
        "client_id": settings.GOOGLE_CLIENT_ID,

        # Google nakon uspješne prijave vraća korisnika
        # na ovaj URL.
        "redirect_uri": "http://127.0.0.1:8000/google/callback/",

        # Authorization Code flow.
        # Google će nam vratiti privremeni authorization code.
        "response_type": "code",

        # Podaci koje tražimo od Google-a.
        "scope": "openid email profile",

        # Omogućava offline pristup kada je potreban refresh token.
        "access_type": "offline",
    }

    # Pretvaramo dictionary u URL query parametre.
    from urllib.parse import urlencode

    return f"{GOOGLE_AUTHORIZATION_URL}?{urlencode(params)}"


def exchange_code_for_token(code):
    """
    Prima authorization code koji je Google poslao
    našem callback view-u.

    Taj code zatim mijenjamo za Google access token.
    """

    data = {
        "code": code,

        "client_id": settings.GOOGLE_CLIENT_ID,

        "client_secret": settings.GOOGLE_CLIENT_SECRET,

        "redirect_uri": "http://127.0.0.1:8000/google/callback/",

        "grant_type": "authorization_code",
    }

    response = requests.post(
        GOOGLE_TOKEN_URL,
        data=data,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def get_google_user_info(access_token):
    """
    Koristi Google access token da dobije podatke
    o trenutno prijavljenom Google korisniku.
    """

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.get(
        GOOGLE_USERINFO_URL,
        headers=headers,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()