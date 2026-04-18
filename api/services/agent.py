import asyncio
import instructor

from config.prompts import (
    AGGREGATION_PROMPT,
    FUNDAMENTAL_PROMPT,
    FUNDAMENTAL_QUERIES,
    MOMENTUM_PROMPT,
    MOMENTUM_QUERIES,
    SENTIMENT_PROMPT,
    SENTIMENT_QUERY_TEMPLATE,
)
from config.settings import settings
from groq import AsyncGroq
from models.agent import (
    AgentResponse,
    FinalRecommendation,
    FundamentalAnalysis,
    MomentumAnalysis,
    SentimentAnalysis,
)

from services.search import SearchService
from services.ticker_extractor import TickerExtractor
# from validators.guardrails_service import GuardrailsService


class AgentService:
    def __init__(self, search_service: SearchService):
        self.search_service = search_service
        client = AsyncGroq(api_key=settings.groq_api_key)
        self.client = instructor.from_groq(client, mode=instructor.Mode.JSON)
        self.ticker_extractor = TickerExtractor()
        # self.guardrails = GuardrailsService()

    def _run_queries(self, queries: list[str], limit: int, filter: dict = None):
        all_results = []
        for query in queries:
            search_results = self.search_service.search(query, limit, filter)
            all_results.extend([result.text for result in search_results.results])
        return "\n\n".join(all_results)

    async def _generate_completion(self, prompt: str, response_model=None):
        return await self.client.chat.completions.create(
            model=settings.groq_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_model=response_model,
        )

    async def _analyze_fundamental(self, ticker: str, limit: int):
        filter = {"ticker": ticker, "form_type": "10-K"}
        context = self._run_queries(FUNDAMENTAL_QUERIES, limit, filter)
        prompt = FUNDAMENTAL_PROMPT.format(context=context)
        return await self._generate_completion(prompt, FundamentalAnalysis)

    async def _analyze_momentum(self, ticker: str, limit: int):
        filter = {"ticker": ticker, "form_type": "10-Q"}
        context = self._run_queries(MOMENTUM_QUERIES, limit, filter)
        prompt = MOMENTUM_PROMPT.format(context=context)
        return await self._generate_completion(prompt, MomentumAnalysis)

    async def _analyze_sentiment(self, ticker: str, limit: int):
        filter = {"ticker": ticker, "source": "yahoo_finance"}
        query = SENTIMENT_QUERY_TEMPLATE.format(ticker=ticker)
        results = self.search_service.search(query, limit, filter)
        context = "\n\n".join([result.text for result in results.results])
        prompt = SENTIMENT_PROMPT.format(context=context)
        return await self._generate_completion(prompt, SentimentAnalysis)

    async def analyze(self, query: str, limit: int = 3):

        # try:
        #     validated_query = self.guardrails.validate_query(query)
        # except Exception as e:
        #     raise ValueError(f"Query rejeitada pelo Guardrails: {e}")

        # ticker = self.ticker_extractor.extract_ticker(validated_query)

        # if not ticker:
        #     raise ValueError("Could not extract a valid ticker symbol from the query")

        # ticker = self.guardrails.validate_ticker(ticker)

        ticker = self.ticker_extractor.extract_ticker(query)

        if ticker == "NONE":
            raise ValueError(
                "No momento nao conseguimos identificar a empresa da sua pergunta. Tente informar o ticker ou o nome da empresa."
            )

        fundamental_filter = {"ticker": ticker, "form_type": "10-K"}
        fundamental_context = self._run_queries(FUNDAMENTAL_QUERIES, limit, fundamental_filter)
        
        if not fundamental_context.strip():
            raise ValueError(
                f"No momento ainda nao temos dados suficientes da empresa {ticker} na nossa base para gerar essa analise. Estamos trabalhando para ampliar a cobertura em breve."
            )

        fundamental_task = self._analyze_fundamental(ticker, limit)
        momentum_task = self._analyze_momentum(ticker, limit)
        sentiment_task = self._analyze_sentiment(ticker, limit)

        (
            fundamental_analysis,
            momentum_analysis,
            sentiment_analysis,
        ) = await asyncio.gather(fundamental_task, momentum_task, sentiment_task)

        aggregation_prompt = AGGREGATION_PROMPT.format(
            fundamental=fundamental_analysis.model_dump_json(indent=2),
            momentum=momentum_analysis.model_dump_json(indent=2),
            sentiment=sentiment_analysis.model_dump_json(indent=2),
        )
        final_recomendation = await self._generate_completion(
            aggregation_prompt, FinalRecommendation
        )

        return AgentResponse(
            query=query,
            ticker=ticker,
            fundamental_analysis=fundamental_analysis,
            momentum_analysis=momentum_analysis,
            sentiment_analysis=sentiment_analysis,
            final_recommendation=final_recomendation,
        )
