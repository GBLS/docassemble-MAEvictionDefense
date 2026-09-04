from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
QUESTION_DIR = ROOT / "docassemble" / "MAEvictionDefense" / "data" / "questions"
TEMPLATE_DIR = ROOT / "docassemble" / "MAEvictionDefense" / "data" / "templates"


def docx_text(template_name: str) -> str:
    with ZipFile(TEMPLATE_DIR / template_name) as template:
        return template.read("word/document.xml").decode("utf-8")


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


def test_next_steps_conditions_known_and_unknown_event_dates():
    next_steps = docx_text("NextSteps.docx")

    assert "{% if case.answer_deadline_known %}" in next_steps
    assert "{% if case.hearing_date_assigned %}" in next_steps
    assert "{{ case.answer_date }}" in next_steps
    assert "Your first court-event date is not known yet" in next_steps


def test_answer_does_not_claim_unknown_cure_timing_as_fact():
    answer = docx_text("SummaryProcessAnswer.docx")

    assert "I ask the court to determine" in answer
    assert "within the time allowed by law" in answer
