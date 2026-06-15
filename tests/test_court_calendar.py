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
