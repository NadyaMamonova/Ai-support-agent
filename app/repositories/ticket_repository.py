from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate


class TicketRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: TicketCreate) -> Ticket:
        ticket = Ticket(
            title=data.title,
            description=data.description,
        )

        self.session.add(ticket)
        await self.session.commit()
        await self.session.refresh(ticket)

        return ticket

    async def list_all(self) -> list[Ticket]:
        result = await self.session.execute(
            select(Ticket).order_by(Ticket.id)
        )
        return list(result.scalars().all())