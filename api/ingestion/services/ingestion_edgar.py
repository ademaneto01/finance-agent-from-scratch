import os
import uuid

from dotenv import load_dotenv
from fastembed import TextEmbedding, SparseTextEmbedding, LateInteractionTextEmbedding
from qdrant_client import QdrantClient, models
from ingestion.utils.semantic_chunker import SemanticChunker
from ingestion.utils.edgar_client_extraction import EdgarClientExtraction

load_dotenv()

DENSE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SPARSE_MODEL = "Qdrant/bm25"
COLBERT_MODEL = "colbert-ir/colbertv2.0"
COLLECTION_NAME = "financial"
EMAIL = "infoslack@gmail.com"
MAX_TOKENS = 300

qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)


class IngestEdgarFilingsService:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.edgar = EdgarClientExtraction(email=EMAIL)
        self.chunker = SemanticChunker(max_tokens=MAX_TOKENS)
        self.dense_model = TextEmbedding(DENSE_MODEL)
        self.sparse_model = SparseTextEmbedding(SPARSE_MODEL)
        self.colbert_model = LateInteractionTextEmbedding(COLBERT_MODEL)

    def run(self):
        data_10k = self.edgar.fetch_filing_data(self.ticker, "10-K")
        text_10k = self.edgar.get_combined_text(data_10k)

        data_10q = self.edgar.fetch_filing_data(self.ticker, "10-Q")
        text_10q = self.edgar.get_combined_text(data_10q)

        all_chunks = []
        for data, text in [(data_10k, text_10k), (data_10q, text_10q)]:
            chunks = self.chunker.create_chunks(text)
            for chunk in chunks:
                all_chunks.append({"text": chunk, "metadata": data["metadata"]})

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
        )

        return {
            "status": "success",
            "ticker": self.ticker,
            "collection": COLLECTION_NAME,
            "chunks_indexed": len(all_chunks),
            "points_uploaded": len(points),
            "form_types": ["10-K", "10-Q"],
        }
