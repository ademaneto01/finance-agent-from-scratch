import os
import uuid

from dotenv import load_dotenv
from fastembed import LateInteractionTextEmbedding, SparseTextEmbedding, TextEmbedding
from qdrant_client import QdrantClient, models
from ingestion.utils.yahoo_client_extraction import YahooClientExtraction
from ingestion.utils.simple_chunker import SimpleChunker

load_dotenv()

DENSE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SPARSE_MODEL = "Qdrant/bm25"
COLBERT_MODEL = "colbert-ir/colbertv2.0"
COLLECTION_NAME = "financial"
MAX_TOKENS = 300

qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)


class CreatePointsFromNewsService:
    def __init__(self, ticker: str):
        self.news_client = YahooClientExtraction()
        self.chunker = SimpleChunker(max_tokens=MAX_TOKENS)
        self.ticker = ticker
        self.dense_model = TextEmbedding(DENSE_MODEL)
        self.sparse_model = SparseTextEmbedding(SPARSE_MODEL)
        self.colbert_model = LateInteractionTextEmbedding(COLBERT_MODEL)

    def run(self):
        news_data = self.news_client.fetch_news(self.ticker, max_stories=10)

        all_chunks = []
        for article in news_data:
            chunks = self.chunker.create_chunks(article["text"])
            for chunk in chunks:
                all_chunks.append({"text": chunk, "metadata": article["metadata"]})

        points = []
        for chunk_data in all_chunks:
            chunk = chunk_data["text"]
            metadata = chunk_data["metadata"]

            dense_embedding = list(self.dense_model.passage_embed([chunk]))[0].tolist()
            sparse_embedding = list(self.sparse_model.passage_embed([chunk]))[
                0
            ].as_object()
            colbert_embedding = list(self.colbert_model.passage_embed([chunk]))[
                0
            ].tolist()

            point = models.PointStruct(
                id=str(uuid.uuid4()),
                vector={
                    "dense": dense_embedding,
                    "sparse": sparse_embedding,
                    "colbert": colbert_embedding,
                },
                payload={"text": chunk, "metadata": metadata},
            )
            points.append(point)

        qdrant.upload_points(
            collection_name=COLLECTION_NAME, points=points, batch_size=5
        )  ##batch_size é o número de pontos enviados por vez para otimizar a performance e evitar sobrecarga no servidor.

        return {
            "status": "success",
            "ticker": self.ticker,
            "collection": COLLECTION_NAME,
            "chunks_indexed": len(all_chunks),
            "points_uploaded": len(points),
            "articles_processed": len(news_data),
        }
