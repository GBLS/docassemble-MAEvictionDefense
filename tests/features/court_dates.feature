Feature: MADE tests

- [ ] User has a court date scheduled (Expected: Should get a court date printed on the Answer.)
- [ ] User does not have a court date scheduled (Expected: Court date should be printed as "TBD" on the Answer.)
- [√] User court date has already passed. (Expected: Should get an exit warning screen. You can stop after the warning screen is reached.)
- [ ] User has a federal mortgage and a 14 day notice to quit. (Expected: Defense on for CARES act should appear on the Answer. It should say that the wrong NTQ type was used.)
- [ ] User does not have a federal mortgage. Has filed the CDC declaration. (Expected: Should get a defense related to CDC declaration printed on the Answer.)
- [ ] User has not filed the CDC declaration. (Expected: No CDC defense should appear on the Answer.)
- [√] User has a "fault" case (something other than non-payment of rent) (Expected: No bugs along the way)
- [√] User has a public housing voucher. (Expected: No bugs along the way)
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

#Scenario: User's court date has passed
#  Given I start the interview at "eviction"
#  When I tap the button "Next"
#  And I tap the button "Tenant"
#  And I tap the button "I agree"
#  And I tap the button "Next"
#  And I tap the "missed" choice
#  And I tap the button "Next"
#  Then I should see the phrase "Exit"

#Scenario: User has a federal mortgage and a 14 day notice to quit.
#  # Cannot examine PDF

#Scenario: User does not have a federal mortgage. Has filed the CDC declaration.
#  # Cannot examine PDF

#Scenario: User has not filed the CDC declaration.
#  # Cannot examine PDF

#Scenario: User has a "fault" case (something other than non-payment of rent)
#  Given I start the interview at "eviction"
#  Then the question id should be "intro screen"
#  When I tap the button "Next"
#  Then the question id should be "who is using"
#  When I tap the button "Tenant"
#  Then the question id should be "how to answer"
#  When I tap the button "I agree"
#  Then the question id should be "tenant rights"
#  When I tap the button "Next"
#  #Then the question id should be "None"  # this element doesn't show up in this case
#  When I tap the "I got a notice" choice
#  When I tap the button "Next"
#  Then the question id should be "address"
#  When I set the address of the var "tenant" to "112 Southampton St., Unit 1, Boston, MA 02118"
#  When I tap the button "Next"
#  Then the question id should be "your name"
#  When I set the name of the variable "tenant" to "Uli Ula Ulther III"
#  When I tap the button "Next"
#  Then the question id should be "additional tenants"
#  When I tap the button "No"
#  Then the question id should be "how named on summons"
#  When I tap the button "Next"
#  Then the question id should be "reminders"
#  When I tap the "Remind" choice
#  When I tap the "Send" choice
#  When I tap the "Edit" choice
#  When I tap the button "Next"
#  Then the question id should be "landlords name"
#  When I set the "name" text field to "Len Lessor"
#  When I tap the button "Next"
#  Then the question id should be "landlord information"
#  When I tap the button "Next"
#  Then the question id should be "landlords attorney"
#  When I tap the button "Next"
#  Then the question id should be "court information"
#  When I tap the button "Next"
#  Then the question id should be "court date"
#  When I tap the "Yes" choice
#  When I set the "When" text field to "01/01/2025"
#  When I tap the button "Next"
#  Then the question id should be "eviction reason"
#  When I tap the "other than owe rent" choice
#  When I tap the button "Next"
#  Then the question id should be "fault reason"
#  When I tap the "Overcrowding" choice
#  When I tap the button "Next"
#  Then the question id should be "defense overview"
#  When I tap the button "Next"
#  Then the question id should be "covid-19"
#  When I tap the "No" choice
#  When I tap the button "Next"
#  Then the question id should be "tenant facts"
#  When I tap the button "Next"
#  Then the question id should be "rental agreement"
#  When I set the "move in" text field to "01/01/2019"
#  When I set the "What do you pay" text field to "1"
#  And I set the var "facts.tenant_rent_frequency" to "week"
#  When I select "a lease" from the "rental agreement" dropdown
#  When I tap the button "Next"
#  When I wait 1 second
#  Then the question id should be "tenancy facts"
#  When I tap the button "Next"
#  Then the question id should be "notice to quit facts"
#  When I select "14 day" from the "Kind" dropdown
#  When I tap the button "Next"
#  Then the question id should be "lease type"
#  When I select "ends" from the "period is over" dropdown
#  When I set the "lease ends" text field to "01/01/2026"
#  When I tap the button "Next"
#  Then the question id should be "notice timing"
#  When I set the "to quit" text field to "01/01/2020"
#  When I set the "to go to court" text field to "02/01/2020"
#  When I tap the button "Next"
#  Then the question id should be "nonpayment defenses"
#  When I tap the "No" choice
#  When I tap the button "Next"
#  Then the question id should be "summons facts"
#  When I tap the button "Next"
#  Then the question id should be "waiver"
#  When I tap the button "Next"
#  Then the question id should be "have a defense"
#  When I tap the button "Continue"
#  Then the question id should be "retaliation splash"
#  When I tap the button "No"
#  Then the question id should be "discrimination splash"
#  When I tap the button "No"
#  Then the question id should be "fault defenses"
#  When I tap the button "Next"
#  Then the question id should be "jury trial"
#  When I tap the button "Keep"
#  Then the question id should be "time to move"
#  When I set the "Explain" text field to "Busy"
#  When I tap the button "Next"
#  Then the question id should be "almost done"
#  When I tap the button "Next"
#  # None can't be a page id
#  When I tap the button "Keep"
#  Then the question id should be "signature"
#  When I tap the button "computer"
#  When I sign
#  When I tap the button "Next"
#  Then the question id should be "method of service"
#  When I select "Mail" from the "Delivery method" dropdown
#  When I set the "Date" text field to "01/01/2024"
#  When I tap the button "Next"
#  # None can't be page id
#  When I tap the button "Skip"
#  Then the question id should be "download screen"
#  Then I wait 30 seconds
#  Then I download "Eviction_Forms.zip"

Scenario: User has a public housing voucher.
  Given I start the interview at "eviction"
  Then the question id should be "intro screen"
#  When I tap to continue
#  Then the question id should be "who is using"
#  When I set the var "person_answering" to "tenant"
#  Then the question id should be "how to answer"
#  When I set the var "how_to_answer" to "continue"
#  Then the question id should be "tenant rights"
#  When I tap to continue
#  #None (update to "your eviction case" when update to master)
#  When I tap the var "case.status" with the value "summons"
#  When I tap to continue
#  Then the question id should be "address"
#  When I set the variable "tenant.address.address" to "112 Southampton St"
#  And I set the var "tenant.address.unit" to "1"
#  And I set the var "tenant.address.city" to "Boston"
#  And I set the var "tenant.address.state" to "MA"
#  And I set the var "tenant.address.zip" to "02118"
#  And I tap to continue
#  Then the question id should be "your name"
#  When I set the var "tenant.name.first" to "Uli"
#  And I set the var "tenant.name.last" to "User"
#  And I tap to continue
#  Then the question id should be "additional tenants"
#  When I set the var "additional_tenants.there_are_any" to "False"
#  Then the question id should be "how named on summons"
#  When I tap to continue
#  Then the question id should be "reminders"
#  When I tap the checkbox var "remind_user"
#  And I tap the checkbox var "survey_user"
#  And I tap the checkbox var "edit_contact_info"
#  When I tap to continue
#  Then the question id should be "landlords name"
#  When I set the var "landlord.name.text" to "Len Lessor"
#  When I tap to continue
#  Then the question id should be "landlord information"
#  When I tap to continue
#  Then the question id should be "landlords attorney"
#  When I tap to continue
#  Then the question id should be "court information"
#  When I tap to continue
#  Then the question id should be "court date"
#  When I tap the var "case.covid_hearing_date_assigned" with the value "True"
#  And I set the var "case.covid_first_event" to "01/01/2025"
#  When I tap to continue
#  Then the question id should be "eviction reason"
#  When I tap the checkbox var "eviction_all_reasons" with the value "nonpayment"
#  When I tap to continue
#
#  Then the question id should be "defense overview"
#  When I tap to continue
#  Then the question id should be "covid-19"
#  When I tap the var "covid_cdc_moratorium" with the value "False"
#  And I tap to continue
#  Then the question id should be "tenant facts"
#  When I tap the var "facts.tenant_has_subsidy"
#  And I tap to continue
#  Then the question id should be "subsidy facts"
#  When I tap the var "subsidy_type" with the value "Section 8 voucher"
#  And I tap to continue
#  
#  Then the question id should be "rental agreement"
#  When I set the var "facts.tenant_movein" to "01/01/2019"
#  And I set the var "facts.tenant_rent_share" to "1"
#  And I set the var "facts.tenant_contract_rent" to "100"
#  And I set the var "facts.tenant_rent_frequency" to "week"
#  And I set the var "tenancy_type" to "lease"
#  And I tap to continue
#  And I wait 1 second
#  Then the question id should be "notice to quit facts"
#  When I tap to continue
#  Then the question id should be "nonpayment defenses"
#  When I tap to continue
#  Then the question id should be "lease type"
#  When I set the var "lease_type" to "self_extending"
#  And I tap to continue
#  Then the question id should be "notice timing"
#  When I set the var "date_received_ntq" to "01/01/2020"
#  And I set the var "date_received_summons" to "01/02/2020"
#  And I tap to continue
#  Then the question id should be "summons facts"
#  When I tap to continue
#  Then the question id should be "nonpayment cure"
#  When I tap to continue
#  Then the question id should be "waiver"
#  When I tap to continue
#  Then the question id should be "have a defense"
#  When I tap to continue
#  Then the question id should be "tenancy facts"
#  When I tap to continue
#  Then the question id should be "subsidy defenses 2"
#  When I tap the var "subsidized_housing.no_ntq_to_agency" with the value "False"
#  And I tap to continue
#  Then the question id should be "subsidy defenses 1"
#  And I tap to continue
#  Then the question id should be "bad conditions"
#  # The below doesn't really need "None", but it's probably a bit confusing otherwise
#  When I tap the var "bad_conditions.conditions" with the value "None"
#  And I tap to continue
#  Then the question id should be "retaliation splash"
#  When I set the var "retaliation.is_retaliated" to "False"
#  Then the question id should be "discrimination splash"
#  When I set the var "tenant.is_discriminated" to "False"
#  Then the question id should be "consumer protection"
#  When I tap to continue
#  Then the question id should be "jury trial"
#  When I set the var "claim_jurytrial" to "False"
#  Then the question id should be "time to move"
#  When I set the var "needs_time_because" to "Busy"
#  And I tap to continue
#  Then the question id should be "almost done"
#  When I tap to continue
#  # None can't be a page id
#  When I set the var "tenant_review_discovery" to "False"
#  Then the question id should be "signature"
#  When I set the var "signature_choice" to "this device"
#  And I sign
#  And I tap to continue
#  Then the question id should be "method of service"
#  When I set the var "method_of_service" to "emailed"
#  And I set the var "service_date" to "01/01/2024"
#  And I tap to continue
#  #None (update to master: Then the question id should be "intake opener")
#  When I set the var "ask_intake_questions" to "skip"
#  Then the question id should be "download screen"
#  Then I download "Eviction_Forms.zip"

#Scenario: User has a delay in receiving RAFT rental assistance which caused to fall behind in rent.
#  # Cannot examine PDF
