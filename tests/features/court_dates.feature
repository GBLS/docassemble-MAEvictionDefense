Feature: MADE tests

- [ ] User has a court date scheduled (Expected: Should get a court date printed on the Answer.)
- [ ] User does not have a court date scheduled (Expected: Court date should be printed as "TBD" on the Answer.)
- [√] User court date has already passed. (Expected: Should get an exit warning screen. You can stop after the warning screen is reached.)
- [ ] User has a federal mortgage and a 14 day notice to quit. (Expected: Defense on for CARES act should appear on the Answer. It should say that the wrong NTQ type was used.)
- [ ] User does not have a federal mortgage. Has filed the CDC declaration. (Expected: Should get a defense related to CDC declaration printed on the Answer.)
- [ ] User has not filed the CDC declaration. (Expected: No CDC defense should appear on the Answer.)
- [ ] User has a "fault" case (something other than non-payment of rent) (Expected: No bugs along the way)
- [ ] User has a public housing voucher. (Expected: No bugs along the way)
- [ ] User has a delay in receiving RAFT rental assistance which caused to fall behind in rent. (Expected: Cauxses 2 paragraphs to appear in the answer: RAFT defense should appear on the answer. Relief requested should include a delay in the case until RAFT is completed.)

#Scenario: User HAS a court date scheduled
#  # Cannot examine PDF
#  Given I start the interview at "eviction"
#  When I tap the button "Next"
#  When I tap the button "Tenant"
#  When I tap the button "I agree"
#  When I tap the button "Next"
#  When I tap the "I got a notice" choice
#  When I tap the button "Next"
#  When I set the "address" text field to "112 Southampton St"
#  When I set the "unit" text field to "1"
#  When I set the "city" text field to "Boston"
#  When I select "Massachusetts" from the "state" dropdown
#  When I set the "zip" text field to "02118"
#  When I tap the button "Next"

#Scenario: User does NOT have a court date scheduled
#  # Cannot examine PDF

Scenario: User's court date has passed
  Given I start the interview at "eviction"
  When I tap the button "Next"
  When I tap the button "Tenant"
  When I tap the button "I agree"
  When I tap the button "Next"
  When I tap the "missed" choice
  When I tap the button "Next"
  Then I should see the phrase "Exit"

#Scenario: User has a federal mortgage and a 14 day notice to quit.
#  # Cannot examine PDF

#Scenario: User does not have a federal mortgage. Has filed the CDC declaration.
#  # Cannot examine PDF

#Scenario: User has not filed the CDC declaration.
#  # Cannot examine PDF

Scenario: User has a "fault" case (something other than non-payment of rent)
  Given I start the interview at "eviction"
  When I tap the button "Next"
  When I tap the button "Tenant"
  When I tap the button "I agree"
  When I tap the button "Next"
  When I tap the "I got a notice" choice
  When I tap the button "Next"
  When I set the "address" text field to "112 Southampton St"
  When I set the "unit" text field to "1"
  When I set the "city" text field to "Boston"
  When I select "Massachusetts" from the "state" dropdown
  When I set the "zip" text field to "02118"
  When I tap the button "Next"
  When I set the "First Name" text field to "Uli"
  When I set the "Last Name" text field to "User"
  When I tap the button "Next"
  When I tap the button "No"  # other tenants
  When I tap the button "Next"
  When I tap the "Remind" choice
  When I tap the "Send" choice
  When I tap the "Edit" choice
  When I tap the button "Next"
  When I set the "name" text field to "Len Lessor"
  When I tap the button "Next"
  When I tap the button "Next"  # Info about attorney
  When I tap the button "Next"  # Landlord has attorney
  When I tap the button "Next"  # Which court
  When I tap the "Yes" choice


#Scenario: User has a public housing voucher.
#  Given

#Scenario: User has a delay in receiving RAFT rental assistance which caused to fall behind in rent.
#  # Cannot examine PDF
