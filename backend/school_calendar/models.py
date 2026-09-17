from django.contrib.auth.models import User
from django.db import models


class Authority(models.IntegerChoices):
    GUEST = 0, "Guest"
    STUDENT = 1, "Student"
    STUCO = 2, "StuCo"
    TEACHER = 3, "Teacher"
    ADMIN = 4, "Admin"


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    authority = models.PositiveSmallIntegerField(
        choices=Authority.choices,
        default=Authority.STUDENT,
    )

    # Optional school-specific information
    student_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    teacher_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    class_name = models.CharField(
        max_length=100,
        blank=True,
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_authority_display()}"

    @property
    def is_student(self):
        return self.authority == Authority.STUDENT

    @property
    def is_stuco(self):
        return self.authority == Authority.STUCO

    @property
    def is_teacher(self):
        return self.authority == Authority.TEACHER

    @property
    def is_admin(self):
        return self.authority == Authority.ADMIN


class CalendarSettings(models.Model):
    """
    There should normally only be one instance of this model.

    first_week_monday:
        The Monday that represents Week 1.

    Week 1:
        Monday A
        Tuesday B
        Wednesday A
        Thursday B
        Friday A

    Week 2:
        Monday B
        Tuesday A
        Wednesday B
        Thursday A
        Friday B
    """

    first_week_monday = models.DateField()

    class Meta:
        verbose_name = "Calendar Settings"
        verbose_name_plural = "Calendar Settings"

    def __str__(self):
        return f"Calendar settings - Week 1: {self.first_week_monday}"


class Event(models.Model):
    name = models.CharField(max_length=255)

    description = models.TextField(
        blank=True,
    )

    location = models.CharField(
        max_length=255,
        blank=True,
    )

    start = models.DateTimeField()
    end = models.DateTimeField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_events",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["start"]

    def __str__(self):
        return self.name


class Assignment(models.Model):
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assignments",
    )

    posted_at = models.DateTimeField()

    due_at = models.DateTimeField()

    class_id = models.CharField(
        max_length=100,
    )

    class_name = models.CharField(
        max_length=255,
    )

    name = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
    )

    google_classroom_link = models.URLField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["due_at"]

    def __str__(self):
        return f"{self.class_name}: {self.name}"


class CalendarRequest(models.Model):
    """
    Used by students to request that something be added/changed.

    Students cannot directly create calendar events or assignments.
    They submit a request which a StuCo/admin/teacher can review.
    """

    class RequestType(models.TextChoices):
        EVENT = "event", "Event"
        ASSIGNMENT = "assignment", "Assignment"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    submitted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="calendar_requests",
    )

    request_type = models.CharField(
        max_length=20,
        choices=RequestType.choices,
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
    )

    requested_data = models.JSONField(
        default=dict,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_calendar_requests",
    )

    review_notes = models.TextField(
        blank=True,
    )

    # Set once the request is approved and turned into a real
    # Event/Assignment, so the created object can be traced back
    # to the request that produced it.
    created_event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_request",
    )

    created_assignment = models.ForeignKey(
        Assignment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_request",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.status})"


class SchoolDay(models.Model):
    class DayType(models.TextChoices):
        SCHOOL = "SCHOOL", "School Day"
        WEEKEND = "WEEKEND", "Weekend"
        HOLIDAY = "HOLIDAY", "Holiday"
        HALF_DAY = "HALF_DAY", "Half Day"
        ADMIN_ONLY = "ADMIN_ONLY", "Admin Only"
        NO_SCHOOL = "NO_SCHOOL", "No School"
        OTHER = "OTHER", "Other"

    class Rotation(models.TextChoices):
        A = "A", "A Day"
        B = "B", "B Day"
        NONE = "NONE", "No Rotation"

    date = models.DateField(
        unique=True,
    )

    day_type = models.CharField(
        max_length=20,
        choices=DayType.choices,
    )

    rotation = models.CharField(
        max_length=4,
        choices=Rotation.choices,
        default=Rotation.NONE,
    )

    # Whether students are expected to attend.
    is_school_day = models.BooleanField(
        default=True,
    )

    start_time = models.TimeField(
        null=True,
        blank=True,
    )

    end_time = models.TimeField(
        null=True,
        blank=True,
    )

    title = models.CharField(
        max_length=255,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    # True when this day was explicitly configured
    # rather than coming from the normal schedule.
    is_override = models.BooleanField(
        default=True,
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_school_days",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.date} - {self.get_day_type_display()}"
