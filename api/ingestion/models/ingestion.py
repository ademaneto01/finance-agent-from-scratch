from pydantic import BaseModel, Field


class IngestionRequest(BaseModel):
    ticker: str = Field(..., description="The stock ticker symbol to ingest data for.")


class IngestionEdgarResponse(BaseModel):
    status: str = Field(..., description="The status of the ingestion process.")
    ticker: str = Field(..., description="The stock ticker symbol that was ingested.")
    collection: str = Field(
        ..., description="The name of the Qdrant collection where data was stored."
    )
    chunks_indexed: int = Field(
        ..., description="The number of text chunks created from the filings."
    )
    points_uploaded: int = Field(
        ..., description="The number of points uploaded to Qdrant."
    )
    form_types: list[str] = Field(
        ..., description="The types of SEC filings that were ingested."
    )


class IngestionYahooResponse(BaseModel):
    status: str = Field(..., description="The status of the ingestion process.")
    ticker: str = Field(..., description="The stock ticker symbol that was ingested.")
    collection: str = Field(
        ..., description="The name of the Qdrant collection where data was stored."
    )
    chunks_indexed: int = Field(
        ..., description="The number of text chunks created from the news articles."
    )
    points_uploaded: int = Field(
        ..., description="The number of points uploaded to Qdrant."
    )
    articles_processed: int = Field(
        ..., description="The number of news articles that were processed."
    )
