"""Exercise speech startup on configured and fresh docassemble servers."""

import ast
from pathlib import Path

import pytest
import yaml


QUESTIONS = Path(__file__).resolve().parents[1] / "docassemble/MAEvictionDefense/data/questions"


@pytest.mark.parametrize("capabilities,config,expected", [
    ({}, {}, False),
    ({"voicerss": False}, {}, False),
    ({"google_maps": True}, {}, False),
    ({"voicerss": True}, {}, True),
    ({"voicerss": True}, {"enable tts": True}, True),
    ({"voicerss": True}, {"enable tts": False}, False),
    ({"voicerss": True}, {"enable tts": None}, False),
    ({"voicerss": False}, {"enable tts": True}, False),
])
def test_interview_only_requests_speech_when_server_supports_it(capabilities, config, expected):
    blocks = yaml.safe_load_all((QUESTIONS / "eviction.yml").read_text(encoding="utf-8"))
    parent = next(b for b in blocks if b and b.get("id") == "parent_interview_flow")
    tree = ast.parse(parent["code"])
    # Execute the interview's actual speech assignment without starting the
    # rest of the interview or stubbing a database/audio upload into existence.
    assignments = [n for n in ast.walk(tree) if isinstance(n, ast.Assign) and any(
        isinstance(target, ast.Name) and target.id == "speak_text" for target in n.targets
    )]
    assert len(assignments) == 1
    scope = {
        "server_capabilities": lambda: capabilities,
        "get_config": lambda name, default=None: config.get(name, default),
    }
    exec(compile(ast.Module(body=assignments, type_ignores=[]), "speech-startup", "exec"), scope)
    assert scope["speak_text"] is expected
