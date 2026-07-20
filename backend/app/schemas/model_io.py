"""Pydantic schemas for model output at the two P3 model boundaries.

These validate the raw JSON returned by the model for P-01 (segment and
classify) and P-02 (normalize attributes) per PROMPT_SPEC.md. Validation
failure here triggers the one-repair-then-fail flow in the model adapter —
see `app/model_adapter/errors.py`.
"""

from typing import Any

from pydantic import BaseModel, Field


class ClassifiedClauseModel(BaseModel):
    clause_id: str
    clause_type: str
    title: str
    section_reference: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    extracted_text: str
    classification_confidence: float = Field(ge=0.0, le=1.0)


class ClassifyResponse(BaseModel):
    clauses: list[ClassifiedClauseModel]


class AttributeValueModel(BaseModel):
    attribute: str
    value: Any
    evidence_spans: list[str] = []


class ExtractResponse(BaseModel):
    values: list[AttributeValueModel]
