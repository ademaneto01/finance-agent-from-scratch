from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.connection import Base


class TickerStatus:
    PENDING = "pending"
    REGISTERED = "registered"
    FAILED = "failed"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TickerQueue(Base):
    __tablename__ = "ticker_queue"

    ticker: Mapped[str] = mapped_column(String(5), primary_key=True)
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default=TickerStatus.PENDING, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        onupdate=_utcnow,
    )
    last_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<TickerQueue ticker={self.ticker} status={self.status} "
            f"updated_at={self.updated_at.isoformat() if self.updated_at else None}>"
        )
