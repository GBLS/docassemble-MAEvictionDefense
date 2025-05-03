Feature: MADE tests

Since the tests are so long and many scenarios don't conflict, some have been combined.

- [√] User has a court date scheduled (Expected: Should get a court date printed on the Answer.)
- [√] User does not have a court date scheduled (Expected: Court date should be printed as "TBD" on the Answer.)
- [√] User court date has already passed. (Expected: Should get an exit warning screen. You can stop after the warning screen is reached.)
- [√] User has a federal mortgage and a 14 day notice to quit. (Expected: Defense on for CARES act should appear on the Answer. It should say that the wrong NTQ type was used.)
- [√] User does not have a federal mortgage. Has filed the CDC declaration. (Expected: Should get a defense related to CDC declaration printed on the Answer.)
- [√] User has not filed the CDC declaration. (Expected: No CDC defense should appear on the Answer.)
- [√] User has a "fault" case (something other than non-payment of rent) (Expected: No bugs along the way)
- [√] User has a public housing voucher. (Expected: No bugs along the way)
- [√] User has a delay in receiving RAFT rental assistance which caused to fall behind in rent. (Expected: Causes 2 paragraphs to appear in the answer: RAFT defense should appear on the answer. Relief requested should include a delay in the case until RAFT is completed.)

@fast @1 

Scenario: User's court date has passed
  Given I start the interview at "eviction"
  Then I get to the question id "not right interview" with this data:
    | var | value | trigger |
    | person_answering | tenant |  |
    | how_to_answer | continue |  |
    | case.status | late |  |

@slow @2 @federal
Scenario: User has a federal mortgage and a 14 day notice to quit
  Given I start the interview at "eviction"
  Then I get to the question id "signature" with this data:
    | var | value | trigger |
    | person_answering | tenant |  |
    | how_to_answer | continue |  |
    | case.status | summons |  |
    | tenant.address.address | 112 Southampton St. |  |
    | tenant.address.unit | 1 |  |
    | tenant.address.city | Boston |  |
    | tenant.address.state | MA |  |
    | tenant.address.zip | 02118 |  |
    | facts.tenant_address_is_eviction_address | True |  |
    | tenant.name.first | Uli |  |
    | tenant.name.last | Ulther |  |
    | additional_tenants.there_are_any | False |  |
    | tenant.name_different_on_summons | False |  |
    | remind_user | True |  |
    | survey_user | True |  |
    | edit_contact_info | True |  |
    | landlord.name.text | Len Lessor |  |
    | landlord.is_new | False |  |
    | court | macourts[31] |  |
    | landlord.has_attorney | False |  |
    | case.hearing_date_assigned | True |  |
    | case.first_event | 01/01/2025 |  |
    | eviction_all_reasons['nonpayment'] | True |  |
    | covid_cares_has_federal_mortgage | True |  |
    | covid_cdc_moratorium | False |  |
    | facts.tenant_movein | 01/01/2019 |  |
    | facts.tenant_rent_share | 1 |  |
    | facts.tenant_rent_frequency | month |  |
    | tenancy_type | lease |  |
    | notice_type | fourteen_day |  |
    | ntq_includes_tenant_name | True |  |
    | ntq_includes_all_tenants | True |  |
    | ntq_includes_correct_address | True |  |
    | dont_owe_rent | True |  |
    | behind_in_rent | True |  |
    | lease_type | fixed_term |  |
    | lease_end_date | 01/01/2026 |  |
    | date_received_ntq | 01/01/2020 |  |
    | date_received_summons | 02/01/2020 |  |
    | ntq_matches_summons | True |  |
    | summons_includes_all_tenants | True |  |
    | summons_includes_correct_address | True |  |
    | ntq_contains_reservation | True |  |
    | bad_conditions.conditions['None'] | True |  |
    | retaliation.is_retaliated | False |  |
    | tenant.is_discriminated | False |  |
    | claim_jurytrial | False |  |
    | needs_time_because | Busy |  |
    | tenant_review_discovery | False |  |
  And I set the var "signature_choice" to "this device"
  And I sign
  And I tap to continue
  And the max seconds for each step is 200
  Then I get to the question id "download screen" with this data:
    | var | value | trigger |
    | method_of_service | emailed |  |
    | service_date | 01/01/2024 |  |
    | ask_intake_questions | skip |  |
  And I wait 1 second
  Then I download "Eviction_Forms.zip"

@slow @3 @cdc
Scenario: User has NO federal mortgage, but HAS filed the CDC declaration
  Given I start the interview at "eviction"
  Then I get to the question id "signature" with this data:
    | var | value | trigger |
    | person_answering | tenant |  |
    | how_to_answer | continue |  |
    | case.status | summons |  |
    | tenant.address.address | 112 Southampton St. |  |
    | tenant.address.unit | 1 |  |
    | tenant.address.city | Boston |  |
    | tenant.address.state | MA |  |
    | tenant.address.zip | 02118 |  |
    | facts.tenant_address_is_eviction_address | True |  |
    | tenant.name.first | Uli |  |
    | tenant.name.last | Ulther |  |
    | additional_tenants.there_are_any | False |  |
    | tenant.name_different_on_summons | False |  |
    | remind_user | True |  |
    | survey_user | True |  |
    | edit_contact_info | True |  |
    | landlord.name.text | Len Lessor |  |
    | landlord.is_new | False |  |
    | court | macourts[31] |  |
    | landlord.has_attorney | False |  |
    | case.hearing_date_assigned | True |  |
    | case.first_event | 01/01/2025 |  |
    | eviction_all_reasons['nonpayment'] | True |  |
    | covid_cdc_moratorium | True |  |
    | facts.tenant_movein | 01/01/2019 |  |
    | facts.tenant_rent_share | 1 |  |
    | facts.tenant_rent_frequency | month |  |
    | tenancy_type | lease |  |
    | notice_type | fourteen_day |  |
    | ntq_includes_tenant_name | True |  |
    | ntq_includes_all_tenants | True |  |
    | ntq_includes_correct_address | True |  |
    | dont_owe_rent | True |  |
    | behind_in_rent | True |  |
    | lease_type | fixed_term |  |
    | lease_end_date | 01/01/2026 |  |
    | date_received_ntq | 01/01/2020 |  |
    | date_received_summons | 02/01/2020 |  |
    | ntq_matches_summons | True |  |
    | summons_includes_all_tenants | True |  |
    | summons_includes_correct_address | True |  |
    | ntq_contains_reservation | True |  |
    | bad_conditions.conditions['None'] | True |  |
    | retaliation.is_retaliated | False |  |
    | tenant.is_discriminated | False |  |
    | claim_jurytrial | False |  |
    | needs_time_because | Busy |  |
    | tenant_review_discovery | False |  |
  And I set the var "signature_choice" to "this device"
  And I sign
  And I tap to continue
  And the max seconds for each step is 200
  Then I get to the question id "download screen" with this data:
    | var | value | trigger |
    | method_of_service | emailed |  |
    | service_date | 01/01/2024 |  |
    | ask_intake_questions | skip |  |
  And I wait 1 second
  Then I download "Eviction_Forms.zip"

@slow @4 @fault
Scenario: User has a "fault" case with NO court date and NO CDC declaration
  Given I start the interview at "eviction"
  Then I get to the question id "signature" with this data:
    | var | value | trigger |
    | person_answering | tenant |  |
    | how_to_answer | continue |  |
    | case.status | summons |  |
    | tenant.address.address | 112 Southampton St. |  |
    | tenant.address.unit | 1 |  |
    | tenant.address.city | Boston |  |
    | tenant.address.state | MA |  |
    | tenant.address.zip | 02118 |  |
    | facts.tenant_address_is_eviction_address | True |  |
    | tenant.name.first | Uli |  |
    | tenant.name.last | Ulther |  |
    | additional_tenants.there_are_any | False |  |
    | tenant.name_different_on_summons | False |  |
    | remind_user | True |  |
    | survey_user | True |  |
    | edit_contact_info | True |  |
    | landlord.name.text | Len Lessor |  |
    | landlord.is_new | False |  |
    | court | macourts[31] |  |
    | landlord.has_attorney | False |  |
    | case.hearing_date_assigned | False |  |
    | eviction_all_reasons['fault'] | True |  |
    | fault_basis['overcrowding'] | True |  |
    | covid_cdc_moratorium | False |  |
    | facts.tenant_movein | 01/01/2019 |  |
    | facts.tenant_rent_share | 1 |  |
    | facts.tenant_rent_frequency | week |  |
    | tenancy_type | lease |  |
    | notice_type | fourteen_day |  |
    | ntq_includes_tenant_name | True |  |
    | ntq_includes_all_tenants | True |  |
    | ntq_includes_correct_address | True |  |
    | dont_owe_rent | True |  |
    | behind_in_rent | False |  |
    | lease_type | fixed_term |  |
    | lease_end_date | 01/01/2026 |  |
    | date_received_ntq | 01/01/2020 |  |
    | date_received_summons | 02/01/2020 |  |
    | ntq_matches_summons | True |  |
    | summons_includes_all_tenants | True |  |
    | summons_includes_correct_address | True |  |
    | ntq_contains_reservation | True |  |
    | retaliation.is_retaliated | False |  |
    | tenant.is_discriminated | False |  |
    | claim_jurytrial | False |  |
    | needs_time_because | Busy |  |
    | tenant_review_discovery | False |  |
  And I set the var "signature_choice" to "this device"
  And I sign
  And I tap to continue
  And the max seconds for each step is 200
  Then I get to the question id "download screen" with this data:
    | var | value | trigger |
    | method_of_service | emailed |  |
    | service_date | 01/01/2024 |  |
    | ask_intake_questions | skip |  |
  And I wait 1 second
  Then I download "Eviction_Forms.zip"

@slow @5 @publichousing
Scenario: User has a public housing voucher with a court date
  Given I start the interview at "eviction"
  Then I get to the question id "signature" with this data:
    | var | value | trigger |
    | person_answering | tenant |  |
    | how_to_answer | continue |  |
    | case.status | summons |  |
    | tenant.address.address | 112 Southampton St. |  |
    | tenant.address.unit | 1 |  |
    | tenant.address.city | Boston |  |
    | tenant.address.state | MA |  |
    | tenant.address.zip | 02118 |  |
    | facts.tenant_address_is_eviction_address | True |  |
    | tenant.name.first | Uli |  |
    | tenant.name.last | Ulther |  |
    | additional_tenants.there_are_any | False |  |
    | tenant.name_different_on_summons | False |  |
    | remind_user | True |  |
    | survey_user | True |  |
    | edit_contact_info | True |  |
    | landlord.name.text | Len Lessor |  |
    | landlord.is_new | False |  |
    | court | macourts[31] |  |
    | landlord.has_attorney | False |  |
    | case.hearing_date_assigned | True |  |
    | case.first_event | 01/01/2025 |  |
    | eviction_all_reasons['nonpayment'] | True |  |
    | covid_cdc_moratorium | False |  |
    | facts.tenant_has_subsidy | True |  |
    | subsidy_type | Section 8 voucher |  |
    | facts.tenant_movein | 01/01/2019 |  |
    | facts.tenant_rent_share | 1 |  |
    | facts.tenant_contract_rent | 100 |  |
    | facts.tenant_rent_frequency | week |  |
    | tenancy_type | lease |  |
    | notice_type | fourteen_day |  |
    | ntq_includes_tenant_name | True |  |
    | ntq_includes_all_tenants | True |  |
    | ntq_includes_correct_address | True |  |
    | dont_owe_rent | True |  |
    | behind_in_rent | True |  |
    | lease_type | self_extending |  |
    | date_received_ntq | 01/01/2020 |  |
    | date_received_summons | 02/01/2020 |  |
    | ntq_matches_summons | True |  |
    | summons_includes_all_tenants | True |  |
    | summons_includes_correct_address | True |  |
    | ntq_contains_reservation | True |  |
    | subsidized_housing.no_proper_termination | True |  |
    | subsidized_housing.no_just_cause | True |  |
    | subsidized_housing.no_ntq_to_agency | False |  |
    | bad_conditions.conditions['None'] | True |  |
    | retaliation.is_retaliated | False |  |
    | tenant.is_discriminated | False |  |
    | claim_jurytrial | False |  |
    | needs_time_because | Busy |  |
    | tenant_review_discovery | False |  |
  And I set the var "signature_choice" to "this device"
  And I sign
  And I tap to continue
  And the max seconds for each step is 200
  Then I get to the question id "download screen" with this data:
    | var | value | trigger |
    | method_of_service | emailed |  |
    | service_date | 01/01/2024 |  |
    | ask_intake_questions | skip |  |
  And I wait 1 second
  Then I download "Eviction_Forms.zip"

@slow @6 @raft
Scenario: User fell behind because of RAFT delay
  Given I start the interview at "eviction"
  Then I get to the question id "signature" with this data:
    | var | value | trigger |
    | person_answering | tenant |  |
    | how_to_answer | continue |  |
    | case.status | summons |  |
    | tenant.address.address | 112 Southampton St. |  |
    | tenant.address.unit | 1 |  |
    | tenant.address.city | Boston |  |
    | tenant.address.state | MA |  |
    | tenant.address.zip | 02118 |  |
    | facts.tenant_address_is_eviction_address | True |  |
    | tenant.name.first | Uli |  |
    | tenant.name.last | Ulther |  |
    | additional_tenants.there_are_any | False |  |
    | tenant.name_different_on_summons | False |  |
    | remind_user | True |  |
    | survey_user | True |  |
    | edit_contact_info | True |  |
    | landlord.name.text | Len Lessor |  |
    | landlord.is_new | False |  |
    | court | macourts[31] |  |
    | landlord.has_attorney | False |  |
    | case.hearing_date_assigned | True |  |
    | case.first_event | 01/01/2025 |  |
    | eviction_all_reasons['nonpayment'] | True |  |
    | covid_cdc_moratorium | False |  |
    | delay_in_raft | True |  |
    | facts.tenant_movein | 01/01/2019 |  |
    | subsidy_type | Section 8 voucher |  |
    | facts.tenant_rent_share | 1 |  |
    | facts.tenant_rent_frequency | month |  |
    | tenancy_type | lease |  |
    | notice_type | fourteen_day |  |
    | ntq_includes_tenant_name | True |  |
    | ntq_includes_all_tenants | True |  |
    | ntq_includes_correct_address | True |  |
    | dont_owe_rent | True |  |
    | behind_in_rent | True |  |
    | lease_type | fixed_term |  |
    | lease_end_date | 01/01/2026 |  |
    | date_received_ntq | 01/01/2020 |  |
    | date_received_summons | 02/01/2020 |  |
    | ntq_matches_summons | True |  |
    | summons_includes_all_tenants | True |  |
    | summons_includes_correct_address | True |  |
    | ntq_contains_reservation | True |  |
    | bad_conditions.conditions['None'] | True |  |
    | retaliation.is_retaliated | False |  |
    | tenant.is_discriminated | False |  |
    | claim_jurytrial | False |  |
    | needs_time_because | Busy |  |
    | tenant_review_discovery | False |  |
  And I set the var "signature_choice" to "this device"
  And I sign
  And I tap to continue
  And the max seconds for each step is 200
  Then I get to the question id "download screen" with this data:
    | var | value | trigger |
    | method_of_service | emailed |  |
    | service_date | 01/01/2024 |  |
    | ask_intake_questions | skip |  |
  And I wait 1 second
  Then I download "Eviction_Forms.zip"
