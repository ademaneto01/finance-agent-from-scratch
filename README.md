# 🤖 Finance Agent - Intelligent Investment Analysis

An **artificial intelligence agent** built from scratch in pure Python for investment analysis and financial research. No dependencies like LangChain or LangGraph — just Python, FastAPI, Groq, and Qdrant.

## 📊 Company Positioning in the Investment Space

This project represents a **next-generation financial analysis system** that combines:

- **Real-Time Financial Data Processing**: Integration with EDGAR (SEC Filings) and Yahoo Finance to capture market information and corporate reports
- **AI-Powered Intelligent Analysis**: Processing of financial text with state-of-the-art LLMs (Groq/Llama) to generate investment recommendations
- **Advanced Semantic Search**: Multi-vector embeddings (dense, sparse, ColBERT) with Qdrant to find relevant insights in large volumes of financial data
- **Structured Recommendations**: Generation of fundamental, momentum, and sentiment analyses with action recommendations (BUY/HOLD/SELL)

### Competitive Differentiators

✅ **Full Fundamental Analysis**: Extracts strengths and weaknesses of companies based on public filings  
✅ **Momentum Analysis**: Evaluates short-term trends based on news and market moves  
✅ **Sentiment Analysis**: Processes market sentiment from multiple news sources  
✅ **Smart Guardrails**: Validates queries to ensure safety and relevance of analyses  
✅ **Hybrid Semantic Search**: Combines dense, sparse, and ColBERT search for maximum relevance  
✅ **Modern REST API**: Easy integration with front-end applications and external tools  

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FASTAPI APPLICATION                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   ROUTERS    │  │   ROUTERS    │  │   ROUTERS    │       │
│  │              │  │              │  │              │       │
│  │ • /agent     │  │ /search      │  │ /ingestion   │       │
│  │ • Analysis   │  │ • RAG Search │  │ • EDGAR      │       │
│  │ • Recommend. │  │ • Similarity │  │ • Yahoo      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         │                  │                  │             │
│         └──────────────────┼──────────────────┘             │
│                            │                                │
│         ┌──────────────────▼──────────────────┐             │
│         │         SERVICES LAYER              │             │
│         ├─────────────────────────────────────┤             │
│         │  AgentService  │  SearchService     │             │
│         │  RAGService    │  EmbeddingsService │             │
│         │  TickerExtract │  GuardrailsService │             │
│         └─────────────────────────────────────┘             │
│                            │                                │
│         ┌──────────────────▼──────────────────┐             │
│         │     DATA INGESTION PIPELINE         │             │
│         ├─────────────────────────────────────┤             │
│         │  EDGAR Client    │  Yahoo Client    │             │
│         │  Semantic Chunker │Simple Chunker   │             │
│         └─────────────────────────────────────┘             │
│                            │                                │
│         ┌──────────────────▼──────────────────┐             │
│         │   EXTERNAL SERVICES & VECTORS DB    │             │
│         ├─────────────────────────────────────┤             │
│         │  Groq LLM      │  Qdrant Vector DB  │             │
│         │  EDGAR API     │  Embeddings Model  │             │
│         │  Yahoo Finance │  Multi-Vector      │             │
│         │  SEC Filings   │  (Dense/Sparse)    │             │
│         └─────────────────────────────────────┘             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Main Features

### 1️⃣ **Financial Analysis Agent** (`POST /agent`)
Main endpoint that runs a full analysis for a ticker:

```json
{
  "query": "Is Apple a good long-term investment?",
  "limit": 3
}
```

**Returns:**
- Fundamental Analysis (grade A-D, thesis, strengths, weaknesses)
- Momentum Analysis (strength, drivers, outlook)
- Sentiment Analysis (score, catalysts, outlook)
- Final Recommendation (BUY/HOLD/SELL with confidence)

### 2️⃣ **Semantic Search** (`POST /search`)
RAG with hybrid multi-vector search over financial data:

```json
{
  "query": "What was Apple's revenue in 2023?",
  "limit": 5
}
```

**Returns:**
- Top 5 most relevant documents
- Similarity scores
- Extracted financial context

### 3️⃣ **EDGAR Ingestion** (`POST /ingestion/edgar`)
Fetches and processes SEC Filings (10-K, 10-Q, 8-K):

```json
{
  "ticker": "AAPL",
}
```

### 4️⃣ **Yahoo Finance Ingestion** (`POST /ingestion/yahoo`)
Fetches news and market data:

```json
{
  "ticker": "AAPL",
}
```

---

## 🚀 Installation and Setup

### Prerequisites

- Python 3.13+
- UV (package manager)
- Groq account (free and fast LLM)
- Qdrant instance (cloud or local)

### 1. Clone the Repository

```bash
git clone <repo-url>
cd finance-agent-from-scratch
```

### 2. Install Dependencies

```bash
# With UV
uv sync
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Groq API (get at https://console.groq.com)
GROQ_API_KEY=gsk_xxxxxxxxxxxxx

# Qdrant (get at https://cloud.qdrant.io or install locally)
QDRANT_URL=https://xxxxx-xxxxx.us-east-1-0.aws.cloud.qdrant.io
QDRANT_API_KEY=xxxxxxxxxxxxxxxx
```

### 4. **IMPORTANT: Create Collection in Qdrant**

This is a **mandatory manual step** that only needs to be done once.

#### Option A: Run Python Script

```bash
# From the project root directory
python -m api.ingestion.create_collection
```

This script:
1. Connects to your Qdrant instance
2. Deletes the "financial" collection (if it exists)
3. Recreates it with settings optimized for financial analysis

**✅ Done!** Your collection is created and ready to receive data.

### 5. Start the API

```bash
# From the api/ directory
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: **http://localhost:8000**

Interactive documentation (Swagger): **http://localhost:8000/docs**

---

## 💻 Usage Examples

### Example 1: Analyze a Ticker

```bash
curl -X POST "http://localhost:8000/agent" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Is Apple a good investment?",
    "limit": 3
  }'
```

**Response:**
```json
{
  "query": "Is Apple a good investment?",
  "ticker": "AAPL",
  "fundamental_analysis": {
    "overall_investment_thesis": "Apple maintains a strong market position with growing revenue...",
    "investment_grade": "A",
    "confidence_score": 0.92,
    "key_strengths": [
      "Integrated ecosystem and brand loyalty",
      "Healthy operating margin",
      "Strong cash position and balance sheet"
    ],
    "key_concerns": [
      "Dependence on the Chinese market",
      "Smartphone market saturation",
      "Increasing regulatory pressure"
    ],
    "recommendation": "buy"
  },
  "momentum_analysis": {
    "overall_momentum": "positive",
    "momentum_strength": "strong",
    "key_momentum_drivers": [
      "Services growth",
      "Demand for AI features"
    ],
    "momentum_risks": [
      "Macro volatility",
      "Pricing pressure"
    ],
    "short_term_outlook": "bullish",
    "momentum_score": 7.5
  },
  "sentiment_analysis": {
    "sentiment_score": 8.2,
    "sentiment_direction": "Positive",
    "key_news_themes": [
      "New product launches",
      "AI expansion",
      "Revenue growth"
    ],
    "recent_catalysts": [
      "WWDC 2024",
      "Positive Q1 earnings",
      "Partnership with OpenAI"
    ],
    "market_outlook": "High confidence in future growth"
  },
  "final_recommendation": {
    "action": "BUY",
    "confidence": 0.89,
    "rationale": "Apple shows solid fundamentals, positive momentum, and favorable market sentiment...",
    "key_risks": [
      "Economic recession",
      "Regulatory pressure in China",
      "Android competition"
    ],
    "key_opportunities": [
      "Expansion in AI",
      "Services growth",
      "New markets"
    ],
    "time_horizon": "Long-term"
  }
}
```

### Example 2: Search Financial Information

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What was Apple's revenue in 2023?",
    "limit": 5
  }'
```

### Example 3: Ingest EDGAR Data

```bash
curl -X POST "http://localhost:8000/ingestion/edgar" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "MSFT",
  }'
```

---

## 📁 Project Structure

```
finance-agent-from-scratch/
├── api/
│   ├── main.py                          # FastAPI app
│   ├── routers/                         # API endpoints
│   │   ├── agent.py                     # Agent analysis endpoint
│   │   ├── search.py                    # Search endpoint
│   │   ├── ingestion_edgar.py           # EDGAR ingestion endpoint
│   │   └── ingestion_yahoo.py           # Yahoo ingestion endpoint
│   ├── services/                        # Business logic
│   │   ├── agent.py                     # Agent service
│   │   ├── search.py                    # Search service
│   │   ├── rag.py                       # RAG service
│   │   ├── embeddings.py                # Embeddings service
│   │   ├── ticker_extractor.py          # Ticker extraction
│   │   └── guardrails_service.py        # Query validation
│   ├── models/                          # Data models
│   │   ├── agent.py                     # Agent request/response
│   │   ├── search.py                    # Search request/response
│   │   └── rag.py                       # RAG models
│   ├── validators/                      # Validation logic
│   │   └── guardrails_service.py        # Query safety checks
│   ├── ingestion/                       # Data ingestion
│   │   ├── create_collection.py         # 🔑 Collection setup script
│   │   ├── create_indexes.py            # Index creation
│   │   ├── services/                    # Ingestion services
│   │   │   ├── ingestion_edgar.py       # EDGAR processor
│   │   │   └── ingestion_yahoo.py       # Yahoo processor
│   │   ├── utils/                       # Utilities
│   │   │   ├── edgar_client_extraction.py
│   │   │   ├── yahoo_client_extraction.py
│   │   │   ├── semantic_chunker.py      # Smart text chunking
│   │   │   └── simple_chunker.py        # Basic chunking
│   │   └── models/
│   │       └── ingestion.py             # Ingestion models
│   └── config/                          # Configuration
│       ├── settings.py                  # App settings
│       ├── company_mappings.py          # Ticker mappings
│       └── prompts.py                   # LLM prompts
├── .env.example                         # Environment template
├── pyproject.toml                       # Project metadata
└── README.md                            # This file
```

---

## 🔧 Advanced Configuration

### Available Models

**Embedding models:**
- `sentence-transformers/all-MiniLM-L6-v2` (default, fast, 384 dims)
- `sentence-transformers/all-mpnet-base-v2` (better quality, 768 dims)

**LLM models (Groq):**
- `llama-3.1-8b-instant` (default)
- `mixtral-8x7b-32768`
- `gemma-7b-it`

**ColBERT models:**
- `colbert-ir/colbertv2.0` (default)

### Customize Settings

Edit `api/config/settings.py`:

```python
class Settings(BaseSettings):
    qdrant_url: str
    qdrant_api_key: str
    collection_name: str = "financial"
    dense_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    sparse_model: str = "Qdrant/bm25"
    colbert_model: str = "colbert-ir/colbertv2.0"
    groq_api_key: str
    groq_model: str = "llama-3.1-8b-instant"
```

---

## 🔒 Security and Guardrails

The system includes query validation for safety:

```python
# Automatic query validation
guardrails_service.validate_query(
    query="What is the best tech investment?",
    tickers=["AAPL", "MSFT", "GOOGL"]
)
```

**Validations included:**
- ✅ Prompt injection detection
- ✅ Ticker validation
- ✅ Financial context checks
- ✅ Input sanitization

---

## 📊 Performance and Scalability

### Hybrid Search (3 vector types)

| Type | Purpose | Performance |
|------|---------|-------------|
| **Dense** | General semantics | ⚡ Fast |
| **Sparse** | Exact term search | ⚡⚡ Very fast |
| **ColBERT** | Maximum relevance | ⚡⚡⚡ Most accurate |

### Smart Chunking

- **Semantic Chunker**: Splits by relevant topics
- **Simple Chunker**: Splits by fixed size
