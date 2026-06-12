import sys
from pathlib import Path

import docassemble


for search_path in sys.path:
    installed_namespace = Path(search_path) / "docassemble"
    if installed_namespace.is_dir() and str(installed_namespace) not in docassemble.__path__:
        docassemble.__path__.append(str(installed_namespace))

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
