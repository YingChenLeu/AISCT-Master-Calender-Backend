from django.contrib import admin

from .models import (
    Assignment,
    CalendarRequest,
    CalendarSettings,
    Event,
    SchoolDay,
    UserProfile,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "authority",
        "student_id",
        "teacher_id",
        "class_name",
    )

    list_filter = (
        "authority",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "student_id",
        "teacher_id",
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "start",
        "end",
        "location",
        "created_by",
    )

    list_filter = (
        "start",
    )

    search_fields = (
        "name",
        "description",
        "location",
    )


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "class_name",
        "teacher",
        "posted_at",
        "due_at",
    )

    list_filter = (
        "class_name",
        "teacher",
    )

    search_fields = (
        "name",
        "class_name",
        "class_id",
        "description",
    )


@admin.register(CalendarRequest)
class CalendarRequestAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "request_type",
        "submitted_by",
        "status",
        "created_at",
        "reviewed_by",
    )

    list_filter = (
        "status",
        "request_type",
    )

    search_fields = (
        "title",
        "description",
        "submitted_by__username",
    )


@admin.register(CalendarSettings)
class CalendarSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "first_week_monday",
    )


@admin.register(SchoolDay)
class SchoolDayAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "day_type",
        "rotation",
        "is_school_day",
        "is_override",
    )

    list_filter = (
        "day_type",
        "rotation",
        "is_school_day",
    )

    search_fields = (
        "title",
        "description",
    )
