from docassemble.MAEvictionDefense.demographics import (
    gender_list,
    age_list,
    ethnicity_list,
    education_list,
    relationship_list,
)


def test_gender_list_returns_list():
    result = gender_list()
    assert isinstance(result, list)
    assert len(result) > 0


def test_gender_list_has_expected_entries():
    result = gender_list()
    codes = [item[0] for item in result]
    assert "female" in codes
    assert "male" in codes


def test_age_list_returns_list():
    result = age_list()
    assert isinstance(result, list)
    assert len(result) > 0


def test_age_list_entries_have_two_elements():
    for item in age_list():
        assert len(item) == 2


def test_ethnicity_list_returns_list():
    result = ethnicity_list()
    assert isinstance(result, list)
    assert len(result) > 0


def test_education_list_returns_list():
    result = education_list()
    assert isinstance(result, list)
    assert len(result) > 0


def test_relationship_list_returns_dict():
    result = relationship_list()
    assert isinstance(result, dict)
    assert len(result) > 0


def test_relationship_list_has_expected_keys():
    result = relationship_list()
    assert "spouse" in result
    assert "parent" in result
    assert "child" in result
