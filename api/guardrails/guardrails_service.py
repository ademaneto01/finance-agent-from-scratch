# services/guardrails_service.py
from guardrails import Guard
from guardrails.hub import ProfanityFree
from openai import OpenAI
from config.settings import settings


def groq_wrapper(*, messages, **kwargs) -> str:
    """Wrapper síncrono para o Guardrails usar o Groq como validador."""
    from openai import OpenAI

    client = OpenAI(
        base_url="https://api.groq.com/openai/v1", api_key=settings.groq_api_key
    )
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
    )
    return response.choices[0].message.content


class GuardrailsService:
    def __init__(self):
        # Guard para validar a query de entrada do usuário
        self.input_guard = Guard().use_many(
            ProfanityFree(on_fail="exception"),
        )

    def validate_query(self, query: str) -> str:
        """
        Valida a query antes de qualquer chamada LLM.
        Retorna a query validada ou lança uma exceção.
        """
        result = self.input_guard.validate(query)
        return result.validated_output

    def validate_ticker(self, ticker: str) -> str:
        """
        Valida o ticker extraído com uma regex simples.
        Retorna o ticker ou lança ValueError.
        """
        import re

        if not re.match(r"^[A-Z]{1,5}$", ticker):
            raise ValueError(
                f"Ticker inválido: '{ticker}'. Deve ter 1-5 letras maiúsculas."
            )
        return ticker
