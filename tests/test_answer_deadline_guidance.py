from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest
from docx import Document
from docxtpl import DocxTemplate
from jinja2 import Environment, StrictUndefined


ROOT = Path(__file__).resolve().parents[1]
QUESTION_DIR = ROOT / "docassemble" / "MAEvictionDefense" / "data" / "questions"
TEMPLATE_DIR = ROOT / "docassemble" / "MAEvictionDefense" / "data" / "templates"


class Court:
    address = SimpleNamespace(on_one_line=lambda: "123 Example Street")

    def __str__(self):
        return "Example Court"


def docx_text(template_name: str) -> str:
    # Word can split a Jinja expression across runs when a document is edited.
    return "\n".join(p.text for p in Document(str(TEMPLATE_DIR / template_name)).paragraphs)


def test_unknown_first_tier_event_does_not_create_an_answer_deadline():
    code = (QUESTION_DIR / "eviction.code.yml").read_text()

    assert "case.answer_date = None" in code
    assert "case.answer_deadline_known = False" in code
    assert "case.answer_date = next_court_business_day" not in code
    assert "case.entry_date = case.answer_date" not in code
    assert "case.entry_date >= date_received_summons.plus(days=7)" in code


def test_every_unknown_deadline_instruction_gives_rule_and_actionable_advice():
    questions = (QUESTION_DIR / "eviction.en.yml").read_text()
    next_steps = docx_text("NextSteps.docx")

    for guidance in (questions, next_steps):
        assert "3 court business days" in guidance
        assert "first-tier" in guidance
        assert "exact deadline" in guidance
        assert "contact the clerk" in guidance
        assert "Do not wait" in guidance or "do not wait" in guidance


@pytest.mark.parametrize("deadline_known", [False, True])
@pytest.mark.parametrize("event_assigned", [False, True])
def test_next_steps_conditions_known_and_unknown_event_dates(deadline_known, event_assigned):
    next_steps = docx_text("NextSteps.docx")

    assert "{% if case.answer_deadline_known %}" in next_steps
    assert "{% if case.hearing_date_assigned %}" in next_steps
    assert "{{ case.answer_date }}" in next_steps
    assert "Your first court-event date is not known yet" in next_steps

    case = SimpleNamespace(answer_deadline_known=deadline_known, hearing_date_assigned=event_assigned)
    if deadline_known:
        case.answer_date = "November 20, 2026"
    context = {
        "case": case,
        "court": Court(),
        "landlord": SimpleNamespace(has_attorney=False),
        "tenant": "Taylor Example",
        "today": lambda: "November 5, 2026",
        "court_is_housing_court": True,
        "court_date_is_holiday": False,
        "date_discovery_due": "November 30, 2026",
        "date_motion_to_compel_due": "December 7, 2026",
        "remind_user": False,
    }
    if event_assigned:
        context["court_date"] = "November 25, 2026"
    template = DocxTemplate(TEMPLATE_DIR / "NextSteps.docx")
    template.render(context, jinja_env=Environment(undefined=StrictUndefined, autoescape=True))
    output = BytesIO()
    template.save(output)
    output.seek(0)
    rendered = "\n".join(p.text for p in Document(output).paragraphs)
    assert ("November 20, 2026" in rendered) is deadline_known
    assert ("Your exact deadline is not known" in rendered) is (not deadline_known)
    assert ("November 25, 2026" in rendered) is event_assigned
    assert ("Your first court-event date is not known yet" in rendered) is (not event_assigned)


def test_answer_does_not_claim_unknown_cure_timing_as_fact():
    answer = docx_text("SummaryProcessAnswer.docx")

    assert "I ask the court to determine" in answer
    assert "within the time allowed by law" in answer


def test_next_steps_uses_the_motion_deadline_without_adding_another_period():
    paragraph = next(p.text for p in Document(TEMPLATE_DIR / "NextSteps.docx").paragraphs
        if "Deliver the Motion to Compel Discovery" in p.text)
    rendered = Environment(undefined=StrictUndefined, autoescape=True).from_string(paragraph).render(
        date_motion_to_compel_due="November 20, 2026")
    assert "no later than November 20, 2026" in rendered
    assert "within 5 days" not in rendered
