import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    document_name: Mapped[str] = mapped_column(String(255))
    document_sha256: Mapped[str] = mapped_column(String(64))
    document_page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    document_language: Mapped[str] = mapped_column(String(16), default="unknown")

    status: Mapped[str] = mapped_column(String(16), default="queued")
    current_stage: Mapped[str | None] = mapped_column(String(32), nullable=True, default="queued")
    overall_risk: Mapped[str | None] = mapped_column(String(16), nullable=True)

    playbook_id: Mapped[str] = mapped_column(String(64), default="defense-services-v1")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_retryable: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    pipeline_version: Mapped[str] = mapped_column(String(16), default="1.0-draft")
    playbook_version: Mapped[str] = mapped_column(String(16), default="1.0-draft")
    prompt_version: Mapped[str] = mapped_column(String(16), default="1.0-draft")

    model_provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    model_revision: Mapped[str | None] = mapped_column(String(64), nullable=True)

    deployment_mode: Mapped[str] = mapped_column(String(16), default="local")
    retrieval_mode: Mapped[str] = mapped_column(String(32), default="degraded_full_rules")

    # Internal parsing state (P1). upload_temp_path is never serialized to the
    # API; it is the server-side path the job runner reads to parse, deleted
    # once parsing finishes (success or failure).
    upload_temp_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    parsed_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parser_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    parser_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    parse_error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)

    clauses: Mapped[list["Clause"]] = relationship(back_populates="review", cascade="all, delete-orphan")
    findings: Mapped[list["Finding"]] = relationship(back_populates="review", cascade="all, delete-orphan")


class Clause(Base):
    __tablename__ = "clauses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    review_id: Mapped[str] = mapped_column(String(36), ForeignKey("reviews.id"))
    clause_type: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(255))
    section_reference: Mapped[str | None] = mapped_column(String(64), nullable=True)
    page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extracted_text: Mapped[str] = mapped_column(Text)
    classification_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    review: Mapped[Review] = relationship(back_populates="clauses")


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    review_id: Mapped[str] = mapped_column(String(36), ForeignKey("reviews.id"))
    clause_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("clauses.id"), nullable=True)

    finding_type: Mapped[str] = mapped_column(String(32))
    clause_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    section_reference: Mapped[str | None] = mapped_column(String(64), nullable=True)
    page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    evidence_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    classification_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_label: Mapped[str] = mapped_column(String(16))
    rule_id: Mapped[str] = mapped_column(String(32))
    deviation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str] = mapped_column(String(32))

    # P4: supplemental guidance retrieved after rule evaluation, stored as a
    # JSON-encoded list (see app.services.guidance_retrieval.GuidanceResult).
    # "[]" (not null) so pre-P4 rows and degraded-retrieval rows are
    # indistinguishable from "no guidance found" at the API layer — this
    # field never carries risk information and is never read by rule_engine.py.
    guidance_json: Mapped[str] = mapped_column(Text, default="[]")

    review: Mapped[Review] = relationship(back_populates="findings")
