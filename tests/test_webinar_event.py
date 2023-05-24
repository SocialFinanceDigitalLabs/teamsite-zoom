import io

import django.test
import yaml
from django.contrib.auth import get_user_model

from teamsite_zoom.models import ZoomProfile

User = get_user_model()

TEMPLATE = """
payload:
    object:
        participant:
            user_id: X1111111
            user_name: "User Name"
            id: X2222222
            join_time: 2020-10-26T08:45:55Z
        id: meeeting-id-1111
        type: 9
        topic: My Meeting Topic
        host_id: host-id-1111
        duration: 45
        start_time: 2020-10-26T08:30:55Z
        timezone: Europe/London
"""


def get_message(user_id, user_name=None, email=None, event="joined"):
    data = yaml.safe_load(io.StringIO(TEMPLATE))
    data["event"] = event
    data["payload"]["object"]["participant"]["user_id"] = user_id

    if user_name is not None:
        data["payload"]["object"]["participant"]["user_name"] = user_name

    if email is not None:
        data["payload"]["object"]["participant"]["email"] = email

    return data


class WebinarMeetingParticipantTestCase(django.test.TestCase):
    def setUp(self):
        user1 = User.objects.create(
            username="user1",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
        )
        ZoomProfile.objects.create(user=user1)

    def test_profile(self):
        ZoomProfile.objects.get(user__email="john.doe@example.com")
