from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import pytest
import yaml
from jinja2 import Environment, StrictUndefined


DATA = Path(__file__).resolve().parents[1] / 'docassemble/MAEvictionDefense/data'


def paragraphs(name):
    with ZipFile(DATA / 'templates' / name) as archive:
        root = ET.fromstring(archive.read('word/document.xml'))
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    return [
        ''.join(t.text or '' for t in p.findall('.//w:t', ns))
        for p in root.findall('./w:body/w:p', ns)
    ]


def render(text, **context):
    return Environment(undefined=StrictUndefined).from_string(
        text.replace('{%p ', '{% ')
    ).render(**context)


@pytest.mark.parametrize('represented', [True, False])
@pytest.mark.parametrize('person,representation', [
    ('tenant', None), ('attorney', 'ghostwriting'), ('attorney', 'entering_appearance')
])
@pytest.mark.parametrize('method,phrase', [
    ('emailed', 'email'), ('mailed', 'first-class mail'), ('delivered in-hand', 'hand delivery')
])
def test_certificate_matches_signer_recipient_and_method(represented, person, representation, method, phrase):
    blocks = list(yaml.safe_load_all((DATA / 'questions/eviction.code.yml').read_text()))
    code = next(b['code'] for b in blocks if 'service_recipient_description =' in b.get('code', ''))
    context = {'landlord': SimpleNamespace(has_attorney=represented), 'service_recipient': 'landlord'}
    exec(code, context)
    assert context['service_recipient'] == ('attorney' if represented else 'landlord')
    context.update(person_answering=person, method_of_service=method,
                   service_method_phrase=phrase,
                   service_date=SimpleNamespace(format=lambda _: 'October 1, 2026'))
    if representation:
        context['representation_type'] = representation
    result = render('\n'.join(paragraphs('include_SignatureBlock.docx')[:5]), **context).strip()
    recipient = "the landlord's attorney" if represented else 'the landlord'
    if representation == 'entering_appearance':
        expected = f'I hereby certify that I served a copy of this document by {phrase} to {recipient} on October 1, 2026.'
    else:
        expected = f'I hereby certify that I caused a copy of this document to be {method} to {recipient} on October 1, 2026.'
    assert result == expected


@pytest.mark.parametrize('selected', [True, False])
def test_forfeiture_is_a_separate_conditional_defense(selected):
    ps = paragraphs('SummaryProcessAnswer.docx')
    start = ps.index('{%p if initial_defense.avoidance_of_forfeiture %}')
    assert start > ps.index('The landlord’s case should be dismissed because {{ initial_defense.custom_reason_for_dismissal }}.')
    result = render('\n'.join(ps[start:start + 5]),
                    initial_defense=SimpleNamespace(avoidance_of_forfeiture=selected)).strip()
    assert result == ('Defense\nAvoidance of Forfeiture\nBased on principles of equity and fairness, it is unfair to evict me from my home.' if selected else '')
