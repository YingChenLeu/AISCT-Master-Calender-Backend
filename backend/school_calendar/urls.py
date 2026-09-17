from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AssignmentViewSet,
    CalendarRequestViewSet,
    CalendarSettingsViewSet,
    DayViewSet,
    EventViewSet,
    SchoolDayViewSet,
    UserProfileViewSet,
)

router = DefaultRouter()

router.register(
    "events",
    EventViewSet,
    basename="events",
)

router.register(
    "assignments",
    AssignmentViewSet,
    basename="assignments",
)

router.register(
    "requests",
    CalendarRequestViewSet,
    basename="requests",
)

router.register(
    "days",
    DayViewSet,
    basename="days",
)

router.register(
    "school-days",
    SchoolDayViewSet,
    basename="school-days",
)

router.register(
    "settings",
    CalendarSettingsViewSet,
    basename="settings",
)

router.register(
    "users",
    UserProfileViewSet,
    basename="users",
)

urlpatterns = [
    path("", include(router.urls)),
]
