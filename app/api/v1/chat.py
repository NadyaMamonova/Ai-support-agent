from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session
from app.repositories.ai_audit_log_repository import AIAuditLogRepository
from app.repositories.ticket_repository import TicketRepository
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent_service import AgentService
from app.services.llm_service import LLMService
from app.services.ticket_service import TicketService
from app.repositories.agent_tool_call_repository import AgentToolCallRepository

router = APIRouter()
llm_service = LLMService()


def get_agent_service(
    session: AsyncSession = Depends(get_db_session),
) -> AgentService:
    ticket_repository = TicketRepository(session)
    audit_log_repository = AIAuditLogRepository(session)

    tool_call_repository = AgentToolCallRepository(session)

    ticket_service = TicketService(
        ticket_repository,
        audit_log_repository,
    )

    return AgentService(
        ticket_service=ticket_service,
        llm_service=llm_service,
        tool_call_repository=tool_call_repository,
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    agent_service: AgentService = Depends(get_agent_service),
) -> ChatResponse:
    return await agent_service.handle_message(data)