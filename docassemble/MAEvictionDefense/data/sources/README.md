# Sources directory

This directory is used to store word translation files,
machine learning training files, and other source files.

## ALKiln Integration Tests

The following `.feature` files are used by ALKiln for integration testing:

- `court_dates.feature` - Main interview flow tests covering court dates,
  federal mortgages, CDC declarations, fault cases, housing vouchers, and RAFT delays
- `business_days.feature` - Tests for business day calculations using
  ALToolbox.business_days (verifies weekend and holiday handling for MA courts)

Run ALKiln tests via GitHub Actions or locally with the ALKiln CLI.

For unit tests of business day calculations, see `tests/test_business_days.py`.
