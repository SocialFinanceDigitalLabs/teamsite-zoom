from datetime import date
from functools import reduce
from typing import Union

from django.http import JsonResponse
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from holiday.util.holiday_report import generate_holiday_report
from resourcing.serializers.user import UserSerializer
from resourcing.views import permissions as sf_permission
from sf_zoom.models import ZoomParticipant, ZoomProfile


class ZoomProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ZoomProfile
        fields = [
            "zoom_id",
            "dept",
            "pic_url",
            "phone_number",
            "extension_number",
            "presence_status",
            "user",
        ]


class ZoomParticipantSerializer(serializers.HyperlinkedModelSerializer):
    profile = ZoomProfileSerializer()

    class Meta:
        model = ZoomParticipant
        fields = [
            "meeting_id",
            "user_id",
            "participant_id",
            "user_name",
            "join_time",
            "profile",
        ]


def get_name(participant: ZoomParticipant) -> str:
    if participant.profile is not None:
        return participant.profile.user.profile.short_name

    try:
        if participant.participant_id is None or len(participant.participant_id) == 0:
            return f"Caller {participant.user_name[0:5]}*******"
    except:
        pass

    return participant.user_name


def get_dept(participant: ZoomParticipant) -> str:
    if participant.profile is not None and participant.profile.dept is not None:
        return participant.profile.dept

    if participant.participant_id is None or len(participant.participant_id) == 0:
        return "Phone"

    return "Visitor"


def get_pic(participant: ZoomParticipant) -> Union[str, None]:
    if participant.profile is not None:
        return participant.profile.user.profile.avatar


class WebinarViewSet(viewsets.ModelViewSet):
    permission_classes = [sf_permission.IsAuthenticatedReadOnly]
    serializer_class = ZoomParticipantSerializer
    queryset = ZoomParticipant.objects.all()

    @action(detail=False)
    def graph(self, request):
        participants = ZoomParticipant.objects.all()

        p_list = [
            {
                "id": p.user_id,
                "name": get_name(p),
                "dept": get_dept(p),
                "pic": get_pic(p),
            }
            for p in participants
        ]

        by_dept = dict()
        for p in p_list:
            by_dept.setdefault(p["dept"], []).append(p)

        nodes = [dict(id="root", name="MMM", val=len(p_list))]
        links = []

        for d, p in by_dept.items():
            nodes.append(dict(id=d, name=d, dept=d, val=len(p)))
            links.append(dict(source="root", target=d))

        for p in p_list:
            nodes.append(
                dict(
                    id=p["id"], name=p["name"], val=1, pic=p.get("pic"), dept=p["dept"]
                )
            )
            links.append(dict(source=p["dept"], target=p["id"]))

        return JsonResponse({"nodes": nodes, "links": links})
