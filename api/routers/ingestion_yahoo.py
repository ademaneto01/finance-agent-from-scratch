from fastapi import APIRouter, HTTPException
from ingestion.services.ingestion_yahoo import CreatePointsFromNewsService
from ingestion.models.ingestion import (
    IngestionRequest,
    IngestionYahooResponse,
)

router = APIRouter()


@router.post("/ingestion/yahoo", response_model=IngestionYahooResponse)
async def ingestionYahoo(request: IngestionRequest):
    try:
        service = CreatePointsFromNewsService(ticker=request.ticker)
        result = service.run()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
