import base64
from datetime import datetime, timedelta, timezone

import requests
from django.conf import settings as django_settings

from ..models import OauthToken
from ..zoom import URL_TOKEN

CLIENT_ID = django_settings.ZOOM_CLIENT_ID
CLIENT_SECRET = django_settings.ZOOM_CLIENT_SECRET
SERVICE_NAME = "zoom"


def __update_token(creds):
    if "access_token" not in creds:
        raise Exception("No access token in credentials", creds)

    try:
        token = OauthToken.objects.get(service=SERVICE_NAME)
    except OauthToken.DoesNotExist:
        token = OauthToken(service=SERVICE_NAME)

    now = datetime.now(tz=timezone.utc)

    token.access_token = creds["access_token"]
    token.refresh_token = creds["refresh_token"]
    token.expires = now + timedelta(seconds=creds["expires_in"])
    token.save()

    return token


def __get_auth_headers():
    auth = base64.b64encode(bytes(f"{CLIENT_ID}:{CLIENT_SECRET}", "utf-8")).decode(
        "ascii"
    )
    return {"Authorization": f"Basic {auth}"}


def get_credentials(code, redirect_uri):
    querystring = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }
    response = requests.post(
        URL_TOKEN, headers=__get_auth_headers(), params=querystring
    )
    token = __update_token(response.json())
    return token.access_token


def get_access_token():
    token = OauthToken.objects.get(service=SERVICE_NAME)
    almost_expired = datetime.now(tz=timezone.utc) + timedelta(seconds=30)
    if token.expires <= almost_expired:
        querystring = {
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
        }
        response = requests.post(
            URL_TOKEN, headers=__get_auth_headers(), params=querystring
        )
        token = __update_token(response.json())

    return token.access_token
