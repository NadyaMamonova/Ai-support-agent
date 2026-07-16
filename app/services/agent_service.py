from app.schemas.chat import ChatRequest, ChatResponse, ToolCall
from app.schemas.ticket import TicketCreate, TicketStatus
from app.services.llm_service import LLMService
from app.services.ticket_service import TicketService
from app.repositories.agent_tool_call_repository import AgentToolCallRepository


class AgentService:
    def __init__(
        self,
        ticket_service: TicketService,
        llm_service: LLMService,
        tool_call_repository: AgentToolCallRepository,
    ) -> None:
        self.ticket_service = ticket_service
        self.llm_service = llm_service
        self.tool_call_repository = tool_call_repository

    async def handle_message(self, data: ChatRequest) -> ChatResponse:
        tool_call = await self._choose_tool(data.message)

        if tool_call.tool == "list_tickets":
            tickets = await self.ticket_service.list_tickets()
            result = f"Найдено тикетов: {len(tickets)}"

            await self.tool_call_repository.create(
                tool_name=tool_call.tool,
                arguments=tool_call.arguments,
                result=result,
            )

            return ChatResponse(answer=result)

        if tool_call.tool == "get_ticket":
            ticket_id = int(tool_call.arguments["ticket_id"])
            ticket = await self.ticket_service.get_ticket_by_id(ticket_id)

            if ticket is None:
                result = "Тикет не найден."
                ticket_id_for_log = ticket_id

            else:
                result = f"Тикет #{ticket.id}: {ticket.title}. Статус: {ticket.status}."
                ticket_id_for_log = ticket.id

            await self.tool_call_repository.create(
                tool_name=tool_call.tool,
                arguments=tool_call.arguments,
                result=result,
                ticket_id=ticket_id_for_log,
            )

            return ChatResponse(answer=result)

        if tool_call.tool == "create_ticket":
            ticket = await self.ticket_service.create_ticket(
                TicketCreate(
                    title=tool_call.arguments["title"],
                    description=tool_call.arguments["description"],
                )
            )
            result = f"Тикет создан. ID: {ticket.id}"

            await self.tool_call_repository.create(
                tool_name=tool_call.tool,
                arguments=tool_call.arguments,
                result=result,
                ticket_id=ticket.id,
            )

            return ChatResponse(answer=result)
        
        if tool_call.tool == "close_ticket":
            ticket_id = int(tool_call.arguments["ticket_id"])

            ticket = await self.ticket_service.update_ticket_status(
                ticket_id=ticket_id,
                status=TicketStatus.CLOSED,
            )

            if ticket is None:
                result = "Тикет не найден."
            else:
                result = f"Тикет #{ticket.id} закрыт."

            await self.tool_call_repository.create(
                tool_name=tool_call.tool,
                arguments=tool_call.arguments,
                result=result,
                ticket_id=ticket_id,
            )

            return ChatResponse(answer=result)
        
    async def _choose_tool(self, message: str) -> ToolCall:
        native_tool_call = await self.llm_service.choose_tool(message)

        if native_tool_call is None:
            raise ValueError("LLM did not choose a tool")

        return ToolCall(
            tool=native_tool_call.name,
            arguments=native_tool_call.arguments,
        )
    