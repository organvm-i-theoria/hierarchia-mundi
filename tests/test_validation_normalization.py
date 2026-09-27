"""Near-match contradictions must fail closed without rewriting source evidence."""

import json

import pytest

from hierarchia.executor import ExecutableModule
from hierarchia.models.stratum import Module, ModuleType


@pytest.mark.parametrize("failed", ["limit respected ", "limit  respected", "LIMIT RESPECTED"])
def test_normalized_criteria_cannot_both_pass_and_fail(failed):
    raw = json.dumps({
        "is_valid": False, "criteria_met": ["limit respected"],
        "criteria_failed": [failed], "suggestions": [], "confidence": 0.8,
    })

    class Backend:
        def complete(self, prompt, system=""):
            return raw

    module = Module(
        id="test.normalization", name="Test", module_type=ModuleType.PROCESS,
        description="A content lens",
    )
    result = ExecutableModule(module).validate("content", Backend())
    assert result.is_valid is False
    assert result.confidence == 0.0
    assert result.criteria_failed == ["Invalid or contradictory structured validation response"]
    assert result.raw_output == raw
