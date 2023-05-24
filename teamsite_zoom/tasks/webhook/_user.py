import logging
from datetime import datetime

from ...models import ZoomProfile

logger = logging.getLogger(__name__)


def user_updated(message):
    data = message.get("payload", {}).get("object")
    if data is None:
        return

    zoom_id = data["id"]
    try:
        profile = ZoomProfile.objects.get(zoom_id__iexact=zoom_id)
    except ZoomProfile.DoesNotExist:
        logger.warning(f"Zoom profile ID does not exist.", zoom_id, data)
        return

    props = set(data.keys()) - {"id"}
    for prop in props:
        if hasattr(profile, prop):
            setattr(profile, prop, data[prop])
    profile.save()
    logger.info(f"Saved {props} on {profile}")


def user_presence_status_updated(message):
    data = message.get("payload", {}).get("object")
    if data is None:
        return

    zoom_id = data["id"]
    date_time = data["date_time"]
    presence_status = data["presence_status"]

    logger.debug(f"User {zoom_id} changed presence to {presence_status}")

    try:
        profile = ZoomProfile.objects.get(zoom_id__iexact=zoom_id)
    except ZoomProfile.DoesNotExist:
        logger.debug(f"Zoom profile ID {zoom_id} does not exist.", data)
        return

    original_status = profile.presence_status
    profile.presence_status = presence_status
    try:
        profile.presence_status_updated = datetime.fromisoformat(date_time)
    except:
        pass

    profile.save()
    logger.info(
        f"Updated {profile} with presence {original_status} -> {presence_status}"
    )
