"""Tests for the GBLS service-area rules."""
import sys
from types import ModuleType


import docassemble


# gbls_intake imports the docassemble server runtime, which is not installed in
# the lightweight CI test environment. Only the service-area rules are tested
# here, so the imported names just need to exist. Another test module may have
# already installed a partial stub, so add to it rather than replacing it.
def _module(name, parent=None, attr=None):
    module = sys.modules.get(name)
    if module is None:
        module = ModuleType(name)
        sys.modules[name] = module
    if parent is not None:
        setattr(parent, attr, module)
    return module


base_module = _module("docassemble.base", parent=docassemble, attr="base")
util_module = _module("docassemble.base.util", parent=base_module, attr="util")
config_module = _module("docassemble.base.config", parent=base_module, attr="config")

for _name, _value in {
    "Individual": object,
    "Address": object,
    "task_performed": lambda *a, **k: None,
    "task_not_yet_performed": lambda *a, **k: None,
    "mark_task_as_performed": lambda *a, **k: None,
    "log": lambda *a, **k: None,
}.items():
    if not hasattr(util_module, _name):
        setattr(util_module, _name, _value)

if not hasattr(config_module, "daconfig"):
    setattr(config_module, "daconfig", {})

from docassemble.MAEvictionDefense.gbls_intake import (  # noqa: E402
    GBLS_ELDER_ONLY_SERVICE_AREA,
    GBLS_SERVICE_AREA,
    city_in_service_area,
)


def test_boston_is_in_the_service_area_for_anyone():
    assert city_in_service_area("Boston") is True
    assert city_in_service_area("Boston", is_elder=True) is True


def test_acton_is_elder_only():
    """Regression test for #310: non-elders in Acton are outside the service area."""
    assert city_in_service_area("Acton") is False
    assert city_in_service_area("Acton", is_elder=True) is True


def test_city_matching_ignores_case_and_padding():
    assert city_in_service_area("  ACTON ", is_elder=True) is True
    assert city_in_service_area("  Cambridge ") is True


def test_town_outside_the_service_area_is_excluded_for_everyone():
    assert city_in_service_area("Springfield") is False
    assert city_in_service_area("Springfield", is_elder=True) is False


def test_missing_city_is_not_in_the_service_area():
    assert city_in_service_area(None) is False
    assert city_in_service_area("") is False


def test_elder_only_towns_are_not_also_in_the_general_area():
    assert not set(GBLS_ELDER_ONLY_SERVICE_AREA) & set(GBLS_SERVICE_AREA)
