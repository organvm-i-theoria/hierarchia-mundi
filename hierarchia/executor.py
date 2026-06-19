"""ExecutableModule — wraps a Module and adds analyze/generate/validate/modulate.

The LLM interface is stubbed out (accepts a callable protocol).
The modulate() method works without LLM — it returns a variant
of the module with adjusted properties.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from pydantic import BaseModel, Field

from hierarchia.models.stratum import Module


class LLMProtocol(Protocol):
    """Protocol for LLM backends. Accepts prompt + system, returns structured output."""

    def complete(self, prompt: str, system: str = "") -> str: ...


class AnalysisResult(BaseModel):
    """Result of analyzing text through a module's lens."""

    module_id: str
    module_name: str
    input_summary: str = ""
    findings: list[str] = Field(default_factory=list)
    cross_refs_activated: list[str] = Field(default_factory=list)
    score: float | None = None
    raw_output: str = ""


class GenerationResult(BaseModel):
    """Result of generating content using a module as template."""

    module_id: str
    module_name: str
    generated_content: str = ""
    structure: dict[str, Any] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)
    raw_output: str = ""


class ValidationResult(BaseModel):
    """Result of validating content against a module's rules."""

    module_id: str
    module_name: str
    is_valid: bool = False
    criteria_met: list[str] = Field(default_factory=list)
    criteria_failed: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    raw_output: str = ""


@dataclass
class ExecutableModule:
    """Wraps a Module and adds execution capabilities.

    Three LLM-powered modes:
        analyze  — examine input text through this module's lens
        generate — produce content using this module as template
        validate — check if content conforms to this module's rules

    One pure mode:
        modulate — return a variant with adjusted properties (no LLM needed)
    """

    module: Module
    stratum_id: str = ""
    stratum_name: str = ""

    @property
    def id(self) -> str:
        return self.module.id

    @property
    def name(self) -> str:
        return self.module.name

    def _build_system_prompt(self, mode: str) -> str:
        lines = [
            f"You are analyzing reality through the lens of: {self.module.name}",
            f"Module type: {self.module.module_type.value}",
            f"Stratum: {self.stratum_id} ({self.stratum_name})",
            f"Description: {self.module.description}",
        ]
        if self.module.properties:
            lines.append("Properties:")
            for k, v in self.module.properties.items():
                lines.append(f"  {k} = {v}")
        if self.module.cross_refs:
            lines.append(f"Cross-references: {', '.join(self.module.cross_refs)}")
        if self.module.probes:
            lines.append("Diagnostic probes:")
            for probe in self.module.probes:
                lines.append(f"  - {probe}")
        lines.append(f"\nMode: {mode}")
        return "\n".join(lines)

    def analyze(self, input_text: str, llm: LLMProtocol) -> AnalysisResult:
        """Analyze input text through this module's lens."""
        system = self._build_system_prompt("ANALYZE")
        prompt = (
            f"Analyze the following text through the lens of {self.module.name}.\n"
            f"Identify patterns, principles, and cross-references.\n\n"
            f"Text:\n{input_text}"
        )
        raw = llm.complete(prompt, system=system)
        return AnalysisResult(
            module_id=self.module.id,
            module_name=self.module.name,
            input_summary=input_text[:200],
            findings=[raw] if raw else [],
            raw_output=raw,
        )

    def generate(self, params: dict[str, Any], llm: LLMProtocol) -> GenerationResult:
        """Generate content using this module as template."""
        system = self._build_system_prompt("GENERATE")
        prompt = (
            f"Generate content in the style and structure of {self.module.name}.\n"
            f"Parameters: {params}\n"
            f"Use the module's properties and cross-references as guides."
        )
        raw = llm.complete(prompt, system=system)
        return GenerationResult(
            module_id=self.module.id,
            module_name=self.module.name,
            generated_content=raw,
            structure=params,
            raw_output=raw,
        )

    def validate(self, content: str, llm: LLMProtocol) -> ValidationResult:
        """Validate content against this module's rules."""
        system = self._build_system_prompt("VALIDATE")
        prompt = (
            f"Validate the following content against the rules and "
            f"properties of {self.module.name}.\n"
            f"Check each property and cross-reference.\n\n"
            f"Content:\n{content}"
        )
        raw = llm.complete(prompt, system=system)
        return ValidationResult(
            module_id=self.module.id,
            module_name=self.module.name,
            is_valid=True,  # LLM would determine this
            raw_output=raw,
        )

    def modulate(self, overrides: dict[str, Any]) -> Module:
        """Return a variant of this module with adjusted properties.

        Does not require LLM — pure data transformation.
        The original module is not modified.
        """
        new_props = {**self.module.properties, **overrides}
        return self.module.model_copy(update={"properties": new_props})
