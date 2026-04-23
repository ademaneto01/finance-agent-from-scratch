from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from database.connection import SessionLocal
from database.models import TickerQueue, TickerStatus


class TickerQueueService:
    def __init__(self, session_factory: sessionmaker | None = None):
        self._session_factory = session_factory or SessionLocal

    def enqueue(self, ticker: str) -> TickerQueue:
        ticker = ticker.upper().strip()

        with self._session_factory() as session:
            existing = session.get(TickerQueue, ticker)
            print(f"Existing: {existing}")
            if existing is not None:
                # `registered` e `failed` sao finais; `pending` ja esta enfileirado.
                return existing

            row = TickerQueue(ticker=ticker, status=TickerStatus.PENDING)
            session.add(row)
            session.commit()
            session.refresh(row)
            return row

    def list_pending(self) -> list[TickerQueue]:
        with self._session_factory() as session:
            stmt = select(TickerQueue).where(
                TickerQueue.status == TickerStatus.PENDING
            )
            return list(session.scalars(stmt).all())

    def mark_registered(self, ticker: str) -> None:
        self._update_status(ticker, TickerStatus.REGISTERED, error_message=None)

    def mark_failed(self, ticker: str, error: str) -> None:
        self._update_status(
            ticker, TickerStatus.FAILED, error_message=error[:4000]
        )

    def _update_status(
        self, ticker: str, status: str, error_message: str | None
    ) -> None:
        ticker = ticker.upper().strip()
        now = datetime.now(timezone.utc)

        with self._session_factory() as session:
            row = session.get(TickerQueue, ticker)
            if row is None:
                return
            row.status = status
            row.error_message = error_message
            row.last_attempt_at = now
            session.commit()
