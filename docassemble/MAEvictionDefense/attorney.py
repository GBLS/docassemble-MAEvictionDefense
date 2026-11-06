"""Calculated answers to refresh after submitting the attorney worksheet.

Keep the factual answers and explicit pleading choices. Discovery has its own
merge step so that refreshing recommendations cannot erase reviewed selections.
"""

ATTORNEY_DERIVED_ANSWERS = (
    "all_answer_variables", "attorney_answer_variables", "common_answer_variables",
    "prepared_with_aoc", "case_title", "defendants_name", "eviction_address",
    "premises_address", "premises_street", "premises_city",
    "city_specific_occupancy_ordinance", "has_city_specific_occupancy_ordinance",
    "local_occupancy_ordinance_name", "local_occupancy_ordinance_requirement",
    "local_occupancy_ordinance_defense_text", "local_occupancy_ordinance_counterclaim_text",
    "occupancy_ordinance_defense_selected", "occupancy_ordinance_counterclaim_selected",
    "check_occupancy_ordinance_defense_selected", "check_occupancy_ordinance_counterclaim_selected",
    "initial_defense.local_occupancy_ordinance", "local_occupancy_ordinance_defense_summary",
    "local_occupancy_ordinance_counterclaim_summary", "facts.tenant_has_lease",
    "court_is_housing_court", "local_housing_court", "transfer_court_name",
    "case.original_date", "case.rescheduled_date", "case.answer_date",
    "case.answer_deadline_known", "case.on_time", "court_date",
    "court_date_is_holiday", "court_date_holiday", "eviction_reason",
    "eviction_detailed_reason", "set_plead_counterclaims", "plead_counterclaims",
    "plead_8a", "plead_93a", "attempted_cure", "tenant_type",
    "initial_defense.no_proper_termination", "initial_defense.need_ntq",
    "initial_defense.ntq_defective", "initial_defense.improper_time_given",
    "initial_defense.no_ntq", "initial_defense.premature_commencement",
    "initial_defense.varney", "initial_defense.defective_summons",
    "initial_defense.cure", "initial_defense.new_tenancy", "initial_defense.no_standing",
    "initial_defense.inconsistent_reasons", "has_defense",
    "bad_conditions.have_conditions", "bqe.violated", "other.repair_and_deduct_statute",
    "security_deposit.violated", "last_months_rent.violated", "plead_lead_paint",
    "loaded_discovery", "need_rental_value", "user_cell", "user_email",
    "didnt_provide_contact_info", "service_method_choices", "service_recipient_description",
    "date_discovery_received", "date_discovery_due", "date_motion_to_compel_due",
    "compel_discovery_with_instructions",
    "downloads", "downloads_pdf", "downloads_docx", "downloads_concat", "downloads_zip",
    "num_downloads", "download_titles_temp", "download_titles", "safe_filename",
)


def checkbox_none_selected(saved, choices=None):
    """Recognize saved empty checkbox answers without triggering gathering."""
    if saved is None:
        return False
    elements = getattr(saved, "elements", saved)
    if choices is not None:
        return not any(elements.get(key, False) for key in choices)
    return not any(elements.values())


def discovery_checked_value(recommended, previous=None, reviewed=False):
    """Apply new recommendations only until the user has reviewed the choices.

    A deliberate unchecked request is just as explicit as a checked request.
    New requests (with no previous boolean value) still receive a default.
    """
    if reviewed and isinstance(previous, bool):
        return previous
    return bool(recommended)
