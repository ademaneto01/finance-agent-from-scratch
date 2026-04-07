# 🤖 Finance Agent - Análise de Investimentos Inteligente

Um **agente de inteligência artificial** construído do zero em Python puro para análise de investimentos e pesquisa financeira. Sem dependências como LangChain ou LangGraph — apenas Python, FastAPI, Groq e Qdrant.

## 📊 Posicionamento da Empresa no Setor de Investimentos

Este projeto representa um **sistema de análise financeira de próxima geração** que combina:

- **Processamento de Dados Financeiros em Tempo Real**: Integração com EDGAR (SEC Filings) e Yahoo Finance para capturar informações de mercado e relatórios corporativos
- **Análise Inteligente Baseada em IA**: Processamento de textos financeiros com LLMs de ponta (Groq/Llama) para gerar recomendações de investimento
- **Busca Semântica Avançada**: Utilização de embeddings multi-vetoriais (dense, sparse, colbert) com Qdrant para encontrar insights relevantes em grandes volumes de dados financeiros
- **Recomendações Estruturadas**: Geração de análises fundamentalistas, momentum e sentimento com recomendações de ação (BUY/HOLD/SELL)

### Diferenciais Competitivos

✅ **Análise Fundamental Completa**: Extrai pontos fortes e fraquezas de empresas baseado em filings públicas
✅ **Análise de Momentum**: Avalia tendências de curto prazo baseado em notícias e movimentos de mercado  
✅ **Análise de Sentimento**: Processa sentimento de mercado a partir de múltiplas fontes de notícias
✅ **Guardrails Inteligentes**: Valida queries para garantir segurança e relevância das análises
✅ **Busca Semântica Híbrida**: Combina busca densa, esparsa e colbert para máxima relevância
✅ **API REST Moderna**: Integração fácil com aplicações front-end e ferramentas externas

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                      FASTAPI APPLICATION                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   ROUTERS    │  │   ROUTERS    │  │   ROUTERS    │      │
│  │              │  │              │  │              │      │
│  │ • /agent     │  │ /search      │  │ /ingestion   │      │
│  │ • Analysis   │  │ • RAG Search │  │ • EDGAR      │      │
│  │ • Recommend. │  │ • Similarity │  │ • Yahoo      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
│         ┌──────────────────▼──────────────────┐             │
│         │         SERVICES LAYER              │             │
│         ├──────────────────────────────────────┤            │
│         │  AgentService  │  SearchService     │            │
│         │  RAGService    │  EmbeddingsService │            │
│         │  TickerExtract │  GuardrailsService │            │
│         └──────────────────────────────────────┘            │
│                            │                                 │
│         ┌──────────────────▼──────────────────┐             │
│         │     DATA INGESTION PIPELINE         │             │
│         ├──────────────────────────────────────┤            │
│         │  EDGAR Client    │  Yahoo Client    │            │
│         │  Semantic Chunker │Simple Chunker   │            │
│         └──────────────────────────────────────┘            │
│                            │                                 │
│         ┌──────────────────▼──────────────────┐             │
│         │   EXTERNAL SERVICES & VECTORS DB    │             │
│         ├──────────────────────────────────────┤            │
│         │  Groq LLM      │  Qdrant Vector DB │            │
│         │  EDGAR API     │  Embeddings Model │            │
│         │  Yahoo Finance │  Multi-Vector     │            │
│         │  SEC Filings   │  (Dense/Sparse)  │            │
│         └──────────────────────────────────────┘            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Funcionalidades Principais

### 1️⃣ **Agent de Análise Financeira** (`POST /agent`)
Endpoint principal que executa análise completa de um ticker:

```json
{
  "query": "Apple é um bom investimento para o longo prazo?",
  "limit": 3
}
```

**Retorna:**
- Análise Fundamental (nota A-D, teses, forças, fraquezas)
- Análise de Momentum (força, drivers, outlook)
- Análise de Sentimento (score, catalistas, outlook)
- Recomendação Final (BUY/HOLD/SELL com confiança)

### 2️⃣ **Busca Semântica** (`POST /search`)
RAG com busca híbrida multi-vetor em dados financeiros:

```json
{
  "query": "Qual foi a receita da Apple em 2023?",
  "limit": 5
}
```

**Retorna:**
- Top 5 documentos mais relevantes
- Scores de similaridade
- Contexto financeiro extraído

### 3️⃣ **Ingestão EDGAR** (`POST /ingestion/edgar`)
Captura e processa SEC Filings (10-K, 10-Q, 8-K):

```json
{
  "ticker": "AAPL",
}
```

### 4️⃣ **Ingestão Yahoo Finance** (`POST /ingestion/yahoo`)
Captura notícias e dados de mercado:

```json
{
  "ticker": "AAPL",
}
```

---

## 🚀 Instalação e Setup

### Pré-requisitos

- Python 3.13+
- UV (gerenciador de pacotes)
- Conta Groq (LLM gratuito e rápido)
- Instância Qdrant (na nuvem ou local)

### 1. Clonar o Repositório

```bash
git clone <repo-url>
cd finance-agent-from-scratch
```

### 2. Instalar Dependências

```bash
# Com UV
uv sync

### 3. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
```

Edite `.env` com suas credenciais:

```env
# Groq API (obtém em https://console.groq.com)
GROQ_API_KEY=gsk_xxxxxxxxxxxxx

# Qdrant (obtém em https://cloud.qdrant.io ou instala localmente)
QDRANT_URL=https://xxxxx-xxxxx.us-east-1-0.aws.cloud.qdrant.io
QDRANT_API_KEY=xxxxxxxxxxxxxxxx
```

### 4. **IMPORTANTE: Criar Collection no Qdrant**

Este é um **passo manual obrigatório** que precisa ser feito apenas uma vez.

#### Opção A: Executar Script Python

```bash
# Do diretório raiz do projeto
python -m api.ingestion.create_collection
```

Este script:
1. Conecta à sua instância Qdrant
2. Deleta a collection "financial" (se existir)
3. Recria com configuração otimizada para análise financeira

**✅ Pronto!** Sua collection está criada e pronta para receber dados.

### 5. Iniciar a API

```bash
# Do diretório api/
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em: **http://localhost:8000**

Documentação interativa (Swagger): **http://localhost:8000/docs**

---

## 💻 Exemplos de Uso

### Exemplo 1: Analisar um Ticker

```bash
curl -X POST "http://localhost:8000/agent" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Apple é um bom investimento?",
    "limit": 3
  }'
```

**Resposta:**
```json
{
  "query": "Apple é um bom investimento?",
  "ticker": "AAPL",
  "fundamental_analysis": {
    "overall_investment_thesis": "Apple mantém posição forte no mercado com receita crescente...",
    "investment_grade": "A",
    "confidence_score": 0.92,
    "key_strengths": [
      "Ecossistema integrado e brand loyalty",
      "Margem operacional saudável",
      "Caixa e posição financeira forte"
    ],
    "key_concerns": [
      "Dependência de mercado chinês",
      "Saturação do mercado de smartphones",
      "Pressão regulatória crescente"
    ],
    "recommendation": "buy"
  },
  "momentum_analysis": {
    "overall_momentum": "positive",
    "momentum_strength": "strong",
    "key_momentum_drivers": [
      "Crescimento em serviços",
      "Demanda por AI features"
    ],
    "momentum_risks": [
      "Volatilidade macro",
      "Pressão em preços"
    ],
    "short_term_outlook": "bullish",
    "momentum_score": 7.5
  },
  "sentiment_analysis": {
    "sentiment_score": 8.2,
    "sentiment_direction": "Positive",
    "key_news_themes": [
      "Novo lançamento de produtos",
      "Expansão AI",
      "Crescimento de receita"
    ],
    "recent_catalysts": [
      "WWDC 2024",
      "Earnings Q1 positivos",
      "Parceria com OpenAI"
    ],
    "market_outlook": "Confiança elevada no crescimento futuro"
  },
  "final_recommendation": {
    "action": "BUY",
    "confidence": 0.89,
    "rationale": "Apple apresenta fundamentos sólidos, momentum positivo e sentimento de mercado favorável...",
    "key_risks": [
      "Recessão econômica",
      "Pressão regulatória China",
      "Competição Android"
    ],
    "key_opportunities": [
      "Expansão em IA",
      "Crescimento de serviços",
      "Novos mercados"
    ],
    "time_horizon": "Long-term"
  }
}
```

### Exemplo 2: Buscar Informações Financeiras

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Qual foi a receita de Apple em 2023?",
    "limit": 5
  }'
```

### Exemplo 3: Ingerir Dados EDGAR

```bash
curl -X POST "http://localhost:8000/ingestion/edgar" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "MSFT",
  }'
```

---

## 📁 Estrutura do Projeto

```
finance-agent-from-scratch/
├── api/
│   ├── main.py                          # FastAPI app
│   ├── routers/                         # Endpoints da API
│   │   ├── agent.py                     # Agent analysis endpoint
│   │   ├── search.py                    # Search endpoint
│   │   ├── ingestion_edgar.py           # EDGAR ingestion endpoint
│   │   └── ingestion_yahoo.py           # Yahoo ingestion endpoint
│   ├── services/                        # Lógica de negócio
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
└── README.md                            # Este arquivo
```

---

## 🔧 Configuração Avançada

### Modelos Disponíveis

**Modelos de Embedding:**
- `sentence-transformers/all-MiniLM-L6-v2` (padrão, rápido, 384 dims)
- `sentence-transformers/all-mpnet-base-v2` (melhor qualidade, 768 dims)

**Modelos LLM (Groq):**
- `llama-3.1-8b-instant` (padrão)
- `mixtral-8x7b-32768`
- `gemma-7b-it`

**Modelos ColBERT:**
- `colbert-ir/colbertv2.0` (padrão)

### Customizar Settings

Edite `api/config/settings.py`:

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

## 🔒 Segurança e Guardrails

O sistema inclui validação de queries para garantir segurança:

```python
# Validação automática de queries
guardrails_service.validate_query(
    query="Qual é o melhor investimento em tech?",
    tickers=["AAPL", "MSFT", "GOOGL"]
)
```

**Validações incluídas:**
- ✅ Detecção de prompts injections
- ✅ Validação de tickers
- ✅ Verificação de contexto financeiro
- ✅ Sanitização de inputs

---

## 📊 Performance e Escalabilidade

### Busca Hybrid (3 tipos de vetores)

| Tipo | Propósito | Performance |
|------|-----------|------------|
| **Dense** | Semântica geral | ⚡ Rápido |
| **Sparse** | Busca exata de termos | ⚡⚡ Muito rápido |
| **ColBERT** | Relevância máxima | ⚡⚡⚡ Mais preciso |

### Chunking Inteligente

- **Semantic Chunker**: Divide por tópicos relevantes
- **Simple Chunker**: Divide por tamanho fixo
