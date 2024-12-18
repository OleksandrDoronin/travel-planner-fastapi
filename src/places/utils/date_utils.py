from datetime import date


def check_future_date(visit_date: date | None) -> date | None:
    """Ensure the visit date is not in the future."""

    if visit_date and visit_date > date.today():
        raise ValueError('Date of visit cannot be in the future')
    return visit_date
