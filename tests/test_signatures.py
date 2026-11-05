"""Render the shared signature template with signatures deliberately unavailable."""

from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest
from docx import Document
from docxtpl import DocxTemplate
from jinja2 import Environment, StrictUndefined


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "docassemble/MAEvictionDefense/data/templates/include_SignatureBlock.docx"


class Signer:
    def __init__(self, name, electronic):
        self.label = name
        self.electronic = electronic
        self.name = SimpleNamespace(full=lambda: name)
        self.address = SimpleNamespace(block=lambda: "123 Main Street")
        self.bbo = "123456"
        self.office = "Legal Services"
        self.email = "test@example.com"
        self.phone_number = "555-0100"
        self.fax_number = ""

    def __str__(self):
        return self.label

    def address_block(self):
        return f"{self.label}\n123 Main Street"

    @property
    def signature(self):
        if not self.electronic:
            raise AssertionError(f"Paper signing requested {self.label}'s electronic signature")
        return f"ELECTRONIC SIGNATURE: {self.label}"


class AdditionalTenants(list):
    def number(self):
        return len(self)


@pytest.mark.parametrize("person,representation", [
    ("tenant", None),
    ("attorney", "ghostwriting"),
    ("attorney", "entering_appearance"),
])
@pytest.mark.parametrize("choice", ["paper", "this device", "phone", None])
def test_signature_template_honors_paper_and_electronic_choices(person, representation, choice):
    electronic = choice != "paper"
    tenant = Signer("Tenant", electronic)
    attorney = Signer("Attorney", electronic)
    cotenant = Signer("Additional Tenant", electronic)
    context = {
        "person_answering": person,
        "representation_type": representation,
        "tenant": tenant,
        "tenants_attorney": attorney,
        "additional_tenants": AdditionalTenants([cotenant]),
        "service_performed_by": "advocate",
        "service_recipient_description": "the landlord",
        "service_method_phrase": "first-class mail",
        "service_date": SimpleNamespace(format=lambda _: "October 29, 2026"),
        "today": lambda: SimpleNamespace(format=lambda _: "10/29/2026"),
        "showifdef": lambda _: "",
    }
    if choice is not None:
        context["signature_choice"] = choice
    context["defined"] = lambda name: name in context

    template = DocxTemplate(TEMPLATE)
    template.render(context, jinja_env=Environment(undefined=StrictUndefined))
    output = BytesIO()
    template.save(output)
    output.seek(0)
    text = "\n".join(p.text for p in Document(output).paragraphs)

    if person == "attorney" and representation == "entering_appearance":
        expected_signers = [attorney]
        assert "BY THEIR ATTORNEY" in text
        assert "BBO # 123456" in text
        assert "Legal Services" in text
    else:
        expected_signers = [tenant, cotenant]
        assert "BY THEIR ATTORNEY" not in text
    for signer in expected_signers:
        assert str(signer) in text
    if electronic:
        for signer in expected_signers:
            assert f"ELECTRONIC SIGNATURE: {signer}" in text
        for signer in [tenant, attorney, cotenant]:
            if signer not in expected_signers:
                assert f"ELECTRONIC SIGNATURE: {signer}" not in text
    else:
        assert "ELECTRONIC SIGNATURE" not in text
        assert "__________________________" in text
