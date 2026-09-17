from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
    Assignment,
    CalendarRequest,
    CalendarSettings,
    Event,
    SchoolDay,
    UserProfile,
)


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "username",
            "email",
            "authority",
            "student_id",
            "teacher_id",
            "class_name",
        ]


class EventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "description",
            "location",
            "start",
            "end",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "created_by",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        # On a PATCH, "start"/"end" may not both be present in `data`,
        # so fall back to the existing instance's values. Using
        # data["start"] directly raised a KeyError on partial updates.
        start = data.get(
            "start",
            getattr(self.instance, "start", None),
        )
        end = data.get(
            "end",
            getattr(self.instance, "end", None),
        )

        if start and end and end <= start:
            raise serializers.ValidationError(
                "Event end time must be after its start time."
            )

        return data


class AssignmentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(
        source="teacher.get_full_name",
        read_only=True,
    )

    class Meta:
        model = Assignment
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "posted_at",
            "due_at",
            "class_id",
            "class_name",
            "name",
            "description",
            "google_classroom_link",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "teacher",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        posted_at = data.get(
            "posted_at",
            getattr(self.instance, "posted_at", None),
        )
        due_at = data.get(
            "due_at",
            getattr(self.instance, "due_at", None),
        )

        if posted_at and due_at and due_at <= posted_at:
            raise serializers.ValidationError(
                "Due time must be after posted time."
            )

        return data


class CalendarRequestSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(
        source="submitted_by.get_full_name",
        read_only=True,
    )

    reviewed_by_name = serializers.CharField(
        source="reviewed_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = CalendarRequest
        fields = [
            "id",
            "submitted_by",
            "submitted_by_name",
            "request_type",
            "title",
            "description",
            "requested_data",
            "status",
            "reviewed_by",
            "reviewed_by_name",
            "review_notes",
            "created_event",
            "created_assignment",
            "created_at",
            "reviewed_at",
        ]

        read_only_fields = [
            "submitted_by",
            "status",
            "reviewed_by",
            "created_event",
            "created_assignment",
            "reviewed_at",
        ]


class CalendarSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarSettings
        fields = [
            "id",
            "first_week_monday",
        ]


class SchoolDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolDay
        fields = [
            "id",
            "date",
            "day_type",
            "rotation",
            "is_school_day",
            "start_time",
            "end_time",
            "title",
            "description",
            "is_override",
            "created_by",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "created_by",
            "created_at",
            "updated_at",
        ]
