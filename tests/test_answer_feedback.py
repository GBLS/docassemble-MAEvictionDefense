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
    # These are extracted DOCX paragraphs, not HTML; preserve literal text.
    return Environment(undefined=StrictUndefined, autoescape=False).from_string(  # nosec B701
        text.replace('{%p ', '{% ')
    ).render(**context)


@pytest.mark.parametrize('represented', [True, False])
@pytest.mark.parametrize('person,representation,performed_by', [
    ('tenant', None, 'tenant'),
    ('attorney', 'ghostwriting', 'tenant'),
    ('attorney', 'ghostwriting', 'advocate'),
    ('attorney', 'entering_appearance', 'tenant'),
    ('attorney', 'entering_appearance', 'advocate'),
])
@pytest.mark.parametrize('method,phrase', [
    ('emailed', 'email'), ('mailed', 'first-class mail'), ('delivered in-hand', 'hand delivery')
])
def test_certificate_matches_signer_recipient_and_method(represented, person, representation, performed_by, method, phrase):
    blocks = list(yaml.safe_load_all((DATA / 'questions/eviction.code.yml').read_text()))
    code = next(b['code'] for b in blocks if 'service_recipient_description =' in b.get('code', ''))
    context = {'landlord': SimpleNamespace(has_attorney=represented), 'service_recipient': 'landlord'}
    exec(code, context)
    assert context['service_recipient'] == ('attorney' if represented else 'landlord')
    context.update(person_answering=person, method_of_service=method,
                   service_performed_by=performed_by,
                   service_date=SimpleNamespace(format=lambda _: 'October 1, 2026'))
    method_code = next(b['code'] for b in blocks if 'service_method_phrase =' in b.get('code', ''))
    exec(method_code, context)
    if representation:
        context['representation_type'] = representation
    result = render('\n'.join(paragraphs('include_SignatureBlock.docx')[:5]), **context).strip()
    recipient = "the landlord's attorney" if represented else 'the landlord'
    if performed_by == 'advocate':
        expected = f'I hereby certify that I served a copy of this document by {phrase} to {recipient} on October 1, 2026.'
    else:
        expected = f'I hereby certify that I caused a copy of this document to be {method} to {recipient} on October 1, 2026.'
    assert result == expected


@pytest.mark.parametrize('person', ['tenant', 'advocate', 'attorney'])
@pytest.mark.parametrize('saved_delivery', [None, 'tenant', 'advocate'])
def test_service_delivery_resolves_without_asking_tenants_a_hidden_question(person, saved_delivery):
    blocks = list(yaml.safe_load_all((DATA / 'questions/eviction.code.yml').read_text()))
    rule = next(b for b in blocks if b.get('sets') == 'service_performed_by')
    screen_blocks = yaml.safe_load_all((DATA / 'questions/eviction.en.yml').read_text(encoding='utf-8'))
    screen = next(b for b in screen_blocks if b and b.get('id') == 'method of service')
    delivery = next(f for f in screen['fields'] if 'service_performed_by' in f.values())
    scope = {'person_answering': person}
    if saved_delivery is not None:
        scope['service_performed_by'] = saved_delivery
    visible = eval(delivery['show if']['code'], {}, scope)
    applicable = eval(rule['if'], {}, scope)
    assert applicable is not visible
    if applicable and saved_delivery is None:
        exec(rule['code'], scope)
    if saved_delivery is not None:
        assert scope['service_performed_by'] == saved_delivery
        return
    if visible:
        # Only the attorney's actual service-screen answer may set this value.
        assert scope.get('service_performed_by') == saved_delivery
        return

    # The live failure happened after intake was skipped, when the certificate
    # requested this hidden variable. Start without a mocked delivery answer.
    assert scope['service_performed_by'] == 'tenant'
    result = render('\n'.join(paragraphs('include_SignatureBlock.docx')[:5]),
                    **scope, method_of_service='emailed',
                    service_recipient_description='the landlord',
                    service_date=SimpleNamespace(format=lambda _: 'November 6, 2026'))
    assert 'I caused a copy of this document to be emailed to the landlord' in result


@pytest.mark.parametrize('selected', [True, False])
def test_forfeiture_is_a_separate_conditional_defense(selected):
    ps = paragraphs('SummaryProcessAnswer.docx')
    start = next(i for i, p in enumerate(ps) if p.startswith('{%p if ') and 'initial_defense.avoidance_of_forfeiture' in p)
    assert start > ps.index('The landlord’s case should be dismissed because {{ initial_defense.custom_reason_for_dismissal }}.')
    result = render('\n'.join(ps[start:start + 5]),
                    eviction_reason='nonpayment',
                    initial_defense=SimpleNamespace(avoidance_of_forfeiture=selected)).strip()
    assert result == ('Defense\nAvoidance of Forfeiture\nBased on principles of equity and fairness, it is unfair to evict me from my home.' if selected else '')
