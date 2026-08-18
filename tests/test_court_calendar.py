import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from types import ModuleType
from typing import Union

import docassemble


for search_path in sys.path:
    installed_namespace = Path(search_path) / "docassemble"
    if installed_namespace.is_dir() and str(installed_namespace) not in docassemble.__path__:
        docassemble.__path__.append(str(installed_namespace))


class DADateTime:
    """Minimal Docassemble date implementation for the lightweight CI test runner."""

    def __init__(self, value: date):
        self.value = value

    @property
    def year(self) -> int:
        return self.value.year

    @property
    def dow(self) -> int:
        return self.value.isoweekday()

    def minus(self, *, days: int) -> "DADateTime":
        return DADateTime(self.value - timedelta(days=days))

    def plus(self, *, days: int) -> "DADateTime":
        return DADateTime(self.value + timedelta(days=days))

    def format(self, date_format: str) -> str:
        if date_format != "yyyy-MM-dd":
            raise ValueError(f"Unsupported test date format: {date_format}")
        return self.value.isoformat()


def as_datetime(value: Union[str, date, DADateTime]) -> DADateTime:
    if isinstance(value, DADateTime):
        return value
    if isinstance(value, datetime):
        return DADateTime(value.date())
    if isinstance(value, date):
        return DADateTime(value)
    return DADateTime(date.fromisoformat(value))


# ALActions does not install the full Docassemble server runtime. ALToolbox's
# business-day module only needs these two date utilities for these tests.
base_module = ModuleType("docassemble.base")
util_module = ModuleType("docassemble.base.util")
setattr(util_module, "DADateTime", DADateTime)
setattr(util_module, "as_datetime", as_datetime)
setattr(base_module, "util", util_module)
setattr(docassemble, "base", base_module)
sys.modules["docassemble.base"] = base_module
sys.modules["docassemble.base.util"] = util_module

from docassemble.MAEvictionDefense.court_calendar import (
    court_business_days_before,
    court_holiday_name,
    late_answer_motion_needed,
    next_court_business_day,
)


def test_court_business_days_before_skips_weekends():
    result = court_business_days_before("2026-03-02", 3)

    assert result.format("yyyy-MM-dd") == "2026-02-25"


def test_court_business_days_before_skips_holidays():
    result = court_business_days_before("2026-01-20", 3)

    assert result.format("yyyy-MM-dd") == "2026-01-14"


def test_patriots_day_is_a_court_business_day():
    result = court_business_days_before("2026-04-21", 1)

    assert result.format("yyyy-MM-dd") == "2026-04-20"
    assert court_holiday_name("2026-04-20") == ""


def test_court_holiday_name_returns_observed_holiday():
    assert court_holiday_name("2026-01-19") == "Martin Luther King Jr. Day"


def test_late_answer_motion_needed_before_deadline():
    assert late_answer_motion_needed("2026-03-01", "2026-03-02", "2026-03-10") is False


def test_late_answer_motion_needed_after_deadline_before_hearing():
    assert late_answer_motion_needed("2026-03-03", "2026-03-02", "2026-03-10") is True


def test_late_answer_motion_needed_after_hearing():
    assert late_answer_motion_needed("2026-03-11", "2026-03-02", "2026-03-10") is False


def test_next_court_business_day_moves_sunday_to_monday():
    result = next_court_business_day("2026-08-16")

    assert result.format("yyyy-MM-dd") == "2026-08-17"


def test_next_court_business_day_keeps_a_business_day():
    result = next_court_business_day("2026-08-17")

    assert result.format("yyyy-MM-dd") == "2026-08-17"


def test_next_court_business_day_skips_a_holiday_and_the_weekend():
    # 2026-11-26 is Thanksgiving, so the next court business day is the Friday.
    assert next_court_business_day("2026-11-26").format("yyyy-MM-dd") == "2026-11-27"
    # 2026-12-25 is Christmas on a Friday, so the deadline moves to the Monday.
    assert next_court_business_day("2026-12-25").format("yyyy-MM-dd") == "2026-12-28"


def test_next_court_business_day_treats_patriots_day_as_a_business_day():
    assert next_court_business_day("2026-04-20").format("yyyy-MM-dd") == "2026-04-20"


def test_answer_deadline_without_hearing_date_is_never_a_weekend_or_holiday():
    """Regression test for #355: the deadline must land on a court business day."""
    day = date(2026, 1, 1)
    while day < date(2027, 1, 1):
        deadline = next_court_business_day(DADateTime(day).plus(days=1))
        assert deadline.dow not in (6, 7), f"{day}: deadline {deadline.format('yyyy-MM-dd')} is a weekend"
        assert court_holiday_name(deadline) == "", (
            f"{day}: deadline {deadline.format('yyyy-MM-dd')} is a court holiday"
        )
        day += timedelta(days=1)
