from typing import Any, Dict, Optional

from models.search import SearchResponse, SearchResult
from qdrant_client import QdrantClient, models
from services.ticker_extractor import TickerExtractor

from services.embeddings import EmbeddingService


class SearchService:
    def __init__(self, qdrant_url: str, qdrant_api_key: str, collection_name: str):
        self.qdrant = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        self.collection_name = collection_name
        self.embedding_service = EmbeddingService()
        self.ticker_extractor = TickerExtractor()

    def _build_qdrant_filter(self, filters: Optional[Dict[str, Any]]) -> Optional[Dict]:
        if not filters:
            return None

        must_conditions = []
        for key, value in filters.items():
            must_conditions.append(
                {"key": f"metadata.{key}", "match": {"value": value}}
            )
        return {"must": must_conditions}

    def search(
        self, query: str, limit: int = 3, filter: Optional[Dict[str, Any]] = None
    ):
        if not filter:
            ticker = self.ticker_extractor.extract_ticker(query)

            if not ticker or ticker == "NONE":
                raise ValueError(
                    "No momento nao conseguimos identificar a empresa da sua pergunta. Tente informar o ticker ou o nome da empresa."
                )

            filter = {"ticker": ticker}

        query_dense, query_sparse, query_colbert = self.embedding_service.embed_query(
            query
        )

        query_filter = self._build_qdrant_filter(filter)

        results = self.qdrant.query_points(
            collection_name=self.collection_name,
            prefetch=[
                {
                    "prefetch": [
                        {"query": query_dense, "using": "dense", "limit": 20},
                        {"query": query_sparse, "using": "sparse", "limit": 20},
                    ],
                    "query": models.FusionQuery(fusion=models.Fusion.RRF),
                    "limit": 15,
                }
            ],
            query=query_colbert,
            using="colbert",
            limit=limit,
            query_filter=query_filter,
        )

        if not results.points:
            return SearchResponse(results=[])

        max_score = max(result.score for result in results.points)

        search_results = [
            SearchResult(
                score=result.score / max_score,
                text=result.payload["text"],
                metadata=result.payload["metadata"],
            )
            for result in results.points
        ]

        return SearchResponse(results=search_results)
