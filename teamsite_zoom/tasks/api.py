from __future__ import absolute_import, unicode_literals

import logging

import requests

from ..models import AssignedNumber, CallingPlan, ZoomProfile
from ..zoom.auth import get_access_token

API_ROOT = "https://api.zoom.us/v2"
URL_USERS = f"{API_ROOT}/users"
URL_PHONE_USERS = f"{API_ROOT}/phone/users"
URL_PHONE_NUMBERS = f"{API_ROOT}/phone/numbers"

DEFAULT_PAGE_SIZE = 60
DEFAULT_QUERY = {}

logger = logging.getLogger(__name__)


def __prune_empty_string(value):
    if value is None:
        return None
    value = value.strip()
    if len(value) == 0:
        return None
    return value


def __get_users(page_number=1):
    token = get_access_token()

    querystring = {"page_number": page_number, "page_size": "200", "status": "active"}
    headers = dict(Authorization=f"Bearer {token}")

    response = requests.request("GET", URL_USERS, headers=headers, params=querystring)
    return response.json()


def __tokenized_page_request(
    url, next_page_token=None, page_size=DEFAULT_PAGE_SIZE, query=DEFAULT_QUERY
):
    querystring = {**query, "page_size": page_size}
    if next_page_token is not None:
        querystring["next_page_token"] = next_page_token
    headers = dict(Authorization=f"Bearer {get_access_token()}")
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()


def __tokenized_all_pages(
    url, property, page_size=DEFAULT_PAGE_SIZE, query=DEFAULT_QUERY
):
    api_page = __tokenized_page_request(url, page_size=page_size, query=query)
    data = api_page[property]
    while len(api_page.get("next_page_token", "")) != 0:
        api_page = __tokenized_page_request(
            url, next_page_token=api_page["next_page_token"], page_size=page_size
        )
        data += api_page.get(property, [])

    return data


def get_phone_users():
    return __tokenized_all_pages(URL_PHONE_USERS, "users")


def get_phone_numbers():
    return __tokenized_all_pages(URL_PHONE_NUMBERS, "phone_numbers")


def get_past_meetings_instances(meeting_id):
    url = f"{API_ROOT}/past_meetings/{meeting_id}/instances"

    headers = dict(Authorization=f"Bearer {get_access_token()}")
    response = requests.request("GET", url, headers=headers)
    return response.json()


def get_past_meetings_participants(meeting_uuid):
    url = f"{API_ROOT}/past_meetings/{meeting_uuid}/participants"
    return __tokenized_all_pages(url, "participants")


def update_all_users():
    api_page = __get_users()
    all_users = api_page["users"]
    while api_page["page_number"] < api_page["page_count"]:
        api_page = __get_users(page_number=api_page["page_number"] + 1)
        all_users += api_page["users"]

    for data in all_users:
        email = data.get("email", "").lower()

        try:
            sf_profile = Profile.objects.get_by_emails(email)
            user = sf_profile.user
        except Profile.DoesNotExist:
            logger.info(f"No django user for email: {email}")
            continue

        try:
            profile = ZoomProfile.objects.get(user=user)
        except ZoomProfile.DoesNotExist:
            profile = ZoomProfile(user=user)

        profile.zoom_id = data.get("id")
        profile.dept = __prune_empty_string(data.get("dept"))
        profile.phone_number = __prune_empty_string(data.get("phone_number"))
        profile.pic_url = __prune_empty_string(data.get("pic_url"))
        profile.save()


def update_all_phone_users():
    all_users = get_phone_users()

    for data in all_users:
        id = data.get("id")
        try:
            profile = ZoomProfile.objects.get(zoom_id=id)
        except ZoomProfile.DoesNotExist:
            logger.debug(f"No ZoomProfile found for {data.get('email')}")
            continue

        profile.extension_number = data.get("extension_number")
        profile.save()

        db_calling_plans = {cp.type for cp in profile.calling_plans.all()}
        api_calling_plans = {cp["type"] for cp in data.get("calling_plans", [])}

        to_delete = db_calling_plans - api_calling_plans
        for type in to_delete:
            for plan in profile.calling_plans.all():
                if plan.type == type:
                    logger.debug(f"Deleting {plan}")
                    plan.delete()

        to_add = api_calling_plans - db_calling_plans
        for type in to_add:
            for plan in data["calling_plans"]:
                if plan["type"] == type:
                    new_plan = CallingPlan(
                        zoom_profile=profile, type=type, name=plan["name"]
                    )
                    new_plan.save()
                    logger.debug(f"Saved {new_plan}")


def update_all_phone_numbers():
    all_numbers = get_phone_numbers()

    assigned_numbers = [
        number
        for number in all_numbers
        if number.get("assignee", {}).get("type") == "user"
    ]
    assigned_numbers_lookup = {number["number"]: number for number in assigned_numbers}

    all_db_numbers = AssignedNumber.objects.all()
    db_number_lookup = {record.number: record for record in all_db_numbers}

    all_zoom_profiles = ZoomProfile.objects.all()
    zoom_profiles_lookup = {p.extension_number: p for p in all_zoom_profiles}

    # Delete ones that are not assigned to users
    for db_record in all_db_numbers:
        if db_record.number not in assigned_numbers_lookup:
            logger.debug(f"Deleting {db_record}")
            db_record.delete()

    for number in assigned_numbers:
        extension = number["assignee"]["extension_number"]
        zoom_profile = zoom_profiles_lookup.get(extension)
        if zoom_profile is None:
            logger.debug(f"No ZoomProfile found for extension {extension}", number)
            continue

        record = db_number_lookup.get(number["number"])
        if record is None:
            record = AssignedNumber(zoom_profile=zoom_profile)
        record.number = number["number"]
        record.location = number["location"]
        logger.debug(f"Saving {record}")
        record.save()


