from app.models.ticket import Ticket
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import TicketCreate


class TicketService:
    def __init__(self, repository: TicketRepository) -> None:
        self.repository = repository

    async def create_ticket(self, data: TicketCreate) -> Ticket:
        return await self.repository.create(data)

    async def list_tickets(self) -> list[Ticket]:
        return await self.repository.list_all()