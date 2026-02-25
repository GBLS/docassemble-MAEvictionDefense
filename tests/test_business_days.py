"""
Unit tests for business day calculations used in MADE eviction defense.

These tests verify that court deadline calculations correctly:
1. Count backwards 3 business days from mediation dates
2. Skip weekends
3. Skip federal holidays and MA holidays (except Patriots' Day)
4. Do NOT skip Patriots' Day (courts are open)

Run with: pytest tests/test_business_days.py -v

TESTING APPROACH
================
These tests verify the business day calculation ALGORITHM that is used by
ALToolbox.business_days (which is called in eviction.code.yml). The functions
in this file replicate the same logic as:
  - ALToolbox.business_days.get_date_n_business_days
  - ALToolbox.business_days.is_business_day

We cannot directly import and test ALToolbox.business_days in pytest because
it depends on `docassemble.base.util` which requires the full docassemble
server runtime. Instead, we:
  1. Implement the same algorithm here using the `holidays` library
  2. Test that algorithm with the same parameters used in production:
     - subdiv='MA' (Massachusetts state holidays)
     - remove_holidays=["Patriots' Day"] (courts are open on Patriots' Day)

For full integration testing of eviction.code.yml with the actual ALToolbox
functions, use ALKiln tests (see data/sources/court_dates.feature).

PRODUCTION CODE LOCATION
========================
The production code using ALToolbox.business_days is in:
  docassemble/MAEvictionDefense/data/questions/eviction.code.yml
  
  Key usages:
  - case.answer_date: Calculated as 3 business days before mediation
  - case.on_time: Checks if today is 3+ business days before mediation
  - Holiday detection: Uses is_business_day for notification logic

ALKILN INTEGRATION TESTS
========================
For integration tests that run within the docassemble server and test the
actual ALToolbox.business_days functions, see:
  docassemble/MAEvictionDefense/data/sources/business_days.feature
"""

import pytest
from datetime import date, timedelta
import holidays


# Configuration matching eviction.code.yml
SUBDIV = 'MA'
REMOVE_HOLIDAYS = ["Patriots' Day"]


def get_holidays_for_year(year: int, subdiv: str = 'MA', remove_holidays: list = None) -> set:
    """Get the set of holiday dates for a given year, excluding removed holidays."""
    holiday_list = holidays.US(state=subdiv, years=year)
    if remove_holidays:
        # Filter out removed holidays
        return {d for d, name in holiday_list.items() if name not in remove_holidays}
    return set(holiday_list.keys())


def is_business_day(check_date: date, subdiv: str = 'MA', remove_holidays: list = None) -> bool:
    """Check if a date is a business day (not weekend, not holiday)."""
    # Weekend check
    if check_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    # Holiday check
    holiday_dates = get_holidays_for_year(check_date.year, subdiv, remove_holidays)
    return check_date not in holiday_dates


def get_date_n_business_days(start_date: date, wait_n_days: int, subdiv: str = 'MA', 
                              remove_holidays: list = None) -> date:
    """
    Calculate a date that is N business days from the start date.
    Negative values go backwards.
    
    This mirrors the logic in ALToolbox.business_days.get_date_n_business_days
    """
    if wait_n_days == 0:
        return start_date
    
    direction = 1 if wait_n_days > 0 else -1
    days_remaining = abs(wait_n_days)
    current = start_date
    
    while days_remaining > 0:
        current = current + timedelta(days=direction)
        if is_business_day(current, subdiv, remove_holidays):
            days_remaining -= 1
    
    return current


# Configuration matching eviction.code.yml
SUBDIV = 'MA'
REMOVE_HOLIDAYS = ["Patriots' Day"]


class TestBusinessDaysBeforeMediation:
    """Test calculating 3 business days before a mediation date."""
    
    def test_monday_mediation_gives_previous_wednesday(self):
        """Monday mediation -> deadline is previous Wednesday (skip Sat/Sun)"""
        # Monday, March 2, 2026
        mediation = date(2026, 3, 2)
        deadline = get_date_n_business_days(
            start_date=mediation,
            wait_n_days=-3,
            subdiv=SUBDIV,
            remove_holidays=REMOVE_HOLIDAYS
        )
        # 3 business days back: Fri Feb 27, Thu Feb 26, Wed Feb 25
        assert deadline == date(2026, 2, 25)
    
    def test_friday_mediation_gives_tuesday(self):
        """Friday mediation -> deadline is Tuesday (3 business days back)"""
        # Friday, March 6, 2026
        mediation = date(2026, 3, 6)
        deadline = get_date_n_business_days(
            start_date=mediation,
            wait_n_days=-3,
            subdiv=SUBDIV,
            remove_holidays=REMOVE_HOLIDAYS
        )
        # 3 business days back: Thu Mar 5, Wed Mar 4, Tue Mar 3
        assert deadline == date(2026, 3, 3)
    
    def test_wednesday_mediation_gives_friday(self):
        """Wednesday mediation -> deadline is Friday (no weekend in between)"""
        # Wednesday, March 4, 2026
        mediation = date(2026, 3, 4)
        deadline = get_date_n_business_days(
            start_date=mediation,
            wait_n_days=-3,
            subdiv=SUBDIV,
            remove_holidays=REMOVE_HOLIDAYS
        )
        # 3 business days back: Tue Mar 3, Mon Mar 2, Fri Feb 27
        assert deadline == date(2026, 2, 27)


class TestFederalHolidaysSkipped:
    """Test that federal holidays are properly skipped."""
    
    def test_skips_mlk_day(self):
        """MLK Day (3rd Monday of January) should be skipped"""
        # Tuesday Jan 20, 2026 (day after MLK Day which is Jan 19, 2026)
        mediation = date(2026, 1, 20)
        deadline = get_date_n_business_days(
            start_date=mediation,
            wait_n_days=-3,
            subdiv=SUBDIV,
            remove_holidays=REMOVE_HOLIDAYS
        )
        # MLK Day is Mon Jan 19, so going back 3 business days:
        # Fri Jan 16, Thu Jan 15, Wed Jan 14
        assert deadline == date(2026, 1, 14)
    
    def test_skips_presidents_day(self):
        """Presidents Day (3rd Monday of February) should be skipped"""
        # Tuesday Feb 17, 2026 (day after Presidents Day which is Feb 16, 2026)
        mediation = date(2026, 2, 17)
        deadline = get_date_n_business_days(
            start_date=mediation,
            wait_n_days=-3,
            subdiv=SUBDIV,
            remove_holidays=REMOVE_HOLIDAYS
        )
        # Presidents Day is Mon Feb 16, so going back 3 business days:
        # Fri Feb 13, Thu Feb 12, Wed Feb 11
        assert deadline == date(2026, 2, 11)
    
    def test_skips_memorial_day(self):
        """Memorial Day (last Monday of May) should be skipped"""
        # Tuesday May 26, 2026 (day after Memorial Day which is May 25, 2026)
        mediation = date(2026, 5, 26)
        deadline = get_date_n_business_days(
            start_date=mediation,
            wait_n_days=-3,
            subdiv=SUBDIV,
            remove_holidays=REMOVE_HOLIDAYS
        )
        # Memorial Day is Mon May 25, so going back 3 business days:
        # Fri May 22, Thu May 21, Wed May 20
        assert deadline == date(2026, 5, 20)
    
    def test_skips_independence_day_observed(self):
        """July 4th (or observed day) should be skipped"""
        # Monday July 6, 2026 (July 4 is Saturday, observed Friday July 3)
        mediation = date(2026, 7, 6)
        deadline = get_date_n_business_days(
            start_date=mediation,
            wait_n_days=-3,
            subdiv=SUBDIV,
            remove_holidays=REMOVE_HOLIDAYS
        )
        # July 3 is observed holiday, so going back 3 business days:
        # Thu July 2, Wed July 1, Tue June 30
        assert deadline == date(2026, 6, 30)
    
    def test_skips_labor_day(self):
        """Labor Day (1st Monday of September) should be skipped"""
        # Tuesday Sep 8, 2026 (day after Labor Day which is Sep 7, 2026)
        mediation = date(2026, 9, 8)
        deadline = get_date_n_business_days(
            start_date=mediation,
            wait_n_days=-3,
            subdiv=SUBDIV,
            remove_holidays=REMOVE_HOLIDAYS
        )
        # Labor Day is Mon Sep 7, so going back 3 business days:
        # Fri Sep 4, Thu Sep 3, Wed Sep 2
        assert deadline == date(2026, 9, 2)
    
    def test_skips_thanksgiving(self):
        """Thanksgiving (4th Thursday of November) should be skipped"""
        # Friday Nov 27, 2026 (day after Thanksgiving which is Nov 26, 2026)
        mediation = date(2026, 11, 27)
        deadline = get_date_n_business_days(
            start_date=mediation,
            wait_n_days=-3,
            subdiv=SUBDIV,
            remove_holidays=REMOVE_HOLIDAYS
        )
        # Thanksgiving is Thu Nov 26, so going back 3 business days:
        # Wed Nov 25, Tue Nov 24, Mon Nov 23
        assert deadline == date(2026, 11, 23)


class TestPatriotsDayNotSkipped:
    """Test that Patriots' Day is NOT skipped (courts are open)."""
    
    def test_patriots_day_is_counted_as_business_day(self):
        """Patriots' Day (3rd Monday of April in MA) should NOT be skipped"""
        # Patriots' Day 2026 is Monday April 20
        # Tuesday April 21, 2026 (day after Patriots' Day)
        mediation = date(2026, 4, 21)
        deadline = get_date_n_business_days(
            start_date=mediation,
            wait_n_days=-3,
            subdiv=SUBDIV,
            remove_holidays=REMOVE_HOLIDAYS
        )
        # Patriots' Day (Mon Apr 20) should be counted as a business day
        # So going back 3 business days: Mon Apr 20, Fri Apr 17, Thu Apr 16
        assert deadline == date(2026, 4, 16)
    
    def test_patriots_day_is_business_day(self):
        """is_business_day should return True for Patriots' Day"""
        # Patriots' Day 2026 is Monday April 20
        patriots_day = date(2026, 4, 20)
        assert is_business_day(
            check_date=patriots_day,
            subdiv=SUBDIV,
            remove_holidays=REMOVE_HOLIDAYS
        ) == True


class TestIsBusinessDay:
    """Test the is_business_day function for holiday detection."""
    
    def test_weekend_is_not_business_day(self):
        """Saturdays and Sundays are not business days"""
        saturday = date(2026, 3, 7)
        sunday = date(2026, 3, 8)
        
        assert is_business_day(saturday, subdiv=SUBDIV, remove_holidays=REMOVE_HOLIDAYS) == False
        assert is_business_day(sunday, subdiv=SUBDIV, remove_holidays=REMOVE_HOLIDAYS) == False
    
    def test_regular_weekday_is_business_day(self):
        """Regular weekdays are business days"""
        wednesday = date(2026, 3, 4)
        assert is_business_day(wednesday, subdiv=SUBDIV, remove_holidays=REMOVE_HOLIDAYS) == True
    
    def test_federal_holiday_is_not_business_day(self):
        """Federal holidays are not business days"""
        # MLK Day 2026 is Monday January 19
        mlk_day = date(2026, 1, 19)
        assert is_business_day(mlk_day, subdiv=SUBDIV, remove_holidays=REMOVE_HOLIDAYS) == False


class TestEdgeCases:
    """Test edge cases and complex scenarios."""
    
    def test_multiple_holidays_in_sequence(self):
        """Handle multiple holidays close together (Thanksgiving week)"""
        # Monday after Thanksgiving weekend 2026 (Nov 30)
        mediation = date(2026, 11, 30)
        deadline = get_date_n_business_days(
            start_date=mediation,
            wait_n_days=-3,
            subdiv=SUBDIV,
            remove_holidays=REMOVE_HOLIDAYS
        )
        # Thanksgiving is Thu Nov 26
        # Going back 3 business days from Mon Nov 30: Fri Nov 27, Wed Nov 25, Tue Nov 24
        assert deadline == date(2026, 11, 24)
    
    def test_new_years_day(self):
        """New Year's Day should be skipped"""
        # Friday Jan 2, 2026 (day after New Year's Day)
        mediation = date(2026, 1, 2)
        deadline = get_date_n_business_days(
            start_date=mediation,
            wait_n_days=-3,
            subdiv=SUBDIV,
            remove_holidays=REMOVE_HOLIDAYS
        )
        # New Year's is Thu Jan 1, so going back 3 business days:
        # Wed Dec 31, Tue Dec 30, Mon Dec 29
        assert deadline == date(2025, 12, 29)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
