Feature: MADE tests

Since the tests are so long and many scenarios don't conflict, some have been combined.

- [√] User has a court date scheduled (Expected: Should get a court date printed on the Answer.)
- [√] User does not have a court date scheduled (Expected: Court date should be printed as "TBD" on the Answer.)
- [√] User court date has already passed. (Expected: Should get an exit warning screen. You can stop after the warning screen is reached.)
- [√] User has a "fault" case (something other than non-payment of rent) (Expected: No bugs along the way)
- [√] User has a public housing voucher. (Expected: No bugs along the way)
- [√] User has a delay in receiving RAFT rental assistance which caused to fall behind in rent. (Expected: Causes 2 paragraphs to appear in the answer: RAFT defense should appear on the answer. Relief requested should include a delay in the case until RAFT is completed.)
- Attorney worksheet: entering an appearance and ghostwriting, discovery review,
  paper signing, service, and downloads in a no-fault case.

@fast @1 

Scenario: User's court date has passed
  Given I start the interview at "eviction"
  And the max seconds for each step is 200
  Then I get to the question id "not right interview" with this data:
    | var | value | trigger |
    | person_answering | tenant |  |
    | how_to_answer | continue |  |
    | case.status | late |  |

@slow @4 @fault
Scenario: User has a "fault" case with NO court date
  Given I start the interview at "eviction"
  And the max seconds for each step is 200
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
    | email_after_completion | False |  |
    | remind_user | False |  |
    | survey_user | False |  |
    | edit_contact_info | False |  |
    | landlord.name.text | Len Lessor |  |
    | landlord.organization_type | other |  |
    | landlord.is_new | False |  |
    | court | macourts[31] |  |
    | transfer_to_housing_court | False |  |
    | landlord.has_attorney | False |  |
    | case.entry_date | today - 10 |  |
    | case.hearing_date_assigned | False |  |
    | case_is_on_time | True |  |
    | eviction_all_reasons['fault'] | True |  |
    | fault_basis['overcrowding'] | True |  |
    | fault.did_not_occur | True |  |
    | fault.not_violation_of_agreement | True |  |
    | fault.no_control_of_guest | False |  |
    | initial_defense.avoidance_of_forfeiture | True |  |
    | facts.tenant_has_subsidy | False |  |
    | tenant.is_nonnativespeaker | False |  |
    | tenant.is_disabled | False |  |
    | tenant.is_under6 | False |  |
    | tenant.is_over60 | False |  |
    | tenant.is_dvvictim | False |  |
    | postforeclosure.is_foreclosed | False |  |
    | claims.harassment | False |  |
    | is_condo_conversion | False |  |
    | is_pca | False |  |
    | facts.tenant_movein | today - 730 |  |
    | facts.tenant_rent_share | 1 |  |
    | facts.tenant_rent_frequency | week |  |
    | tenancy_type | lease |  |
    | notice_type | thirty_day |  |
    | ntq_includes_tenant_name | True |  |
    | ntq_includes_all_tenants | True |  |
    | ntq_includes_correct_address | True |  |
    | lease_requires_30_day_notice | False |  |
    | ntq_leaves_off_required_language | False |  |
    | lease_type | fixed_term |  |
    | lease_end_date | today + 365 |  |
    | date_received_ntq | today - 90 |  |
    | date_received_summons | today - 20 |  |
    | summons_in_hand | True |  |
    | summons_mailed | False |  |
    | summons_last_and_usual | False |  |
    | ntq_matches_summons | True |  |
    | summons_includes_all_tenants | True |  |
    | summons_includes_correct_address | True |  |
    | post_ntq_waiver['None'] | True |  |
    | retaliation.is_retaliated | False |  |
    | tenant.is_discriminated | False |  |
    | occupancy_ordinance_applies | False |  |
    | claim_jurytrial | False |  |
    | needs_time_because | Busy |  |
    | tenant_review_discovery | False |  |
  And I set the var "signature_choice" to "this device"
  And I sign
  And I tap to continue
  Then I get to the question id "download screen" with this data:
    | var | value | trigger |
    | method_of_service | emailed |  |
    | service_date | today |  |
    | ask_intake_questions | skip |  |
  And I wait 1 second
  Then I download "Eviction_Forms.zip"

@slow @5 @publichousing
Scenario: User has a public housing voucher with a court date
  Given I start the interview at "eviction"
  And the max seconds for each step is 200
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
    | email_after_completion | False |  |
    | remind_user | False |  |
    | survey_user | False |  |
    | edit_contact_info | False |  |
    | landlord.name.text | Len Lessor |  |
    | landlord.organization_type | other |  |
    | landlord.is_new | False |  |
    | court | macourts[31] |  |
    | transfer_to_housing_court | False |  |
    | landlord.has_attorney | False |  |
    | case.entry_date | today - 10 |  |
    | case.hearing_date_assigned | True |  |
    | case.first_event | today + 60 |  |
    | eviction_all_reasons['nonpayment'] | True |  |
    | tenant_got_accompanying_form | False |  |
    | facts.tenant_has_subsidy | True |  |
    | subsidy_type | Section 8 voucher |  |
    | delay_in_raft | False |  |
    | tenant.is_nonnativespeaker | False |  |
    | tenant.is_disabled | False |  |
    | tenant.is_under6 | False |  |
    | tenant.is_over60 | False |  |
    | tenant.is_dvvictim | False |  |
    | postforeclosure.is_foreclosed | False |  |
    | claims.harassment | False |  |
    | is_condo_conversion | False |  |
    | is_pca | False |  |
    | facts.tenant_movein | today - 730 |  |
    | facts.tenant_rent_share | 1 |  |
    | facts.tenant_contract_rent | 100 |  |
    | facts.tenant_rent_frequency | week |  |
    | tenancy_type | lease |  |
    | notice_type | fourteen_day |  |
    | ntq_includes_tenant_name | True |  |
    | ntq_includes_all_tenants | True |  |
    | ntq_includes_correct_address | True |  |
    | lease_requires_30_day_notice | False |  |
    | ntq_leaves_off_required_language | False |  |
    | dont_owe_rent | True |  |
    | behind_in_rent | True |  |
    | refused_rent_increase | False |  |
    | attempted_full_cure | False |  |
    | attempted_offered_cure | False |  |
    | other.vendor_payments | False |  |
    | initial_defense.avoidance_of_forfeiture | True |  |
    | paid_rent_owed | True |  |
    | lease_type | self_extending |  |
    | date_received_ntq | today - 90 |  |
    | date_received_summons | today - 20 |  |
    | summons_in_hand | True |  |
    | summons_mailed | False |  |
    | summons_last_and_usual | False |  |
    | ntq_matches_summons | True |  |
    | summons_includes_all_tenants | True |  |
    | summons_includes_correct_address | True |  |
    | post_ntq_waiver['None'] | True |  |
    | subsidized_housing.pha_pays_rent | True |  |
    | subsidized_housing.stopped_payment | False |  |
    | subsidized_housing.improper_rent_calculation | False |  |
    | subsidized_housing.landlord_overcharged | False |  |
    | subsidized_housing.no_proper_termination | True |  |
    | subsidized_housing.no_just_cause | True |  |
    | subsidized_housing.no_ntq_to_agency | False |  |
    | subsidized_housing.vawa | False |  |
    | bqe.locked_out | False |  |
    | bqe.entered_without_permission | False |  |
    | claims.utilities | False |  |
    | paid_deposit | False |  |
    | paid_lmr | False |  |
    | bad_conditions.conditions['None'] | True |  |
    | consumer_protection.late_fees | False |  |
    | consumer_protection.nonagreed_rent | False |  |
    | consumer_protection.unlawful_court_fees | False |  |
    | consumer_protection.unlawful_lease_terms | False |  |
    | consumer_protection.other | False |  |
    | retaliation.is_retaliated | False |  |
    | tenant.is_discriminated | False |  |
    | occupancy_ordinance_applies | False |  |
    | claim_jurytrial | False |  |
    | needs_time_because | Busy |  |
    | tenant_review_discovery | False |  |
  And I set the var "signature_choice" to "this device"
  And I sign
  And I tap to continue
  Then I get to the question id "download screen" with this data:
    | var | value | trigger |
    | method_of_service | emailed |  |
    | service_date | today |  |
    | ask_intake_questions | skip |  |
  And I wait 1 second
  Then I download "Eviction_Forms.zip"

@slow @6 @raft
Scenario: User fell behind because of RAFT delay
  Given I start the interview at "eviction"
  And the max seconds for each step is 200
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
    | email_after_completion | False |  |
    | remind_user | False |  |
    | survey_user | False |  |
    | edit_contact_info | False |  |
    | landlord.name.text | Len Lessor |  |
    | landlord.organization_type | other |  |
    | landlord.is_new | False |  |
    | court | macourts[31] |  |
    | transfer_to_housing_court | False |  |
    | landlord.has_attorney | False |  |
    | case.entry_date | today - 10 |  |
    | case.hearing_date_assigned | True |  |
    | case.first_event | today + 60 |  |
    | eviction_all_reasons['nonpayment'] | True |  |
    | tenant_got_accompanying_form | False |  |
    | delay_in_raft | True |  |
    | discrimination.raft_refusal | True |  |
    | tenant.is_nonnativespeaker | False |  |
    | tenant.is_disabled | False |  |
    | tenant.is_under6 | False |  |
    | tenant.is_over60 | False |  |
    | tenant.is_dvvictim | False |  |
    | postforeclosure.is_foreclosed | False |  |
    | claims.harassment | False |  |
    | is_condo_conversion | False |  |
    | is_pca | False |  |
    | facts.tenant_movein | today - 730 |  |
    | facts.tenant_has_subsidy | True |  |
    | subsidy_type | Section 8 voucher |  |
    | subsidized_housing.pha_pays_rent | True |  |
    | subsidized_housing.stopped_payment | False |  |
    | subsidized_housing.improper_rent_calculation | False |  |
    | subsidized_housing.landlord_overcharged | False |  |
    | subsidized_housing.no_proper_termination | True |  |
    | subsidized_housing.no_just_cause | True |  |
    | subsidized_housing.no_ntq_to_agency | False |  |
    | subsidized_housing.vawa | False |  |
    | facts.tenant_rent_share | 1 |  |
    | facts.tenant_rent_frequency | month |  |
    | tenancy_type | lease |  |
    | notice_type | fourteen_day |  |
    | ntq_includes_tenant_name | True |  |
    | ntq_includes_all_tenants | True |  |
    | ntq_includes_correct_address | True |  |
    | lease_requires_30_day_notice | False |  |
    | ntq_leaves_off_required_language | False |  |
    | dont_owe_rent | True |  |
    | behind_in_rent | True |  |
    | refused_rent_increase | False |  |
    | attempted_full_cure | False |  |
    | attempted_offered_cure | False |  |
    | other.vendor_payments | False |  |
    | initial_defense.avoidance_of_forfeiture | True |  |
    | paid_rent_owed | True |  |
    | lease_type | fixed_term |  |
    | lease_end_date | today + 365 |  |
    | date_received_ntq | today - 90 |  |
    | date_received_summons | today - 20 |  |
    | summons_in_hand | True |  |
    | summons_mailed | False |  |
    | summons_last_and_usual | False |  |
    | ntq_matches_summons | True |  |
    | summons_includes_all_tenants | True |  |
    | summons_includes_correct_address | True |  |
    | post_ntq_waiver['None'] | True |  |
    | bqe.locked_out | False |  |
    | bqe.entered_without_permission | False |  |
    | claims.utilities | False |  |
    | paid_deposit | False |  |
    | paid_lmr | False |  |
    | bad_conditions.conditions['None'] | True |  |
    | consumer_protection.late_fees | False |  |
    | consumer_protection.nonagreed_rent | False |  |
    | consumer_protection.unlawful_court_fees | False |  |
    | consumer_protection.unlawful_lease_terms | False |  |
    | consumer_protection.other | False |  |
    | retaliation.is_retaliated | False |  |
    | tenant.is_discriminated | True |  |
    | discrimination.protected_classes['receipt of rental assistance'] | True |  |
    | discrimination.show_other | False |  |
    | occupancy_ordinance_applies | False |  |
    | claim_jurytrial | False |  |
    | needs_time_because | Busy |  |
    | tenant_review_discovery | False |  |
  And I set the var "signature_choice" to "this device"
  And I sign
  And I tap to continue
  Then I get to the question id "download screen" with this data:
    | var | value | trigger |
    | method_of_service | emailed |  |
    | service_date | today |  |
    | ask_intake_questions | skip |  |
  And I wait 1 second
  Then I download "Eviction_Forms.zip"

@slow @attorney @worksheet
Scenario Outline: Attorney completes the no-fault worksheet with <representation> representation
  Given I start the interview at "eviction"
  And the max seconds for each step is 200
  Then I get to the question id "attorney worksheet" with this data:
    | var | value | trigger |
    | person_answering | attorney |  |
    | attorney_workflow | fast |  |
    | case.status | summons |  |
  # Stop at each discovery screen so this cannot silently use the tenant path.
  # Do not supply nonpayment/fault-only answers in this fresh no-fault session.
  Then I get to the question id "interrogatories" with this data:
    | var | value | trigger |
    | representation_type | <representation> |  |
    | tenants_attorney.name.first | Morgan |  |
    | tenants_attorney.name.last | Example |  |
    | tenants_attorney.bbo | 123456 |  |
    | tenants_attorney.phone_number | 202-555-0100 |  |
    | tenants_attorney.office | Example Legal Services |  |
    | tenants_attorney.address.address | 123 Example Street |  |
    | tenants_attorney.address.city | Boston |  |
    | tenants_attorney.address.state | MA |  |
    | tenants_attorney.address.zip | 02118 |  |
    | tenant.name.first | Taylor |  |
    | tenant.name.last | Example |  |
    | tenant.address.address | 112 Southampton St. |  |
    | tenant.address.unit | 1 |  |
    | tenant.address.city | Boston |  |
    | tenant.address.state | MA |  |
    | tenant.address.zip | 02118 |  |
    | facts.tenant_address_is_eviction_address | True |  |
    | additional_tenants.there_are_any | False |  |
    | tenant.name_different_on_summons | False |  |
    | email_after_completion | False |  |
    | remind_user | False |  |
    | survey_user | False |  |
    | landlord.name.text | Example Housing LLC |  |
    | landlord.organization_type | corporate |  |
    | landlord.is_new | False |  |
    | landlord.address.address | 456 Example Street |  |
    | landlord.address.city | Boston |  |
    | landlord.address.state | MA |  |
    | landlord.address.zip | 02118 |  |
    | landlord.has_attorney | <plaintiff_has_counsel> |  |
    | landlords_attorney.name.text | Jordan Example |  |
    | landlords_attorney.address.address | 789 Example Street |  |
    | landlords_attorney.address.city | Boston |  |
    | landlords_attorney.address.state | MA |  |
    | landlords_attorney.address.zip | 02118 |  |
    | court | macourts[31] |  |
    | transfer_to_housing_court | False |  |
    | case.entry_date | today - 10 |  |
    | case.hearing_date_assigned | True |  |
    | case.first_event | today + 60 |  |
    | include_late_answer_motion | False |  |
    | eviction_all_reasons['nofault'] | True |  |
    | nofault_basis['desire to sell'] | True |  |
    | facts.tenant_has_subsidy | False |  |
    | tenant.is_nonnativespeaker | False |  |
    | tenant.is_disabled | False |  |
    | tenant.is_under6 | False |  |
    | tenant.is_over60 | False |  |
    | tenant.is_dvvictim | False |  |
    | facts.tenant_movein | today - 730 |  |
    | is_pca | False |  |
    | facts.tenant_rent_share | 1500 |  |
    | facts.tenant_rent_frequency | month |  |
    | tenancy_type | taw |  |
    | postforeclosure.is_foreclosed | False |  |
    | claims.harassment | False |  |
    | is_condo_conversion | False |  |
    | notice_type | thirty_day |  |
    | ntq_includes_tenant_name | True |  |
    | ntq_includes_all_tenants | True |  |
    | ntq_includes_correct_address | True |  |
    | lease_requires_30_day_notice | False |  |
    | ntq_leaves_off_required_language | False |  |
    | date_received_ntq | today - 90 |  |
    | date_received_summons | today - 20 |  |
    | summons_in_hand | True |  |
    | summons_mailed | False |  |
    | summons_last_and_usual | False |  |
    | ntq_matches_summons | True |  |
    | summons_includes_all_tenants | True |  |
    | summons_includes_correct_address | True |  |
    | post_ntq_waiver['None'] | True |  |
    | bad_conditions.conditions['None'] | True |  |
    | retaliation.is_retaliated | False |  |
    | tenant.is_discriminated | False |  |
    | occupancy_ordinance_applies | False |  |
    | claims.utilities | False |  |
    | bqe.locked_out | False |  |
    | bqe.entered_without_permission | False |  |
    | bqe.heat | False |  |
    | bqe.hot_water | False |  |
    | bqe.unpaid_utilities | False |  |
    | bqe.shutoff_utilities | False |  |
    | bqe.removed_possessions | False |  |
    | bqe.bad_conditions | False |  |
    | paid_deposit | False |  |
    | paid_lmr | False |  |
    | consumer_protection.late_fees | False |  |
    | consumer_protection.nonagreed_rent | False |  |
    | consumer_protection.unlawful_court_fees | False |  |
    | consumer_protection.unlawful_lease_terms | False |  |
    | consumer_protection.other | False |  |
    | initial_defense.custom_reason_for_dismissal | TEST ONLY - custom dismissal ground. |  |
    | initial_defense.custom_other | TEST ONLY - custom defense check. |  |
    | needs_time_because | TEST ONLY - additional time to move requested. |  |
    | claim_jurytrial | True |  |
  When I tap to continue
  Then the question id should be "document requests"
  When I tap to continue
  Then the question id should be "signature"
  When I set the var "signature_choice" to "paper"
  Then I get to the question id "download screen" with this data:
    | var | value | trigger |
    | service_recipient | <recipient> |  |
    | service_performed_by | <delivered_by> |  |
    | method_of_service | delivered in-hand |  |
    | service_date | today |  |
    | ask_intake_questions | skip |  |
  And I wait 1 second
  Then I download "Eviction_Forms.zip"

  Examples:
    | representation | plaintiff_has_counsel | recipient | delivered_by |
    | entering_appearance | True | attorney | advocate |
    | ghostwriting | False | landlord | tenant |
