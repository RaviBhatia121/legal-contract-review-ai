import json

from fastapi import APIRouter, Depends, Form, Query, Response, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.errors import review_expired, review_not_found
from app.core.config import get_settings
from app.core.job_runner import schedule_review_job
from app.db.models import Finding, Review
from app.db.repository import ReviewRepository
from app.db.session import get_session
from app.schemas.review import (
    DocumentInfo,
    DraftClauseOut,
    ErrorOut,
    FindingOut,
    FindingsByRisk,
    GuidanceItemOut,
    Provenance,
    ReviewCreated,
    ReviewListOut,
    ReviewOut,
    ReviewSummary,
    ReviewSummaryItem,
)
from app.services.drafting import draft_clause_for_rule
from app.services.retention import is_expired
from app.services.upload import delete_temp_upload, sha256_hex, validate_and_read_upload, write_temp_upload

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])


def _finding_to_out(finding: Finding) -> FindingOut:
    guidance = [GuidanceItemOut(**item) for item in json.loads(finding.guidance_json or "[]")]
    draft_clause = draft_clause_for_rule(finding.rule_id)
    draft_clause_out = (
        DraftClauseOut(
            text=draft_clause.text,
            source=draft_clause.source,
            approval_note=draft_clause.approval_note,
        )
        if draft_clause
        else None
    )
    return FindingOut(
        finding_id=finding.id,
        finding_type=finding.finding_type,  # type: ignore[arg-type]
        clause_id=finding.clause_id,
        clause_type=finding.clause_type or "unknown",
        title=finding.title,
        section_reference=finding.section_reference,
        page_start=finding.page_start,
        page_end=finding.page_end,
        evidence_text=finding.evidence_text,
        classification_confidence=finding.classification_confidence,
        risk_label=finding.risk_label,  # type: ignore[arg-type]
        rule_id=finding.rule_id,
        deviation_reason=finding.deviation_reason,
        recommended_action=finding.recommended_action,
        needs_review=finding.needs_review,
        source=finding.source,  # type: ignore[arg-type]
        guidance=guidance,
        suggested_draft_clause=draft_clause_out,
    )


def _build_review_out(review: Review) -> ReviewOut:
    if review.status == "failed":
        return ReviewOut(
            review_id=review.id,
            status="failed",
            error=ErrorOut(
                code=review.error_code or "INTERNAL_ERROR",
                message=review.error_message or "The review could not be completed.",
                retryable=bool(review.error_retryable),
            ),
        )

    if review.status != "completed":
        return ReviewOut(
            review_id=review.id,
            status=review.status,  # type: ignore[arg-type]
            current_stage=review.current_stage,
            created_at=review.created_at.isoformat() if review.created_at else None,
            started_at=review.started_at.isoformat() if review.started_at else None,
        )

    findings = [_finding_to_out(f) for f in review.findings if f.finding_type != "missing_clause"]
    missing_clauses = [_finding_to_out(f) for f in review.findings if f.finding_type == "missing_clause"]
    all_findings = findings + missing_clauses

    by_risk = FindingsByRisk(Critical=0, High=0, Medium=0, Low=0)
    for f in all_findings:
        setattr(by_risk, f.risk_label, getattr(by_risk, f.risk_label) + 1)

    settings = get_settings()
    return ReviewOut(
        review_id=review.id,
        document=DocumentInfo(
            name=review.document_name,
            sha256=review.document_sha256,
            page_count=review.document_page_count or 0,
            language=review.document_language,
        ),
        status="completed",
        review_summary=ReviewSummary(
            overall_risk=review.overall_risk,  # type: ignore[arg-type]
            clauses_reviewed=len(review.clauses),
            findings_total=len(all_findings),
            findings_by_risk=by_risk,
            missing_clause_count=len(missing_clauses),
            needs_review_count=sum(1 for f in all_findings if f.needs_review),
        ),
        findings=findings,
        missing_clauses=missing_clauses,
        provenance=Provenance(
            deployment_mode=review.deployment_mode,  # type: ignore[arg-type]
            pipeline_version=review.pipeline_version,
            playbook_version=review.playbook_version,
            prompt_version=review.prompt_version,
            parser_name=review.parser_name or "none",
            parser_version=review.parser_version or "unknown",
            model_provider=review.model_provider or "rule-engine",
            model_name=review.model_name or "none",
            model_revision=review.model_revision,
            mode_requested=review.mode_requested,  # type: ignore[arg-type]
            mode_used=review.mode_used,  # type: ignore[arg-type]
            fallback_used=bool(review.fallback_used),
            fallback_reason=review.fallback_reason,
            retrieval_mode=review.retrieval_mode,  # type: ignore[arg-type]
            completed_at=review.completed_at.isoformat() if review.completed_at else "",
        ),
    )


@router.post("", status_code=202, response_model=ReviewCreated)
async def create_review(
    file: UploadFile,
    playbook_id: str = Form(default="defense-services-v1"),
    session: AsyncSession = Depends(get_session),
) -> ReviewCreated:
    content, display_name, extension = await validate_and_read_upload(file)
    digest = sha256_hex(content)
    temp_path = write_temp_upload(content, extension)

    settings = get_settings()
    review = Review(
        document_name=display_name,
        document_sha256=digest,
        playbook_id=playbook_id,
        deployment_mode=settings.deployment_mode,
        upload_temp_path=temp_path,
    )
    repo = ReviewRepository(session)
    try:
        review = await repo.create_review(review)
    except Exception:
        delete_temp_upload(temp_path)
        raise

    schedule_review_job(review.id)

    return ReviewCreated(
        review_id=review.id,
        status="queued",
        status_url=f"/api/v1/reviews/{review.id}",
    )


@router.get("", response_model=ReviewListOut)
async def list_reviews(
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> ReviewListOut:
    """Summary-only review history for the dashboard (P8.1). Never returns
    evidence text, full findings, parsed text, or model/credential internals.
    Expired terminal reviews encountered on this page are deleted, same as
    GET /{review_id} — so a returned page may contain fewer than `limit`
    items when expired rows were purged; this is expected, not a bug."""
    repo = ReviewRepository(session)
    rows = await repo.list_summaries(limit=limit, offset=offset, settings=get_settings())
    items = [
        ReviewSummaryItem(
            review_id=review.id,
            document_name=review.document_name,
            status=review.status,  # type: ignore[arg-type]
            overall_risk=review.overall_risk,  # type: ignore[arg-type]
            created_at=review.created_at.isoformat() if review.created_at else "",
            completed_at=review.completed_at.isoformat() if review.completed_at else None,
            findings_total=findings_total,
            missing_clause_count=missing_clause_count,
            needs_review_count=needs_review_count,
            deployment_mode=review.deployment_mode,  # type: ignore[arg-type]
            retrieval_mode=review.retrieval_mode,  # type: ignore[arg-type]
            mode_used=review.mode_used,  # type: ignore[arg-type]
            fallback_used=bool(review.fallback_used),
        )
        for review, findings_total, missing_clause_count, needs_review_count in rows
    ]
    return ReviewListOut(items=items, limit=limit, offset=offset)


@router.get("/{review_id}", response_model=ReviewOut)
async def get_review(review_id: str, session: AsyncSession = Depends(get_session)) -> ReviewOut:
    repo = ReviewRepository(session)
    review = await repo.get(review_id)
    if review is None:
        raise review_not_found()

    if is_expired(review, get_settings()):
        await repo.delete(review)
        raise review_expired()

    return _build_review_out(review)


@router.delete("/{review_id}", status_code=204)
async def delete_review(review_id: str, session: AsyncSession = Depends(get_session)) -> Response:
    repo = ReviewRepository(session)
    review = await repo.get(review_id)
    if review is None:
        raise review_not_found()
    await repo.delete(review)
    return Response(status_code=204)
