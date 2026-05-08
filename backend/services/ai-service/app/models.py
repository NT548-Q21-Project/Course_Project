import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class MatchResult(Base):
    __tablename__ = "match_results"
    __table_args__ = (
        CheckConstraint(
            "fit_level IN ('strong_fit', 'fit', 'weak_fit', 'not_fit')",
            name="check_match_results_fit_level",
        ),
        UniqueConstraint(
            "cv_id",
            "job_id",
            name="uq_match_results_cv_id_job_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    cv_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    fit_level: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    strengths: Mapped[list[str] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    weaknesses: Mapped[list[str] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    suggestions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
