from app.schemas.chat import ChatRequest, ChatResponse, ToolCall
from app.schemas.ticket import TicketCreate
from app.services.llm_service import LLMService
from app.services.ticket_service import TicketService


class AgentService:
    def __init__(
        self,
        ticket_service: TicketService,
        llm_service: LLMService,
    ) -> None:
        self.ticket_service = ticket_service
        self.llm_service = llm_service

    async def handle_message(self, data: ChatRequest) -> ChatResponse:
        tool_call = await self._choose_tool(data.message)

        if tool_call.tool == "list_tickets":
            tickets = await self.ticket_service.list_tickets()
            return ChatResponse(answer=f"Найдено тикетов: {len(tickets)}")

        if tool_call.tool == "get_ticket":
            ticket_id = int(tool_call.arguments["ticket_id"])
            ticket = await self.ticket_service.get_ticket_by_id(ticket_id)

            if ticket is None:
                return ChatResponse(answer="Тикет не найден.")

            return ChatResponse(
                answer=(
                    f"Тикет #{ticket.id}: {ticket.title}. "
                    f"Статус: {ticket.status}."
                )
            )

        if tool_call.tool == "create_ticket":
            ticket = await self.ticket_service.create_ticket(
                TicketCreate(
                    title=tool_call.arguments["title"],
                    description=tool_call.arguments["description"],
                )
            )
            return ChatResponse(answer=f"Тикет создан. ID: {ticket.id}")

        return ChatResponse(answer="Я пока не умею выполнять такой запрос.")

    async def _choose_tool(self, message: str) -> ToolCall:
        user_prompt = (
            "Choose exactly one tool for the user request. "
            "Return only JSON. No markdown. "
            "Available tools: list_tickets, get_ticket, create_ticket. "
            "Tool schemas: "
            '{"tool":"list_tickets","arguments":{}} '
            '{"tool":"get_ticket","arguments":{"ticket_id":1}} '
            '{"tool":"create_ticket","arguments":{"title":"Short title","description":"Full description"}} '
            f"User message: {message}"
        )

        content = await self.llm_service.complete_json(
            system_prompt="You are an AI agent router. Return only valid JSON.",
            user_prompt=user_prompt,
        )

        return ToolCall.model_validate_json(content)