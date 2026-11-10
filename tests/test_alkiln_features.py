"""Catch ALKiln scenarios that parse but cannot supply concrete test answers."""

import csv
import json
import re
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
from gherkin.parser import Parser
from gherkin.pickles.compiler import Compiler
from mako.template import Template
from ruamel.yaml import YAML


SOURCES = Path(__file__).resolve().parents[1] / "docassemble/MAEvictionDefense/data/sources"


@pytest.mark.parametrize("path", sorted(SOURCES.glob("*.feature")), ids=lambda p: p.name)
def test_alkiln_scenarios_have_complete_examples(path):
    document = Parser().parse(path.read_text(encoding="utf-8"))
    document["uri"] = str(path)
    scenarios = [child["scenario"] for child in document["feature"]["children"] if "scenario" in child]
    expected_count = 0
    for scenario in scenarios:
        if scenario["keyword"] == "Scenario Outline":
            examples = scenario["examples"]
            assert examples and any(e["tableBody"] for e in examples), (
                f"{scenario['name']} needs an Examples table; ALKiln cannot answer literal placeholders."
            )
            expected_count += sum(len(e["tableBody"]) for e in examples)
        else:
            expected_count += 1

    compiled = Compiler().compile(document)
    assert len(compiled) == expected_count > 0
    for scenario in compiled:
        assert not re.search(r"<[A-Za-z_][A-Za-z_0-9]*>", json.dumps(scenario)), (
            f"Unresolved placeholder in {scenario['name']}"
        )


def test_attorney_story_tables_supply_all_required_visible_worksheet_answers():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required to evaluate the worksheet's visibility rules")
    path = SOURCES / "court_dates.feature"
    document = Parser().parse(path.read_text(encoding="utf-8"))
    document["uri"] = str(path)
    blocks = YAML(typ="safe").load_all(
        (SOURCES.parent / "questions/interview-attorney.yml").read_text(encoding="utf-8")
    )
    worksheet = next(b for b in blocks if b and b.get("id") == "attorney worksheet")
    with (SOURCES / "occupancy_ordinances.csv").open(encoding="utf-8", newline="") as source:
        occupancy_cities = {row["city"].strip().lower(): {} for row in csv.DictReader(source)}
    fixtures = []
    for scenario in Compiler().compile(document):
        if not any(tag["name"] == "@worksheet" for tag in scenario["tags"]):
            continue
        answers = {}
        for step in scenario["steps"]:
            rows = step.get("argument", {}).get("dataTable", {}).get("rows", [])
            for row in rows[1:]:
                name, value = [cell["value"] for cell in row["cells"][:2]]
                answers[name] = {"True": True, "False": False}.get(value, value)
        scope = {
            "json": json, "occupancy_ordinance_by_city": occupancy_cities,
            "macourts": [SimpleNamespace(instanceName=answers["court"], name="Boston Housing Court")],
        }
        fields = []
        for field in worksheet["fields"]:
            if field.get("datatype") == "yesno":
                name = field.get("field", next(iter(field.values())))
                # A single checkbox needs no table response when its initial
                # state already matches the scenario. Include that state when
                # evaluating conditional required fields.
                answers.setdefault(name, field.get("default", False))
            if "note" in field or field.get("required") is False:
                continue
            name = field.get("field", next(iter(field.values())))
            expression = Template(field.get("js show if", "true")).render(**scope)
            fields.append({"name": name, "expression": expression})
        fixtures.append({"scenario": scenario["name"], "answers": answers, "fields": fields})
    assert fixtures, "No worksheet scenarios were compiled"
    script = """
const fs = require('node:fs');
const fixtures = JSON.parse(fs.readFileSync(0, 'utf8'));
const results = fixtures.map(({scenario, answers, fields}) => {
  const val = name => answers[name];
  const missing = fields.filter(field => Boolean(eval(field.expression)))
    .map(field => field.name)
    .filter(name => !(name in answers) && !Object.keys(answers).some(key => key.startsWith(name + '[')));
  return {scenario, missing};
});
process.stdout.write(JSON.stringify(results));
"""
    result = subprocess.run([node, "-e", script], input=json.dumps(fixtures),
                            capture_output=True, text=True, check=True)
    for scenario in json.loads(result.stdout):
        assert not scenario["missing"], (
            f"{scenario['scenario']} is missing required visible worksheet answers: "
            + ", ".join(scenario["missing"])
        )


def test_nonpayment_story_tables_supply_a_date_when_rent_is_paid():
    path = SOURCES / "court_dates.feature"
    document = Parser().parse(path.read_text(encoding="utf-8"))
    document["uri"] = str(path)
    for scenario in Compiler().compile(document):
        answers = {}
        for step in scenario["steps"]:
            rows = step.get("argument", {}).get("dataTable", {}).get("rows", [])
            for row in rows[1:]:
                name, value = [cell["value"] for cell in row["cells"][:2]]
                answers[name] = value
        if answers.get("paid_rent_owed") == "True":
            assert answers.get("cure_date"), (
                f"{scenario['name']} says rent was paid but omits the required cure_date"
            )
