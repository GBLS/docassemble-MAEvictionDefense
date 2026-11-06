# Sources directory

This directory is used to store word translation files,
machine learning training files, and other source files.

## ALKiln Integration Tests

The following `.feature` files are used by ALKiln for integration testing:

- `court_dates.feature` - Tenant interview tests covering a past court date,
  an unassigned court date, fault cases, housing vouchers, and RAFT delays.
  The `@attorney @worksheet` scenario outline also runs the single-page attorney
  worksheet with both entering-an-appearance and ghostwriting representation,
  checks both discovery review screens, chooses paper signing, answers service
  questions, and downloads the forms. It uses a fresh no-fault case without
  supplying hidden nonpayment or fault answers.

Run ALKiln tests via the **ALKiln v5 tests** GitHub Actions workflow or locally
with the ALKiln CLI and a docassemble test server. To run only the new attorney
coverage, use the workflow's `tags` input: `@attorney and @worksheet`.

Story tables explicitly answer branch choices and use relative dates so a future
court date does not expire. Copies, reminders, and surveys are disabled, and
tenant contact details are left blank. The service screen only shows
`service_performed_by` for attorneys and `service_recipient` when the landlord
has counsel; those conditional answers are in the attorney outline's service
table. A tenant without plaintiff counsel does not see either field.
`eviction.code.yml` supplies `service_performed_by = 'tenant'` for that hidden
field when the certificates are generated. Install that interview-code change
on the test server as well as uploading the feature file; an extra story-table
row cannot answer a field that is hidden from tenants.

Keep the attorney outline's final `Examples` table when copying the feature
into a Playground. Its two rows replace `<representation>`,
`<plaintiff_has_counsel>`, `<recipient>`, and `<delivered_by>` with actual answers.
`tests/test_alkiln_features.py` checks that outlines have examples and compile
without unresolved placeholders.
With Node.js on PATH, it also evaluates the current worksheet's visibility rules
against both attorney examples and names any missing required visible fields.
Run `python -m pytest -q tests/test_alkiln_features.py` before a server test.

The November 6, 2026 run in `ENV/alkiln-2026-11-06 at 17h13m47sUTC` reached
signing and service in all three tenant completion scenarios, then failed during
document generation after skipping intake because `service_performed_by` was
undefined. The attorney scenario timed out on the initial worksheet load before
filling any worksheet answers. Its saved HTML contains about 179,000 DOM elements,
mostly in the syntax-highlighted developer Source panel. This is a separate
browser timeout, not evidence of a missing worksheet answer. The corrected code
and examples still need a live rerun. If the Playground load continues to time
out, use the isolated-server workflow with the package installed and server debug
disabled. [Docassemble always includes the Source panel in Playground interviews](https://docassemble.org/docs/initial.html#debug),
even when the debug feature is disabled.

The follow-up run at `18h26m57sUTC` passed the tenant scenarios but still timed
out before filling either attorney worksheet. A fresh development session
reproduced that transition failure. Replaying its actual response with the
server's JavaScript showed the stall inside form initialization; removing only
the debug Source panel let the same form initialize in about two seconds.
That panel contained 30 copies of the roughly 70 KB worksheet definition.
The trace shows retries as the worksheet's field objects are created one by one.
Those objects and choice lists are now initialized in the small
`attorney_worksheet_ready` block. That block also prepares optional saved-checkbox
answers and Boston condominium defaults for the field templates. This reduces
repeated worksheet source in debug traces and preserves saved None selections.
These local changes need to be installed before the next
live attorney rerun; the timing comparison used the captured response, not a
server installation of the change.

For date calculation unit tests, see `tests/test_court_calendar.py`. Local Python
checks do not replace an ALKiln run against a docassemble server. Story-table
and relative-date syntax follow the [ALKiln writing guide](https://assemblyline.suffolklitlab.org/docs/components/ALKiln/writing/).
