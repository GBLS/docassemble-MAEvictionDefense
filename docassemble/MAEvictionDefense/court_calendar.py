from typing import Union

from docassemble.ALToolbox.business_days import is_business_day, standard_holidays
from docassemble.base.util import DADateTime, as_datetime


def is_court_business_day(date_to_check: Union[str, DADateTime]) -> bool:
    """Return whether Massachusetts courts are ordinarily open on the date."""
    return is_business_day(date=as_datetime(date_to_check), subdiv="MA")


def court_business_days_before(
    start_date: Union[str, DADateTime], number_of_days: int
) -> DADateTime:
    """Return the date a given number of Massachusetts court business days earlier."""
    date_to_check = as_datetime(start_date)
    business_days_counted = 0

    while business_days_counted < number_of_days:
        date_to_check = date_to_check.minus(days=1)
        if is_court_business_day(date_to_check):
            business_days_counted += 1

    return date_to_check


def next_court_business_day(date_to_check: Union[str, DADateTime]) -> DADateTime:
    """Return the first Massachusetts court business day on or after the given date."""
    candidate = as_datetime(date_to_check)

    while not is_court_business_day(candidate):
        candidate = candidate.plus(days=1)

    return candidate


def late_answer_motion_needed(
    current_date: Union[str, DADateTime],
    answer_deadline: Union[str, DADateTime],
    hearing_date: Union[str, DADateTime, None] = None,
) -> bool:
    """Return whether the late answer motion should be offered."""
    today_date = as_datetime(current_date).format("yyyy-MM-dd")
    deadline_date = as_datetime(answer_deadline).format("yyyy-MM-dd")

    if hearing_date in (None, ""):
        return today_date > deadline_date

    hearing_date_value = as_datetime(hearing_date).format("yyyy-MM-dd")
    return today_date > deadline_date and today_date <= hearing_date_value


def court_holiday_name(date_to_check: Union[str, DADateTime]) -> str:
    """Return the observed Massachusetts court holiday name, if any."""
    normalized_date = as_datetime(date_to_check)
    return standard_holidays(
        year=normalized_date.year,
        subdiv="MA",
    ).get(normalized_date.format("yyyy-MM-dd"), "")
