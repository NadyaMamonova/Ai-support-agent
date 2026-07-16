from openai import AsyncOpenAI

from app.core.config import settings
from app.schemas.ai import TicketAnalysisRequest, TicketAnalysisResponse, TicketAnalysisResult
import json

from app.schemas.chat import NativeToolCall


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
    
    
    async def complete_json(self, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
        )

        content = response.choices[0].message.content

        if content is None:
            raise ValueError("LLM returned empty response")

        return content
    

    async def choose_tool(
        self,
        message: str,
    ) -> NativeToolCall | None:
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "list_tickets",
                    "description": "Return the list of support tickets.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_ticket",
                    "description": "Get one support ticket by its integer ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {
                                "type": "integer",
                                "description": "The ticket ID.",
                            }
                        },
                        "required": ["ticket_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "create_ticket",
                    "description": "Create a new support ticket.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "A short ticket title.",
                            },
                            "description": {
                                "type": "string",
                                "description": "A detailed description of the problem.",
                            },
                        },
                        "required": ["title", "description"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "close_ticket",
                    "description": "Close a support ticket by its integer ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {
                                "type": "integer",
                                "description": "The ticket ID.",
                            }
                        },
                        "required": ["ticket_id"],
                    },
                },
            },
        ]

        response = await self.client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI support agent. "
                        "Choose the appropriate tool for the user's request. "
                        "Do not invent ticket data."
                    ),
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            tools=tools,
            tool_choice="auto",
            temperature=0,
        )

        assistant_message = response.choices[0].message

        if not assistant_message.tool_calls:
            return None

        tool_call = assistant_message.tool_calls[0]

        arguments = tool_call.function.arguments

        if isinstance(arguments, str):
            arguments = json.loads(arguments)

        return NativeToolCall(
            name=tool_call.function.name,
            arguments=arguments,
        )