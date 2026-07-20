from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Clause, Finding, Review


class ReviewRepository:
    """SQLite-backed repository boundary for review records.

    All review/clause/finding persistence goes through this class so callers
    never issue raw queries against the ORM session directly.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_review(self, review: Review) -> Review:
        self._session.add(review)
        await self._session.commit()
        await self._session.refresh(review)
        return review

    async def get(self, review_id: str) -> Review | None:
        stmt = (
            select(Review)
            .where(Review.id == review_id)
            .options(selectinload(Review.clauses), selectinload(Review.findings))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(
        self,
        review: Review,
        *,
        status: str,
        current_stage: str | None,
        started_at: datetime | None = None,
    ) -> Review:
        review.status = status
        review.current_stage = current_stage
        if started_at is not None:
            review.started_at = started_at
        await self._session.commit()
        await self._session.refresh(review)
        return review

    async def set_parsed_document(
        self,
        review: Review,
        *,
        parsed_text: str,
        document_page_count: int,
        document_language: str,
        parser_name: str,
        parser_version: str,
    ) -> Review:
        review.parsed_text = parsed_text
        review.document_page_count = document_page_count
        review.document_language = document_language
        review.parser_name = parser_name
        review.parser_version = parser_version
        await self._session.commit()
        await self._session.refresh(review)
        return review

    async def clear_upload_temp_path(self, review: Review) -> Review:
        review.upload_temp_path = None
        await self._session.commit()
        await self._session.refresh(review)
        return review

    async def mark_completed(
        self,
        review: Review,
        *,
        overall_risk: str,
        clauses: list[Clause],
        findings: list[Finding],
        document_page_count: int,
        document_language: str,
        model_provider: str,
        model_name: str,
        model_revision: str | None,
        retrieval_mode: str,
    ) -> Review:
        review.status = "completed"
        review.current_stage = None
        review.overall_risk = overall_risk
        review.completed_at = datetime.now(timezone.utc)
        review.document_page_count = document_page_count
        review.document_language = document_language
        review.model_provider = model_provider
        review.model_name = model_name
        review.model_revision = model_revision
        review.retrieval_mode = retrieval_mode
        review.upload_temp_path = None
        for clause in clauses:
            clause.review_id = review.id
            self._session.add(clause)
        for finding in findings:
            finding.review_id = review.id
            self._session.add(finding)
        await self._session.commit()
        await self._session.refresh(review)
        return review

    async def mark_failed(
        self,
        review: Review,
        *,
        code: str,
        message: str,
        retryable: bool,
        parse_error_code: str | None = None,
    ) -> Review:
        review.status = "failed"
        review.current_stage = None
        review.error_code = code
        review.error_message = message
        review.error_retryable = retryable
        if parse_error_code is not None:
            review.parse_error_code = parse_error_code
        review.completed_at = datetime.now(timezone.utc)
        review.upload_temp_path = None
        await self._session.commit()
        await self._session.refresh(review)
        return review

    async def delete(self, review: Review) -> None:
        await self._session.delete(review)
        await self._session.commit()
