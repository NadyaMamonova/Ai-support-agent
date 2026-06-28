from openai import AsyncOpenAI

from app.core.config import settings
from app.schemas.ai import TicketAnalysisRequest, TicketAnalysisResponse, TicketAnalysisResult


class LLMService:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )

    async def analyze_ticket(
        self,
        data: TicketAnalysisRequest,
    ) -> TicketAnalysisResult:
        prompt = (
            f"Title: {data.title}\n"
            f"Description: {data.description}"
        )
        response = await self.client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict support ticket classifier. "
                        "Return exactly one JSON object with exactly these keys: "
                        "category, priority, summary, suggested_resolution. "
                        "Allowed categories: billing, database, auth, infrastructure, bug, other, invalid. "
                        "Allowed priorities: low, medium, high, critical. "
                        "If input is not a support ticket, return: "
                        '{"category":"invalid","priority":"low","summary":"Input is not a support ticket.","suggested_resolution":[]} '
                        "Do not answer questions. Do not solve math. "
                        "Return JSON only. No markdown."
                )
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
        )

        content = response.choices[0].message.content

        if content is None:
            raise ValueError("LLM returned empty response")

        analysis = TicketAnalysisResponse.model_validate_json(content)

        return TicketAnalysisResult(
            analysis=analysis,
            prompt=prompt,
            raw_response=content,
            model=settings.llm_model,
        )