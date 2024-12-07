from datetime import date
from typing import Optional


def format_title_case(value: str) -> str:
    """Convert a string to title case."""

    return value.strip().title()


def check_future_date(visit_date: Optional[date]) -> Optional[date]:
    """Ensure the visit date is not in the future."""

    if visit_date and visit_date > date.today():
        raise ValueError('Date of visit cannot be in the future')
    return visit_date
