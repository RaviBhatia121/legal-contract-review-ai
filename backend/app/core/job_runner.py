import asyncio
import dataclasses
import json
import logging
import os
from typing import Callable

from haystack.core.errors import PipelineRuntimeError
from sqlalchemy import select

from app.api import errors
from app.core.config import Settings, get_settings
from app.db.models import Clause, Finding, Review
from app.db.repository import ReviewRepository
from app.db.session import async_session_factory
from app.model_adapter.errors import ModelOutputInvalidError, ModelTimeoutError, ProviderUnavailableError
from app.playbook.loader import Playbook, load_playbook
from app.services import applicability
from app.services.clause_intelligence import (
    DETERMINISTIC_MODE,
    DETERMINISTIC_SOURCE,
    MODEL_ASSISTED_SOURCE,
    MODEL_MODE,
    ClauseIntelligenceService,
)
from app.services.guidance_retrieval import DEGRADED_MODE, GuidanceService
from app.services.parsing import (
    PARSER_NAME,
    PARSER_VERSION,
    DocumentParseFailedError,
    DocumentTooLongError,
    EncryptedDocumentError,
    ParsingError,
    parse_document,
)
from app.services.rule_engine import ClauseRecord, FindingRecord, evaluate_clauses
from app.services.upload import delete_temp_upload

logger = logging.getLogger(__name__)

_ACTIVE_STATUSES = ("queued", "parsing", "analyzing", "validating")

# Bounded PoC job runner (D-12 baseline): a single backend process, limited
# in-process concurrency, no durable queue or multi-instance guarantees.
_MAX_CONCURRENT_JOBS = 2
_job_semaphore = asyncio.Semaphore(_MAX_CONCURRENT_JOBS)

# Stages after classification (see run_review_job: classifying_clauses runs
# separately, before the post-classification applicability check). Mirrors
# the allowed current_stage values in OUTPUT_SCHEMA.md.
_POST_CLASSIFY_STAGE_SEQUENCE: list[tuple[str, str, float]] = [
    ("analyzing", "checking_playbook", 0.1),
    ("analyzing", "extracting_attributes", 0.15),
    ("analyzing", "evaluating_rules", 0.15),
    ("validating", "validating_result", 0.1),
]

_PARSE_ERROR_MAP: dict[type[ParsingError], tuple[str, bool]] = {
    EncryptedDocumentError: ("ENCRYPTED_DOCUMENT", False),
    DocumentTooLongError: ("DOCUMENT_TOO_LONG", False),
    DocumentParseFailedError: ("DOCUMENT_PARSE_FAILED", True),
}

# Deterministic mode has no model call of any kind (rule engine only); these
# provenance values say so honestly rather than implying a model ran.
_RULE_ENGINE_PROVIDER = "rule-engine"
_RULE_ENGINE_MODEL = "none"
_RULE_ENGINE_MODEL_REVISION = None

_MODEL_ADAPTER_ERROR_MAP: dict[type[Exception], Callable[[], errors.ApiError]] = {
    ModelTimeoutError: errors.model_timeout,
    ModelOutputInvalidError: errors.model_output_invalid,
    ProviderUnavailableError: errors.provider_unavailable,
}
_MODEL_EXECUTION_ERRORS = (*_MODEL_ADAPTER_ERROR_MAP.keys(), PipelineRuntimeError)


async def run_review_job(review_id: str) -> None:
    async with _job_semaphore:
        async with async_session_factory() as session:
            repo = ReviewRepository(session)
            review = await repo.get(review_id)
            if review is None:
                logger.warning("job_runner: review %s not found", review_id)
                return

            try:
                review = await repo.update_status(review, status="parsing", current_stage="parsing_document")

                path = review.upload_temp_path
                extension = os.path.splitext(path)[1] if path else ""
                try:
                    parsed = parse_document(path, extension)
                except tuple(_PARSE_ERROR_MAP) as exc:
                    code, retryable = _PARSE_ERROR_MAP[type(exc)]
                    await repo.mark_failed(
                        review, code=code, message=str(exc), retryable=retryable, parse_error_code=code
                    )
                    return
                finally:
                    delete_temp_upload(path)

                review = await repo.set_parsed_document(
                    review,
                    parsed_text=parsed.text,
                    document_page_count=parsed.page_count,
                    document_language=parsed.language,
                    parser_name=PARSER_NAME,
                    parser_version=PARSER_VERSION,
                )

                review = await repo.update_status(
                    review, status="analyzing", current_stage="checking_applicability"
                )
                await asyncio.sleep(0.1)

                if not applicability.has_reviewable_text(parsed.text):
                    await repo.mark_failed(review, **_error_kwargs(errors.no_reviewable_text()))
                    return

                playbook = load_playbook(review.playbook_id)
                settings = get_settings()
                intelligence = ClauseIntelligenceService(settings)

                review = await repo.update_status(
                    review, status="analyzing", current_stage="classifying_clauses"
                )
                mode_requested = settings.clause_intelligence_mode
                fallback_used = False
                fallback_reason = None
                try:
                    clause_inputs, mode_used = await intelligence.get_clause_inputs(parsed, playbook)
                except _MODEL_EXECUTION_ERRORS as exc:
                    if mode_requested != MODEL_MODE:
                        error_builder = _MODEL_ADAPTER_ERROR_MAP.get(type(exc), errors.provider_unavailable)
                        await repo.mark_failed(review, **_error_kwargs(error_builder()))
                        return
                    fallback_used = True
                    fallback_reason = type(exc).__name__
                    logger.warning(
                        "job_runner: review %s model path unavailable (%s); using deterministic fallback",
                        review_id,
                        fallback_reason,
                    )
                    clause_inputs = _deterministic_fallback_inputs(parsed)
                    mode_used = DETERMINISTIC_MODE

                # Real applicability check, using classification output —
                # source-agnostic, so it runs the same way whether
                # `clause_inputs` came from the deterministic or model path.
                if not applicability.is_applicable(clause_inputs, playbook):
                    await repo.mark_failed(review, **_error_kwargs(errors.document_not_applicable()))
                    return

                for status, stage, delay in _POST_CLASSIFY_STAGE_SEQUENCE:
                    review = await repo.update_status(review, status=status, current_stage=stage)
                    await asyncio.sleep(delay)

                source = MODEL_ASSISTED_SOURCE if mode_used == "model" else DETERMINISTIC_SOURCE
                clause_records, finding_records, overall_risk = evaluate_clauses(clause_inputs, playbook, source=source)
                clause_rows, finding_rows = _to_orm_rows(clause_records, finding_records)

                # P4: guidance retrieval is pure post-processing enrichment —
                # findings, rule_ids, severities, and overall_risk above are
                # already final. This can only add a `guidance` list to each
                # Finding row; it cannot change any of them.
                retrieval_mode = await _attach_guidance(finding_rows, finding_records, playbook, settings)

                if mode_used == "model":
                    model_provider, model_name = settings.provider_type, settings.model_name
                else:
                    model_provider, model_name = _RULE_ENGINE_PROVIDER, _RULE_ENGINE_MODEL

                await repo.mark_completed(
                    review,
                    overall_risk=overall_risk,
                    clauses=clause_rows,
                    findings=finding_rows,
                    document_page_count=parsed.page_count,
                    document_language=parsed.language,
                    model_provider=model_provider,
                    model_name=model_name,
                    model_revision=_RULE_ENGINE_MODEL_REVISION,
                    mode_requested=mode_requested,
                    mode_used=mode_used,
                    fallback_used=fallback_used,
                    fallback_reason=fallback_reason,
                    retrieval_mode=retrieval_mode,
                )
            except Exception as exc:
                # P6: log the exception type and review_id only — never the
                # message or traceback. A ValidationError from the model
                # path (ModelOutputInvalidError) can echo verbatim quoted
                # document evidence text in its message, and str(exc) on
                # arbitrary exceptions elsewhere isn't guaranteed safe
                # either. The API's own typed error (INTERNAL_ERROR, a
                # fixed safe message) already carries everything a caller
                # needs; this log line is for operator correlation only.
                logger.error("job_runner: review %s failed with %s", review_id, type(exc).__name__)
                await repo.mark_failed(
                    review,
                    code="INTERNAL_ERROR",
                    message="The review could not be completed.",
                    retryable=True,
                )


def _error_kwargs(api_error) -> dict:
    return {
        "code": api_error.code,
        "message": api_error.detail["error"]["message"],
        "retryable": api_error.retryable,
    }


def _deterministic_fallback_inputs(parsed):
    from app.services.rule_engine import build_deterministic_clause_inputs

    return build_deterministic_clause_inputs(parsed)


def _to_orm_rows(
    clause_records: list[ClauseRecord], finding_records: list[FindingRecord]
) -> tuple[list[Clause], list[Finding]]:
    clause_rows: list[Clause] = []
    clause_id_by_key: dict[str, str] = {}
    for record in clause_records:
        clause = Clause(
            clause_type=record.clause_type,
            title=record.title,
            section_reference=record.section_reference,
            page_start=record.page_start,
            page_end=record.page_end,
            extracted_text=record.extracted_text,
            classification_confidence=record.classification_confidence,
        )
        clause_rows.append(clause)
        clause_id_by_key[record.key] = clause.id

    finding_rows: list[Finding] = [
        Finding(
            clause_id=clause_id_by_key.get(record.clause_key) if record.clause_key else None,
            finding_type=record.finding_type,
            clause_type=record.clause_type,
            title=record.title,
            section_reference=record.section_reference,
            page_start=record.page_start,
            page_end=record.page_end,
            evidence_text=record.evidence_text,
            classification_confidence=record.classification_confidence,
            risk_label=record.risk_label,
            rule_id=record.rule_id,
            deviation_reason=record.deviation_reason,
            recommended_action=record.recommended_action,
            needs_review=record.needs_review,
            source=record.source,
        )
        for record in finding_records
    ]
    return clause_rows, finding_rows


async def _attach_guidance(
    finding_rows: list[Finding],
    finding_records: list[FindingRecord],
    playbook: Playbook,
    settings: Settings,
) -> str:
    """Sets `guidance_json` on each Finding row in place. Returns the
    resulting retrieval_mode ("qdrant" or "degraded_full_rules"). Never
    raises — GuidanceService.retrieve_for_rules degrades to an empty result
    rather than propagating a Qdrant/embedding failure into the review."""
    if not finding_records:
        for row in finding_rows:
            row.guidance_json = "[]"
        return DEGRADED_MODE

    triggered_rules = [playbook.rule_by_id(fr.rule_id) for fr in finding_records]
    guidance_service = GuidanceService(settings)
    guidance_by_rule, retrieval_mode = await guidance_service.retrieve_for_rules(triggered_rules)

    for row, record in zip(finding_rows, finding_records):
        items = guidance_by_rule.get(record.rule_id, [])
        row.guidance_json = json.dumps([dataclasses.asdict(item) for item in items])
    return retrieval_mode


def schedule_review_job(review_id: str) -> None:
    asyncio.create_task(run_review_job(review_id))


async def recover_interrupted_jobs() -> None:
    """Restart-recovery: active jobs interrupted by a process restart move to failed.

    Any temp upload file left behind by an interrupted job is deleted
    defensively before the review is marked failed.
    """
    async with async_session_factory() as session:
        repo = ReviewRepository(session)
        result = await session.execute(select(Review).where(Review.status.in_(_ACTIVE_STATUSES)))
        interrupted = result.scalars().all()
        for review in interrupted:
            delete_temp_upload(review.upload_temp_path)
            await repo.mark_failed(
                review,
                code="JOB_INTERRUPTED",
                message="The review job was interrupted by a service restart.",
                retryable=True,
            )
