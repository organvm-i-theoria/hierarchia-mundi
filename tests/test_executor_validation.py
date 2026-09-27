"""Regression tests for fail-closed content judgments; no external LLM calls."""

import json

import pytest

from hierarchia.executor import ExecutableModule
from hierarchia.models.stratum import Module, ModuleType


class Backend:
    def __init__(self, response):
        self.response = response
        self.system = ""

    def complete(self, prompt, system=""):
        self.system = system
        return self.response


@pytest.fixture
def executable():
    return ExecutableModule(Module(
        id="test.process", name="Test", module_type=ModuleType.PROCESS,
        description="A content lens", properties={"limit": 1},
    ))


def judgment(**overrides):
    return json.dumps({
        "is_valid": True, "criteria_met": ["limit respected"],
        "criteria_failed": [], "suggestions": [], "confidence": 0.8,
        **overrides,
    })


def test_positive_is_parsed_with_evidence(executable):
    backend = Backend(judgment())
    result = executable.validate("content", backend)
    assert result.is_valid is True
    assert result.criteria_met == ["limit respected"]
    assert result.confidence == 0.8
    assert result.raw_output == backend.response
    assert result.module_id == "test.process"
    assert "Return only a JSON object" in backend.system


def test_negative_is_not_converted_to_success(executable):
    raw = judgment(is_valid=False, criteria_met=[], criteria_failed=["limit exceeded"])
    result = executable.validate("bad content", Backend(raw))
    assert result.is_valid is False
    assert result.criteria_failed == ["limit exceeded"]
    assert result.raw_output == raw


@pytest.mark.parametrize("raw", [
    "", "Looks valid", "false", "true", "null", "[]", "{}",
    '{"is_valid": true}',
    judgment(is_valid="true"), judgment(is_valid=1),
    judgment(confidence="0.8"), judgment(confidence=True),
    judgment(confidence=-0.1), judgment(confidence=1.1),
    judgment(confidence=float("nan")), judgment(confidence=float("inf")),
    judgment(criteria_met=[]), judgment(criteria_met=[""]),
    judgment(criteria_met=["   "]), judgment(criteria_met=[42]),
    judgment(criteria_failed=["limit exceeded"]),
    judgment(is_valid=False, criteria_failed=[]),
    judgment(is_valid=False, criteria_failed=["limit respected"]),
    judgment(unexpected="extra"), judgment(suggestions="retry"),
    '{"is_valid":false,"is_valid":true,"criteria_met":["ok"],'
    '"criteria_failed":[],"suggestions":[],"confidence":1}',
    "```json\n" + judgment() + "\n```", judgment() + " trailing",
    "x" * 65_537, None, 1,
])
def test_untrusted_responses_fail_closed(executable, raw):
    result = executable.validate("content", Backend(raw))
    assert result.is_valid is False
    assert result.confidence == 0.0
    assert result.criteria_failed


def test_backend_failure_propagates(executable):
    class Broken:
        def complete(self, prompt, system=""):
            raise RuntimeError("backend unavailable")
    with pytest.raises(RuntimeError, match="backend unavailable"):
        executable.validate("content", Broken())


def test_property_modulation_still_preserves_original(executable):
    variant = executable.modulate({"limit": 2})
    assert variant.properties["limit"] == 2
    assert executable.module.properties["limit"] == 1
