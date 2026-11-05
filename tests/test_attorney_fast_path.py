"""Exercise the interview's actual YAML rules without a docassemble server."""

import ast
import csv
import json
import re
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
from mako.template import Template
from ruamel.yaml import YAML

from docassemble.MAEvictionDefense.attorney import (
    ATTORNEY_DERIVED_ANSWERS,
    checkbox_none_selected,
    discovery_checked_value,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docassemble/MAEvictionDefense/data"
QUESTIONS = DATA / "questions"


def blocks(filename):
    return [b for b in YAML(typ="safe").load_all((QUESTIONS / filename).read_text(encoding="utf-8")) if b]


def rule(filename, sets):
    return next(b["code"] for b in blocks(filename) if b.get("sets") == sets)


def field_name(field):
    if "note" in field:
        return None
    return next(iter(field.values()))


def field(variable):
    return next(
        f for b in blocks("interview-attorney.yml") for f in b.get("fields", [])
        if field_name(f) == variable
    )


def worksheet():
    return next(b for b in blocks("interview-attorney.yml") if b.get("id") == "attorney worksheet")


def lookup_scope(answers):
    """Resolve saved answers without seeking questions in the lightweight runner."""
    def defined(name):
        try:
            eval(name, {}, answers)
            return True
        except (NameError, AttributeError, KeyError):
            return False

    def showifdef(name, default=""):
        # Match the runtime's expression restriction so a permissive stub
        # cannot hide a crash caused by parentheses inside a dictionary key.
        if re.search(r"[\(\)\n\r]|lambda:|lambda ", name):
            raise ValueError(f"showifdef() is invalid: {name!r}")
        return eval(name, {}, answers) if defined(name) else default

    return {**answers, "defined": defined, "showifdef": showifdef}


def browser_expression(expression, answers):
    scope = {
        "occupancy_ordinance_by_city": {"boston": {}, "somerville": {}},
        "macourts": [SimpleNamespace(instanceName="housing", name="Boston Housing Court")],
        "json": json,
    }
    expression = Template(expression).render(**scope)
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required to test the worksheet's live visibility rules")
    script = "const fs = require('node:fs'); const input = JSON.parse(fs.readFileSync(0, 'utf8')); const val = name => input.answers[name]; process.stdout.write(JSON.stringify(Boolean(eval(input.expression))));"
    result = subprocess.run([node, "-e", script], input=json.dumps({"expression": expression, "answers": answers}), capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


@pytest.mark.parametrize("person,mode,target", [
    ("tenant", None, "guided_answer_variables"),
    ("attorney", "guided", "guided_answer_variables"),
    ("attorney", "fast", "attorney_answer_variables"),
])
def test_routing_preserves_tenant_and_optional_guided_path(person, mode, target):
    scope = {"person_answering": person, "nav": SimpleNamespace(set_section=lambda *_: None), target: True}
    if mode is not None:
        scope["attorney_workflow"] = mode
    exec(rule("interview-order.yml", "all_answer_variables"), scope)
    assert scope["all_answer_variables"] is True


@pytest.mark.parametrize("grounds,expected", [
    ({"fault": True}, False),
    ({"fault": True, "nonpayment": True}, True),
    ({"nonpayment": True}, True),
    ({"nofault": True}, True),
    ({"nontq": True}, True),
    ({"unsure": True}, True),
])
def test_fast_counterclaim_controls_follow_shared_guided_rules(grounds, expected):
    scope = {
        "eviction_all_reasons": dict.fromkeys(["fault", "nonpayment", "nofault", "nontq", "unsure"], False) | grounds,
        "initial_defense": SimpleNamespace(), "fault_basis": [], "nofault_basis": [], "need": lambda *_: None,
    }
    exec(rule("eviction.code.yml", "eviction_reason"), scope)
    shared_rule = next(b["code"] for b in blocks("eviction.code.yml") if "set_plead_counterclaims = True" in b.get("code", ""))
    exec(shared_rule, scope)
    assert scope["plead_counterclaims"] is expected
    # Live visibility must agree with the backend's policy before submission.
    answers = {f"eviction_all_reasons['{key}']": selected for key, selected in scope["eviction_all_reasons"].items()}
    for variable in ("paid_deposit", "paid_lmr", "bad_conditions.conditions", "bqe.heat"):
        assert browser_expression(field(variable)["js show if"], answers) is expected


def test_no_notice_does_not_require_answers_about_nonexistent_notice_text():
    scope = {
        "notice_type": "no_ntq", "is_pca": False,
        "facts": SimpleNamespace(tenant_has_subsidy=True),
        "tenancy_type": "taw", "initial_defense": SimpleNamespace(no_ntq=True),
    }
    shared_rule = next(b["code"] for b in blocks("eviction.code.yml") if b.get("sets") == ["initial_defense.no_proper_termination", "initial_defense.need_ntq"])
    exec(shared_rule, scope)
    exec(rule("eviction.code.yml", "initial_defense.new_tenancy"), scope)
    assert scope["initial_defense"].need_ntq is True
    assert scope["initial_defense"].no_proper_termination is True
    assert scope["initial_defense"].new_tenancy is False


@pytest.mark.parametrize("mode,expected", [("fast", False), ("guided", True)])
def test_explicit_fast_path_pleading_choices_survive_shared_calculations(mode, expected):
    tree = ast.parse(rule("interview-order.yml", "common_answer_variables"))
    # Execute the actual default-setting branches with facts that support both
    # recommendations and an attorney who explicitly declined both pleadings.
    branches = [node for node in tree.body if isinstance(node, ast.If) and any(
        isinstance(n, ast.Assign) and any(
            isinstance(t, ast.Attribute) and t.attr in ("is_retaliated", "is_discriminated")
            for t in n.targets
        ) for n in ast.walk(node)
    )]
    scope = {
        "person_answering": "attorney", "attorney_workflow": mode,
        "plead_counterclaims": True, "bad_conditions": SimpleNamespace(have_conditions=True),
        "tenant": SimpleNamespace(is_dvvictim=True, is_disabled=True, is_discriminated=False),
        "claims": SimpleNamespace(harassment=True),
        "retaliation": SimpleNamespace(is_retaliated=False),
    }
    exec(compile(ast.Module(body=branches, type_ignores=[]), "shared-defaults", "exec"), scope)
    assert scope["retaliation"].is_retaliated is expected
    assert scope["tenant"].is_discriminated is expected


def test_refresh_clears_calculations_without_deleting_facts_or_explicit_choices():
    input_fields = {field_name(f) for b in blocks("interview-attorney.yml") for f in b.get("fields", [])}
    assert not input_fields.intersection(ATTORNEY_DERIVED_ANSWERS)
    assert {"initial_defense.cure", "initial_defense.new_tenancy", "eviction_reason", "loaded_discovery", "downloads"}.issubset(ATTORNEY_DERIVED_ANSWERS)
    for b in blocks("interview-attorney.yml"):
        if b.get("fields") and b.get("id") != "attorney workflow choice":
            invalidated = []
            scope = {
                "ATTORNEY_DERIVED_ANSWERS": ATTORNEY_DERIVED_ANSWERS,
                "showifdef": lambda *args: False, "court": SimpleNamespace(name="Boston Housing Court"),
                "bad_conditions": SimpleNamespace(), "retaliation": SimpleNamespace(is_retaliated=False),
                "tenant": SimpleNamespace(is_discriminated=False, is_nonnativespeaker=False, address=SimpleNamespace(city="Boston")), "discrimination": SimpleNamespace(),
                "facts": SimpleNamespace(tenant_has_subsidy=False, tenant_address_is_eviction_address=True),
                "occupancy_ordinance_by_city": {"boston": {}},
                "defined": lambda *_: False, "nav": SimpleNamespace(unhide=lambda: None),
            }
            # This standalone attachment is outside the regenerated main bundle.
            scope["compel_discovery_with_instructions"] = {"plaintiff": "Old landlord", "signer": "Old tenant"}
            def undefine(*args):
                invalidated.extend(args)
                for name in args:
                    scope.pop(name, None)
            scope["undefine"] = undefine
            exec(b["validation code"], scope)
            assert set(ATTORNEY_DERIVED_ANSWERS).issubset(invalidated)
            assert "compel_discovery_with_instructions" not in scope


def test_dynamic_visibility_only_references_fields_on_the_same_screen():
    # A cross-screen val() silently hides a field in docassemble. Prerequisites
    # must use a server condition or a rendered constant instead.
    for block in blocks("interview-attorney.yml"):
        names = {field_name(f) for f in block.get("fields", [])}
        for item in block.get("fields", []):
            for reference in re.findall(r'val\("([^"\n]+)"\)', item.get("js show if", "")):
                assert reference in names or reference.split("[")[0] in names


def test_inline_review_responds_to_unsaved_facts_without_changing_choices():
    recommendation = next(f for f in worksheet()["fields"] if "suggest reviewing a discrimination" in f.get("note", ""))
    answers = {"tenant.is_disabled": True, "tenant.is_discriminated": False}
    assert browser_expression(recommendation["js show if"], answers) is True
    answers["tenant.is_disabled"] = False
    assert browser_expression(recommendation["js show if"], answers) is False
    assert answers["tenant.is_discriminated"] is False


def test_one_worksheet_uses_in_page_links_and_follows_the_tenant_order():
    forms = [b for b in blocks("interview-attorney.yml") if b.get("fields") and b.get("id") != "attorney workflow choice"]
    assert len(forms) == 1
    form = forms[0]
    assert form["continue button field"] == "attorney_intake_complete"
    assert "url_action" not in form["subquestion"]
    targets = re.findall(r'href="#(made-attorney-[^"]+)"', form["subquestion"])
    for target in targets:
        assert any(f'id="{target}"' in f.get("note", "") for f in form["fields"])
    variables = [field_name(f) for f in form["fields"]]
    ordered = ["tenant.name.first", "landlord.name.text", "court", "facts.tenant_movein", "notice_type", "bad_conditions.conditions", "retaliation.is_retaliated", "tenant.is_discriminated", "fault.did_not_occur", "security_deposit.amount", "postforeclosure.no_standing", "claim_jurytrial"]
    assert [variables.index(v) for v in ordered] == sorted(variables.index(v) for v in ordered)
    flow = rule("interview-attorney.yml", "attorney_answer_variables")
    assert "attorney_intake_complete" in flow
    assert "attorney_review_complete" not in flow
    assert "attorney_parties_complete" not in flow


def test_first_render_never_seeks_unsaved_on_screen_answers():
    scope = {
        **lookup_scope({}),
        "occupancy_ordinance_by_city": {"boston": {}, "somerville": {}},
        "macourts": [SimpleNamespace(instanceName="housing", name="Boston Housing Court")],
        "json": json, "url_of": lambda filename: filename, "default_lang": "",
        "checkbox_none_selected": checkbox_none_selected,
    }
    def check(value):
        if isinstance(value, dict):
            for item in value.values():
                check(item)
        elif isinstance(value, list):
            for item in value:
                check(item)
        elif isinstance(value, str) and "${" in value:
            Template(value).render(**scope)
    check(worksheet())
    assert not any(isinstance(f.get("show if"), dict) for f in worksheet()["fields"])


@pytest.mark.parametrize("variable,key", [
    ("attorney_boston_condo_notice", "My landlord failed to provide me with 5 years' notice and someone with a disability or an elder is part of my household."),
    ("attorney_boston_condo_just_cause", "My landlord did not give me 'just cause' for my eviction (they gave no reason or a bad reason)."),
])
@pytest.mark.parametrize("saved,expected", [
    ("undefined", False),
    ("missing", False),
    (False, False),
    (True, True),
])
def test_boston_condo_defaults_preserve_saved_answers_without_seeking_questions(variable, key, saved, expected):
    answers = {}
    if saved != "undefined":
        answers["condo_local_violations"] = {} if saved == "missing" else {key: saved}
    rendered = Template(field(variable)["default"]).render(**lookup_scope(answers))
    assert rendered.strip() == str(expected)


@pytest.mark.parametrize("saved,expected", [
    (None, False),
    ({}, True),
    ({"insects": False, "other": False}, True),
    ({"insects": True, "other": False}, False),
])
def test_saved_none_is_distinct_from_an_unanswered_checkbox_group(saved, expected):
    assert checkbox_none_selected(saved) is expected
    if saved is not None:
        class UngatheredCheckboxes:
            elements = saved

            def _trigger_gather(self):
                pytest.fail("Reading saved checkbox answers must not gather questions")

        assert checkbox_none_selected(UngatheredCheckboxes()) is expected


def test_every_worksheet_checkbox_group_restores_only_saved_empty_answers():
    for item in worksheet()["fields"]:
        if item.get("datatype") != "checkboxes" or item.get("none of the above") is False:
            continue
        name = field_name(item)
        key = next(iter(item["choices"][0].values()))
        for saved, expected in [(None, ""), ({key: False}, "made-attorney-saved-none"), ({key: True}, "")]:
            answers = {}
            if saved is not None:
                parts = name.split(".")
                if len(parts) == 1:
                    answers[name] = saved
                else:
                    answers[parts[0]] = SimpleNamespace(**{parts[1]: saved})
            scope = {**lookup_scope(answers), "checkbox_none_selected": checkbox_none_selected}
            assert Template(item["css class"]).render(**scope).strip() == expected


def test_boston_standalone_answers_do_not_select_hidden_local_checkbox_choices():
    item = field("condo_local_violations")
    answers = {"condo_local_violations": {
        "My landlord did not give me 'just cause' for my eviction (they gave no reason or a bad reason).": True,
    }}
    scope = {**lookup_scope(answers), "checkbox_none_selected": checkbox_none_selected}
    assert Template(item["css class"]).render(**scope).strip() == "made-attorney-saved-none"


def test_guided_retaliation_facts_are_not_inferred_from_bad_conditions():
    question = next(b for b in blocks("eviction.en.yml") if b.get("id") == "retaliation")
    factual_names = {"retaliation.withheld_rent", "retaliation.badconditions_to_landlord", "retaliation.badconditions_to_agency"}
    facts = [f for f in question["fields"] if field_name(f) in factual_names]
    assert len(facts) == 3
    assert all("default" not in f for f in facts)


def test_six_month_retaliation_fact_requires_an_explicit_answer_in_both_workflows():
    guided = next(b for b in blocks("eviction.en.yml") if b.get("id") == "retaliation")
    guided_field = next(f for f in guided["fields"] if field_name(f) == "retaliation.within_6_months")
    for item in (guided_field, field("retaliation.within_6_months")):
        assert item["datatype"] == "yesnoradio"
        assert item["required"] is True
        assert "default" not in item


@pytest.mark.parametrize("person,representation,clinic,in_area,expected", [
    ("attorney", "entering_appearance", "", True, []),
    ("attorney", "entering_appearance", "", False, []),
    ("attorney", "ghostwriting", "", True, ["ask_intake_questions"]),
    ("tenant", None, "", True, ["ask_intake_questions"]),
    ("advocate", None, "", True, ["ask_intake_questions"]),
    ("tenant", None, "", False, ["out_of_service_area"]),
    ("attorney", "ghostwriting", "gbls", True, ["out_of_service_area"]),
])
def test_intake_invitation_respects_representation(person, representation, clinic, in_area, expected):
    parent = next(b for b in blocks("eviction.yml") if b.get("id") == "parent_interview_flow")
    tree = ast.parse(parent["code"])
    branch = next(n for n in tree.body if isinstance(n, ast.If) and any(
        isinstance(child, ast.Name) and child.id == "ask_intake_questions" for child in ast.walk(n)
    ))
    visits = []

    class VisitQuestions(ast.NodeTransformer):
        def visit_Expr(self, node):
            if isinstance(node.value, ast.Name):
                return ast.copy_location(ast.Expr(value=ast.Call(
                    func=ast.Name(id="record", ctx=ast.Load()), args=[ast.Constant(node.value.id)], keywords=[]
                )), node)
            return node

    branch = ast.fix_missing_locations(VisitQuestions().visit(branch))
    scope = {
        "person_answering": person, "tenant": SimpleNamespace(is_over60=False),
        "url_args": {"clinic": clinic}, "in_service_area": lambda *a, **k: in_area,
        "ask_intake_questions": "skip", "record": visits.append,
    }
    if representation is not None:
        scope["representation_type"] = representation
    exec(compile(ast.Module(body=[branch], type_ignores=[]), "intake-routing", "exec"), scope)
    assert visits == expected


def test_error_feedback_link_does_not_depend_on_interview_template_evaluation():
    from urllib.parse import parse_qs, urlparse

    metadata = next(b["metadata"] for b in blocks("eviction.yml") if "metadata" in b)
    error_help = metadata["error help"]
    assert "${" not in error_help
    url = re.search(r"\[Please tell us more about the bug\]\(([^)]+)\)", error_help).group(1)
    params = parse_qs(urlparse(url).query)
    assert params["i"] == ["docassemble.MAEvictionDefense:feedback.yml"]
    assert params["reset"] == ["1"]
    assert (QUESTIONS / "feedback.yml").exists()


@pytest.mark.parametrize("variable,answers,before,changed,after", [
    ("subsidized_housing.pha_pays_rent", {"facts.tenant_has_subsidy": False, "subsidy_type": "MRVP"}, False, {"facts.tenant_has_subsidy": True}, True),
    ("date_received_ntq", {"notice_type": "no_ntq"}, False, {"notice_type": "fourteen_day"}, True),
    ("occupancy_ordinance_applies", {"facts.tenant_address_is_eviction_address": True, "tenant.address.city": "Boston", "premises_alternate_address.city": "Newton"}, True, {"facts.tenant_address_is_eviction_address": False}, False),
    ("attorney_boston_condo_notice", {"facts.tenant_address_is_eviction_address": True, "tenant.address.city": "Boston", "is_condo_conversion": True}, True, {"tenant.address.city": "Somerville"}, False),
    ("tenant.preferred_language", {"tenant.is_nonnativespeaker": True, "tenant.needs_interpreter": True}, True, {"tenant.is_nonnativespeaker": False}, False),
])
def test_visibility_updates_on_the_same_screen(variable, answers, before, changed, after):
    expression = field(variable)["js show if"]
    assert browser_expression(expression, answers) is before
    answers.update(changed)
    assert browser_expression(expression, answers) is after


class Requests:
    def __init__(self):
        self.elements = {}

    def initializeObject(self, key, _type):
        self.elements[key] = SimpleNamespace()

    def __getitem__(self, key):
        return self.elements[key]

    def matches_category(self, category):
        return [key for key, item in self.elements.items() if item.category == category]


def test_refreshing_real_discovery_rules_preserves_reviewed_choices_and_custom_requests():
    def load_csv(relative):
        with (DATA / relative.removeprefix("data/")).open(encoding="utf-8-sig", newline="") as source:
            return list(csv.DictReader(source))

    scope = {
        "ints": Requests(), "drq": Requests(), "DiscoveryRequest": object,
        "other_ints": SimpleNamespace(), "other_drq": SimpleNamespace(),
        "load_from_csv": load_csv, "discovery_checked_value": discovery_checked_value,
        "person_answering": "attorney", "attorney_workflow": "fast", "word": lambda s: s,
        "bad_conditions": SimpleNamespace(have_conditions=True),
    }

    def defined(name):
        try:
            eval(name, scope)
            return True
        except (NameError, AttributeError, KeyError):
            return False

    scope.update(defined=defined, value=lambda name: eval(name, scope))
    code = next(b["code"] for b in blocks("discovery-logic.yml") if b.get("need") == "all_answer_variables")
    exec(code, scope)
    selected = next(key for key, item in scope["ints"].elements.items() if item.recommended)
    optional = next(key for key, item in scope["ints"].elements.items() if not item.recommended)
    scope["ints"][selected].checked = False
    scope["ints"][optional].checked = True
    scope["interrogatory_questions"] = True
    scope["other_ints"].there_are_any = True
    scope["bad_conditions"].have_conditions = False
    exec(code, scope)
    assert scope["ints"][selected].checked is False
    assert scope["ints"][optional].checked is True
    assert scope["other_ints"].there_are_any is True
    # Document requests have not been reviewed, so those defaults track facts.
    assert scope["drq"]["bad_conditions_photos"].recommended is False
    assert scope["drq"]["bad_conditions_photos"].checked is False
    assert any("Recommended" in f.get("help", "") for f in scope["ints_fields"])
