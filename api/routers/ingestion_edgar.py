from fastapi import APIRouter, HTTPException
from ingestion.services.ingestion_edgar import IngestEdgarFilingsService
from ingestion.models.ingestion import (
    IngestionRequest,
    IngestionEdgarResponse,
)

router = APIRouter()


@router.post("/ingestion/edgar", response_model=IngestionEdgarResponse)
async def ingestionEdgar(request: IngestionRequest):
    try:
        service = IngestEdgarFilingsService(ticker=request.ticker)
        result = service.run()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
