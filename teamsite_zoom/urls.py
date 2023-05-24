from django.urls import include, path, re_path
from rest_framework import routers

from sf_zoom.views.webinar import WebinarViewSet

router = routers.DefaultRouter()
router.register(r"webinar", WebinarViewSet, basename="zoom")

urlpatterns = [
    path("", include(router.urls)),
]
