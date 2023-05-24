import json
import logging

from django.conf import settings as django_settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from sf_zoom.tasks import on_message_received

logger = logging.getLogger(__name__)

VERIFICATION_TOKEN = django_settings.ZOOM["VERIFICATION_TOKEN"]


@csrf_exempt
def view(request):
    if request.method != "POST":
        return HttpResponse(content="Method Not Allowed", status=405)

    body = request.body.decode("utf-8")
    authorization = request.headers.get("authorization")
    if authorization != VERIFICATION_TOKEN:
        logging.error("Failed to verify Zoom message token")
        return HttpResponse(content="Unauthorized", status=401)

    try:
        message_data = json.loads(body)
    except ValueError as e:
        logger.error("Failed to parse Slack message body")
        return HttpResponse(content="Bad Request", status=400)

    on_message_received.delay(message_data)

    return HttpResponse("OK")
