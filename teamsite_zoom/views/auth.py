from django.conf import settings as django_settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from sf_zoom.zoom import URL_AUTH
from sf_zoom.zoom.auth import get_credentials

CLIENT_ID = django_settings.ZOOM["CLIENT_ID"]


@csrf_exempt
def oauth_view(request):
    if request.method != "GET":
        return HttpResponse(content="Method Not Allowed", status=405)

    host = request.headers["host"]
    redirect_uri = f"https://{host}/oauth/zoom"

    if request.GET.get("code") is not None:
        get_credentials(request.GET["code"], redirect_uri)
        return redirect(f"{request.scheme}://{host}/admin/")
    else:
        return redirect(
            f"{URL_AUTH}?response_type=code&client_id={CLIENT_ID}&redirect_uri={redirect_uri}"
        )
