from datetime import date

from .models import CalendarSettings


def get_week_number(day: date, first_week_monday: date) -> int:
    """
    Returns the school week number.

    first_week_monday = Week 1
    The following Monday = Week 2, etc.
    """

    difference = (day - first_week_monday).days

    if difference < 0:
        raise ValueError(
            "Date is before the configured first_week_monday."
        )

    return difference // 7 + 1


def get_day_type(day: date) -> str:
    """
    Returns:
        "A"
        "B"
        None for Saturday/Sunday

    Rules:

    Week 1:
        Mon A
        Tue B
        Wed A
        Thu B
        Fri A

    Week 2:
        Mon B
        Tue A
        Wed B
        Thu A
        Fri B
    """

    if day.weekday() >= 5:
        return None

    settings = CalendarSettings.objects.first()

    if not settings:
        raise ValueError(
            "CalendarSettings has not been configured."
        )

    week_number = get_week_number(
        day,
        settings.first_week_monday,
    )

    # Week 1 => False
    # Week 2 => True
    week_is_b = (week_number - 1) % 2 == 1

    # Friday is explicitly based on the week.
    if day.weekday() == 4:
        return "B" if week_is_b else "A"

    # Monday-Thursday alternate.
    # Week 1 starts A.
    school_day_index = day.weekday()

    is_b = (school_day_index + (1 if week_is_b else 0)) % 2 == 1

    return "B" if is_b else "A"
