from app.models.ticket import Ticket
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import TicketCreate, TicketStatus


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
    