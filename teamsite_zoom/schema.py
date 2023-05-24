import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from .models import AssignedNumber, CallingPlan, ZoomProfile


class ZoomProfileNode(DjangoObjectType):
    class Meta:
        model = ZoomProfile
        filter_fields = []
        interfaces = (graphene.relay.Node,)
        fields = "__all__"


class AssignedNumberNode(DjangoObjectType):
    class Meta:
        model = AssignedNumber
        filter_fields = []
        interfaces = (graphene.relay.Node,)
        fields = "__all__"


class CallingPlanNode(DjangoObjectType):
    class Meta:
        model = CallingPlan
        filter_fields = []
        interfaces = (graphene.relay.Node,)
        fields = "__all__"


class Query(object):
    zoom_profile = graphene.relay.Node.Field(ZoomProfileNode)
    all_zoom_profiles = DjangoFilterConnectionField(ZoomProfileNode)
