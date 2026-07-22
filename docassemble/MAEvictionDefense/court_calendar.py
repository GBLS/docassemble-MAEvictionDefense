from typing import Union

from docassemble.ALToolbox.business_days import is_business_day, standard_holidays
from docassemble.base.util import DADateTime, as_datetime


COURT_HOLIDAY_EXCLUSIONS = ["Patriots' Day"]


def court_business_days_before(
    start_date: Union[str, DADateTime], number_of_days: int
) -> DADateTime:
    """Return the date a given number of Massachusetts court business days earlier."""
    date_to_check = as_datetime(start_date)
    business_days_counted = 0

    while business_days_counted < number_of_days:
        date_to_check = date_to_check.minus(days=1)
        if is_business_day(
            date=date_to_check,
            subdiv="MA",
            remove_holidays=COURT_HOLIDAY_EXCLUSIONS,
        ):
            business_days_counted += 1

    return date_to_check


def late_answer_motion_needed(
    current_date: Union[str, DADateTime],
    answer_deadline: Union[str, DADateTime],
    hearing_date: Union[str, DADateTime, None] = None,
) -> bool:
    """Return whether the late answer motion should be offered."""
    today_date = as_datetime(current_date)
    deadline_date = as_datetime(answer_deadline)

    if hearing_date in (None, ""):
        return today_date > deadline_date

    hearing_date_value = as_datetime(hearing_date)
    return today_date > deadline_date and today_date <= hearing_date_value


def court_holiday_name(date_to_check: Union[str, DADateTime]) -> str:
    """Return the observed Massachusetts court holiday name, if any."""
    normalized_date = as_datetime(date_to_check)
    return standard_holidays(
        year=normalized_date.year,
        subdiv="MA",
        remove_holidays=COURT_HOLIDAY_EXCLUSIONS,
    ).get(normalized_date.format("yyyy-MM-dd"), "")
