"""Render production labels and Answer sections with inapplicable answers absent."""

from copy import deepcopy
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest
from docx import Document
from docxtpl import DocxTemplate
from jinja2 import Environment, StrictUndefined, UndefinedError
from mako.template import Template
from ruamel.yaml import YAML


DATA = Path(__file__).resolve().parents[1] / "docassemble/MAEvictionDefense/data"


class UnansweredCounsel:
    def __str__(self):
        pytest.fail("A no-counsel case must not request an attorney name")


@pytest.mark.parametrize("has_counsel", [False, True])
def test_service_labels_do_not_gather_hidden_counsel(has_counsel):
    blocks = YAML(typ="safe").load_all(
        (DATA / "questions/eviction.en.yml").read_text(encoding="utf-8")
    )
    screen = next(b for b in blocks if b and b.get("id") == "method of service")
    recipient = next(f for f in screen["fields"] if "service_recipient" in f.values())
    scope = {
        "landlord": SimpleNamespace(has_attorney=has_counsel),
        "landlords_attorney": "Jordan Example" if has_counsel else UnansweredCounsel(),
    }
    # Docassemble evaluates choice labels even when their field is hidden.
    labels = [Template(label).render(**scope) for choice in recipient["choices"] for label in choice]
    assert ("Jordan Example" in " ".join(labels)) is has_counsel


def render_answer_section(opening, context, start=None):
    """Render an actual balanced paragraph block, retaining docxtpl's processing."""
    paragraphs = Document(DATA / "templates/SummaryProcessAnswer.docx").paragraphs
    if start is None:
        start = next(i for i, p in enumerate(paragraphs) if opening in p.text)
    document = Document()
    depth = 0
    for paragraph in paragraphs[start:]:
        text = paragraph.text.strip()
        if text.startswith(("{%p if ", "{%p for ")):
            depth += 1
        elif text in ("{%p endif %}", "{%p endfor %}"):
            depth -= 1
        document.element.body.insert(-1, deepcopy(paragraph._p))
        if depth == 0:
            break
    else:
        pytest.fail("Unbalanced Answer template section")
    source = BytesIO()
    document.save(source)
    source.seek(0)
    template = DocxTemplate(source)
    context = {**context, "defined": lambda name: name in context}
    template.render(context, jinja_env=Environment(undefined=StrictUndefined, autoescape=True))
    output = BytesIO()
    template.save(output)
    output.seek(0)
    return "\n".join(p.text for p in Document(output).paragraphs)


class Violations(list):
    def any_true(self):
        return bool(self)

    def true_values(self):
        return self


@pytest.mark.parametrize("saved_state", [None, Violations(["STATE VIOLATION"])])
def test_small_condo_building_renders_only_local_claims(saved_state):
    context = {
        "is_condo_conversion": True,
        "more_than_3_units": False,
        "condo_local_violations": Violations(["LOCAL PERMIT", "BOSTON JUST CAUSE"]),
    }
    if saved_state is not None:
        context["condo_violations"] = saved_state
    text = render_answer_section("{%p if is_condo_conversion", context)
    assert "LOCAL PERMIT" in text
    assert "BOSTON JUST CAUSE" in text
    assert "STATE VIOLATION" not in text


def test_large_condo_building_retains_state_claims():
    text = render_answer_section("{%p if is_condo_conversion", {
        "is_condo_conversion": True,
        "more_than_3_units": True,
        "condo_violations": Violations(["STATE VIOLATION"]),
    })
    assert "STATE VIOLATION" in text


def test_no_condo_conversion_does_not_print_saved_local_claims():
    text = render_answer_section("{%p if is_condo_conversion", {
        "is_condo_conversion": False,
        "condo_local_violations": Violations(["STALE LOCAL VIOLATION"]),
    })
    assert "STALE LOCAL VIOLATION" not in text
    assert "converted into a condominium" not in text


@pytest.mark.parametrize("reason", ["nofault", "nontq", "unsure", "nonpayment", "fault"])
@pytest.mark.parametrize("saved_choice", [None, False, True])
def test_forfeiture_output_only_reads_choices_for_applicable_grounds(reason, saved_choice):
    defense = SimpleNamespace()
    if saved_choice is not None:
        defense.avoidance_of_forfeiture = saved_choice
    if reason in ("nonpayment", "fault") and saved_choice is None:
        # Applicable cases still require the user's explicit choice.
        with pytest.raises(UndefinedError):
            render_answer_section("initial_defense.avoidance_of_forfeiture", {
                "eviction_reason": reason, "initial_defense": defense,
            })
        return
    text = render_answer_section("initial_defense.avoidance_of_forfeiture", {
        "eviction_reason": reason, "initial_defense": defense,
    })
    assert ("equity and fairness" in text) is (
        reason in ("nonpayment", "fault") and saved_choice is True
    )


@pytest.mark.parametrize("expected_text", [
    "failure or delay of a government agency",
    "Continue this Case for Payment by Government Agency",
])
@pytest.mark.parametrize("reason", ["nofault", "nontq", "unsure", "fault", "nonpayment"])
@pytest.mark.parametrize("saved_raft", [None, False, True])
def test_raft_output_does_not_gather_hidden_nonpayment_answers(expected_text, reason, saved_raft):
    # Locate by the distinctive text in the block, so this test exercises both
    # production RAFT blocks before and after adding their grounds guards.
    paragraphs = Document(DATA / "templates/SummaryProcessAnswer.docx").paragraphs
    body = next(i for i, p in enumerate(paragraphs) if expected_text in p.text)
    if "Government Agency" in expected_text:
        body -= 1  # The relief block starts with an empty paragraph.
    opening = paragraphs[body - 1].text
    context = {"eviction_reason": reason}
    if saved_raft is not None:
        context["delay_in_raft"] = saved_raft
    if reason == "nonpayment" and saved_raft is None:
        with pytest.raises(UndefinedError):
            render_answer_section(opening, context, start=body - 1)
        return
    text = render_answer_section(opening, context, start=body - 1)
    assert (expected_text in text) is (reason == "nonpayment" and saved_raft is True)


@pytest.mark.parametrize("is_discriminated", [False, True])
def test_fresh_no_fault_answer_renders_without_nonpayment_or_fault_answers(is_discriminated):
    # Render the entire production Answer, not just its previously failing
    # blocks. No RAFT, cure, forfeiture, fault, condo or subsidy answers exist.
    defenses = SimpleNamespace(**dict.fromkeys([
        "no_proper_termination", "need_ntq", "no_ntq", "ntq_defective",
        "improper_time_given", "premature_commencement", "varney",
        "defective_summons", "new_tenancy", "no_standing",
        "inconsistent_reasons", "local_occupancy_ordinance",
    ], False), custom_reason_for_dismissal="TEST ONLY - no-fault defense",
        custom_other="TEST ONLY - other no-fault defense")
    context = {
        "eviction_reason": "nofault", "eviction_all_reasons": {"nofault": True},
        "tenant": SimpleNamespace(name="Taylor Example", is_discriminated=is_discriminated,
            is_disabled=False, is_nonnativespeaker=False, is_over60=False),
        "facts": SimpleNamespace(tenant_has_subsidy=False, tenant_has_lease=False,
            tenant_movein="January 1, 2020"),
        "initial_defense": defenses,
        "premises_address": "123 Fictional Test Street, Boston, MA 02114",
        "plead_counterclaims": True, "plead_8a": True, "plead_93a": False,
        "retaliation": SimpleNamespace(is_retaliated=False),
        "bad_conditions": SimpleNamespace(have_conditions=False),
        "bqe": SimpleNamespace(violated=False),
        "claims": SimpleNamespace(utilities=False, harassment=False),
        "postforeclosure": SimpleNamespace(is_foreclosed=False),
        "discrimination": SimpleNamespace(protected_classes=Violations(["Source of income"])),
        "is_condo_conversion": False, "has_city_specific_occupancy_ordinance": False,
        "paid_deposit": False, "paid_lmr": False, "claim_jurytrial": False,
        "needs_time_because": "TEST ONLY - time to move", "currency": str,
        "prepared_with_aoc": True,
    }
    def defined(name):
        try:
            eval(name, {}, context)
            return True
        except (NameError, AttributeError, KeyError):
            return False
    context["defined"] = defined
    context["showifdef"] = lambda name: eval(name, {}, context) if defined(name) else ""
    # Caption/signature subtemplates have their own tests; isolate the full
    # Answer's dependencies from the shared document-composition runtime.
    context["include_docx_template"] = lambda *args, **kwargs: ""
    template = DocxTemplate(DATA / "templates/SummaryProcessAnswer.docx")
    template.render(context, jinja_env=Environment(undefined=StrictUndefined, autoescape=True))
    output = BytesIO()
    template.save(output)
    output.seek(0)
    text = "\n".join(p.text for p in Document(output).paragraphs)
    assert "TEST ONLY - no-fault defense" in text
    assert "TEST ONLY - time to move" in text
    assert "failure or delay of a government agency" not in text
    assert "Continue this Case for Payment by Government Agency" not in text
    assert "equity and fairness" not in text
