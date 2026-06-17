from app.models.ticket import Ticket
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ai import TicketAnalysisRequest
from app.schemas.ticket import TicketCreate, TicketStatus

from app.services.llm_service import LLMService

class TicketService:
    def __init__(self, repository: TicketRepository) -> None:
        self.repository = repository

    async def create_ticket(self, data: TicketCreate) -> Ticket:
        return await self.repository.create(data)

    async def list_tickets(self) -> list[Ticket]:
        return await self.repository.list_all()
    
    async def update_ticket_status(
        self,
        ticket_id: int,
        status: TicketStatus,
    ) -> Ticket | None:
        ticket = await self.repository.get_by_id(ticket_id)

        if ticket is None:
            return None

        return await self.repository.update_status(ticket, status)
    
    async def delete_ticket(self, ticket_id: int) -> bool:
        ticket = await self.repository.get_by_id(ticket_id)

        if ticket is None:
            return False

        await self.repository.delete(ticket)
        return True
    
    async def analyze_ticket(
        self,
        ticket_id: int,
        llm_service: LLMService,
    ) -> Ticket | None:
        ticket = await self.repository.get_by_id(ticket_id)

        if ticket is None:
            return None
        
        if ticket.ai_summary is not None:
            return ticket

        analysis = await llm_service.analyze_ticket(
            TicketAnalysisRequest(
                title=ticket.title,
                description=ticket.description,
            )
        )

        return await self.repository.save_analysis(
            ticket=ticket,
            analysis=analysis,
        )
    