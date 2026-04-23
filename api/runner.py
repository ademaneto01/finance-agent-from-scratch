import logging
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

from config.settings import settings
from database.connection import Base, engine
from database.models import TickerQueue
from ingestion.services.ingestion_edgar import IngestEdgarFilingsService
from ingestion.services.ingestion_yahoo import CreatePointsFromNewsService
from services.ticker_queue import TickerQueueService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def _ensure_tables() -> None:
    with engine.connect() as conn:
        Base.metadata.create_all(engine)
        conn.commit()


def _process_ticker(
    ticker_row: TickerQueue, queue_service: TickerQueueService
) -> tuple[bool, str | None]:
    ticker = ticker_row.ticker
    try:
        logger.info(f"  -> Edgar ingestion for {ticker}")
        edgar_result = IngestEdgarFilingsService(ticker=ticker).run()
        logger.info(
            f"     Edgar: {edgar_result.get('points_uploaded', 0)} points uploaded"
        )

        logger.info(f"  -> Yahoo ingestion for {ticker}")
        yahoo_result = CreatePointsFromNewsService(ticker=ticker).run()
        logger.info(
            f"     Yahoo: {yahoo_result.get('points_uploaded', 0)} points uploaded"
        )

        queue_service.mark_registered(ticker)
        return True, None
    except Exception as exc:
        logger.error(f"  -> Failed to ingest {ticker}: {exc}", exc_info=True)
        queue_service.mark_failed(ticker, str(exc))
        return False, str(exc)


def run_daily_ticker_ingestion() -> dict:
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("Starting Daily Ticker Ingestion Pipeline")
    logger.info("=" * 60)

    results: dict = {
        "start_time": start_time.isoformat(),
        "total": 0,
        "registered": [],
        "failed": [],
        "success": False,
    }

    try:
        logger.info("\n[0/3] Ensuring database tables exist...")
        _ensure_tables()
        logger.info("Database tables verified/created")

        queue_service = TickerQueueService()

        logger.info("\n[1/3] Listing pending tickers...")
        pending = queue_service.list_pending()
        results["total"] = len(pending)
        logger.info(f"Found {len(pending)} pending ticker(s)")

        logger.info("\n[2/3] Processing pending tickers...")
        for row in pending:
            logger.info(f"Processing ticker: {row.ticker}")
            ok, err = _process_ticker(row, queue_service)
            if ok:
                results["registered"].append(row.ticker)
            else:
                results["failed"].append({"ticker": row.ticker, "error": err})

        results["success"] = True
    except Exception as exc:
        logger.error(f"Pipeline failed with error: {exc}", exc_info=True)
        results["error"] = str(exc)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    results["end_time"] = end_time.isoformat()
    results["duration_seconds"] = duration

    logger.info("\n" + "=" * 60)
    logger.info("[3/3] Pipeline Summary")
    logger.info("=" * 60)
    logger.info(f"Duration: {duration:.1f} seconds")
    logger.info(f"Total pending: {results['total']}")
    logger.info(f"Registered: {len(results['registered'])} -> {results['registered']}")
    logger.info(f"Failed: {len(results['failed'])}")
    for f in results["failed"]:
        logger.info(f"  - {f['ticker']}: {f['error']}")
    logger.info("=" * 60)

    return results


def _sleep_until_next_run(hour: int = 0, minute: int = 0) -> None:
    tz = ZoneInfo(settings.runner_timezone)
    now = datetime.now(tz)
    next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if next_run <= now:
        next_run = next_run + timedelta(days=1)

    seconds = (next_run - now).total_seconds()
    logger.info(
        f"Sleeping until {next_run.isoformat()} ({seconds:.0f} seconds)"
    )
    time.sleep(seconds)


if __name__ == "__main__":
    logger.info("Daily ticker ingestion runner started")
    _ensure_tables()

    while True:
        _sleep_until_next_run(hour=0, minute=0)
        try:
            run_daily_ticker_ingestion()
        except Exception as exc:
            logger.error(f"Unhandled error in daily run: {exc}", exc_info=True)
