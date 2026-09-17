from datetime import date as date_cls

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .day_utils import get_day_type
from .models import (
    Assignment,
    Authority,
    CalendarRequest,
    CalendarSettings,
    Event,
    SchoolDay,
    UserProfile,
)
from .permissions import (
    CanModifyAssignments,
    CanModifyEvents,
    IsAdmin,
    get_authority,
)
from .serializers import (
    AssignmentSerializer,
    CalendarRequestSerializer,
    CalendarSettingsSerializer,
    EventSerializer,
    SchoolDaySerializer,
    UserProfileSerializer,
)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]

        return [CanModifyEvents()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]

        return [CanModifyAssignments()]

    def perform_create(self, serializer):
        serializer.save(
            teacher=self.request.user,
            posted_at=timezone.now(),
        )


class CalendarRequestViewSet(viewsets.ModelViewSet):
    queryset = CalendarRequest.objects.all()
    serializer_class = CalendarRequestSerializer

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return CalendarRequest.objects.none()

        authority = get_authority(user)

        if authority == Authority.ADMIN:
            return CalendarRequest.objects.all()

        return CalendarRequest.objects.filter(
            submitted_by=user
        )

    def get_permissions(self):
        if self.action in ["create", "list", "retrieve"]:
            return [permissions.IsAuthenticated()]

        return [IsAdmin()]

    def perform_create(self, serializer):
        serializer.save(
            submitted_by=self.request.user,
        )

    def _build_event(self, calendar_request, reviewer):
        """
        Turn an approved EVENT request into a real Event.
        Returns the created Event, or None if requested_data
        did not validate.
        """

        serializer = EventSerializer(data=calendar_request.requested_data)

        if not serializer.is_valid():
            return None

        return serializer.save(created_by=reviewer)

    def _build_assignment(self, calendar_request, reviewer):
        """
        Turn an approved ASSIGNMENT request into a real Assignment.
        Returns the created Assignment, or None if requested_data
        did not validate.
        """

        serializer = AssignmentSerializer(
            data=calendar_request.requested_data
        )

        if not serializer.is_valid():
            return None

        return serializer.save(
            teacher=reviewer,
            posted_at=timezone.now(),
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAdmin],
    )
    def approve(self, request, pk=None):
        calendar_request = self.get_object()

        if calendar_request.status != CalendarRequest.Status.PENDING:
            return Response(
                {"detail": "This request has already been reviewed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # NOTE: approving a request previously only flipped its status
        # without ever creating the Event/Assignment it was requesting.
        # We build the real object here, from requested_data, using the
        # reviewing admin as its owner/teacher of record.
        if calendar_request.request_type == CalendarRequest.RequestType.EVENT:
            created = self._build_event(calendar_request, request.user)
            if created is None:
                return Response(
                    {"detail": "requested_data is not a valid event."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            calendar_request.created_event = created

        elif calendar_request.request_type == CalendarRequest.RequestType.ASSIGNMENT:
            created = self._build_assignment(calendar_request, request.user)
            if created is None:
                return Response(
                    {"detail": "requested_data is not a valid assignment."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            calendar_request.created_assignment = created

        else:
            return Response(
                {"detail": "Unknown request_type."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        calendar_request.status = CalendarRequest.Status.APPROVED
        calendar_request.reviewed_by = request.user
        calendar_request.reviewed_at = timezone.now()
        calendar_request.review_notes = request.data.get(
            "review_notes",
            "",
        )
        calendar_request.save()

        return Response(
            CalendarRequestSerializer(calendar_request).data
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAdmin],
    )
    def reject(self, request, pk=None):
        calendar_request = self.get_object()

        if calendar_request.status != CalendarRequest.Status.PENDING:
            return Response(
                {"detail": "This request has already been reviewed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        calendar_request.status = CalendarRequest.Status.REJECTED
        calendar_request.reviewed_by = request.user
        calendar_request.reviewed_at = timezone.now()
        calendar_request.review_notes = request.data.get(
            "review_notes",
            "",
        )
        calendar_request.save()

        return Response(
            CalendarRequestSerializer(calendar_request).data
        )


class DayViewSet(viewsets.ViewSet):
    """
    GET /api/days/2026-09-04/

    Resolution order:
      1. An explicit SchoolDay row for that date (holiday, half day,
         manually corrected rotation, etc.) always wins.
      2. Otherwise, weekends report as WEEKEND / no rotation.
      3. Otherwise, the A/B rotation is computed from CalendarSettings.

    Previously this endpoint only ever did step 3, so any holiday or
    schedule override stored in SchoolDay was silently ignored.
    """

    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, pk=None):
        try:
            day = date_cls.fromisoformat(pk)
        except ValueError:
            return Response(
                {"detail": "Invalid date."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        override = SchoolDay.objects.filter(date=day).first()

        if override:
            return Response(SchoolDaySerializer(override).data)

        if day.weekday() >= 5:
            return Response({
                "date": day,
                "day_type": SchoolDay.DayType.WEEKEND,
                "rotation": SchoolDay.Rotation.NONE,
                "is_school_day": False,
                "is_override": False,
            })

        rotation = get_day_type(day)

        return Response({
            "date": day,
            "day_type": SchoolDay.DayType.SCHOOL,
            "rotation": rotation,
            "is_school_day": True,
            "is_override": False,
        })


class SchoolDayViewSet(viewsets.ModelViewSet):
    """
    Lets admins create/edit explicit overrides (holidays, half days,
    schedule corrections). Reading is open to everyone; writing is
    admin-only, mirroring CalendarSettings.
    """

    queryset = SchoolDay.objects.all()
    serializer_class = SchoolDaySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]

        return [IsAdmin()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CalendarSettingsViewSet(viewsets.ModelViewSet):
    queryset = CalendarSettings.objects.all()
    serializer_class = CalendarSettingsSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]

        return [IsAdmin()]

    def create(self, request, *args, **kwargs):
        if CalendarSettings.objects.exists():
            return Response(
                {
                    "detail": (
                        "Calendar settings already exist. "
                        "Update the existing settings instead."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserProfileSerializer
    # Explicit on purpose: the project's global DRF default is
    # AllowAny (see settings.py), so without this every profile
    # endpoint would technically be open. get_queryset() already
    # returns nothing for anonymous users, but this makes the
    # intended access rule explicit rather than incidental.
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return UserProfile.objects.none()

        if get_authority(user) != Authority.ADMIN:
            return UserProfile.objects.filter(user=user)

        return UserProfile.objects.all()
