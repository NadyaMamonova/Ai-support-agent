import json

from openai import AsyncOpenAI

from app.core.config import settings
from app.schemas.ai import TicketAnalysisRequest, TicketAnalysisResponse


class LLMService:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )

    async def analyze_ticket(
        self,
        data: TicketAnalysisRequest,
    ) -> TicketAnalysisResponse:
        response = await self.client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI support ticket classifier. "
                        "Return only valid JSON with keys: "
                        "category, priority, summary. "
                        "priority must be one of: low, medium, high, critical."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Title: {data.title}\n"
                        f"Description: {data.description}"
                    ),
                },
            ],
            temperature=0,
        )

        content = response.choices[0].message.content

        if content is None:
            raise ValueError("LLM returned empty response")

        return TicketAnalysisResponse.model_validate_json(content)