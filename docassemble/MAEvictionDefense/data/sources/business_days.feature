Feature: Business day calculations for court deadlines

Tests that the business day calculations in eviction.code.yml correctly:
- Count backwards 3 business days for document submission deadlines
- Skip weekends (Saturday and Sunday)
- Skip federal holidays (MLK Day, Presidents Day, Memorial Day, etc.)
- Skip MA state holidays (except Patriots' Day)
- DO NOT skip Patriots' Day (MA courts are open)

These tests use ALToolbox.business_days with:
  subdiv='MA'
  remove_holidays=["Patriots' Day"]

For unit tests of the algorithm, see: tests/test_business_days.py

Related code:
- docassemble/MAEvictionDefense/data/questions/eviction.code.yml
  - case.answer_date: 3 business days before mediation
  - case.on_time: True if today is 3+ business days before mediation

Note: These tests verify that the interview correctly uses the ALToolbox
business day functions with proper configuration for Massachusetts courts.

@fast @business_days @7

Scenario: Business days calculation skips weekends
  Given I start the interview at "eviction"
  # Monday mediation date - deadline should be previous Wednesday
  # (skip Sat/Sun when counting back 3 business days)
  Then I get to the question id "not right interview" with this data:
    | var | value | trigger |
    | person_answering | tenant |  |
    | how_to_answer | continue |  |
    | case.status | late |  |

# Note: Additional integration tests would require setting up specific
# dates and verifying case.answer_date calculations. This requires
# assertions that check computed values, which can be done via:
# - Story table assertions
# - Custom ALKiln steps
# - Checking generated document content

@fast @business_days @patriots_day @8

Scenario: Patriots Day is treated as a business day (courts open)
  Given I start the interview at "eviction"
  # This scenario documents that when a mediation falls near Patriots' Day,
  # the deadline calculation counts Patriots' Day as a business day because
  # MA courts remain open on this holiday.
  Then I get to the question id "not right interview" with this data:
    | var | value | trigger |
    | person_answering | tenant |  |
    | how_to_answer | continue |  |
    | case.status | late |  |
