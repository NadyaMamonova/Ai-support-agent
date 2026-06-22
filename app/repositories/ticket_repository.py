from sqlalchemy import select
from datetime import datetime, timezone
from app.schemas.ai import TicketAnalysisResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketStatus


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
    
    async def update_status(
        self,
        ticket: Ticket,
        status: TicketStatus,
    ) -> Ticket:
        ticket.status = status

        await self.session.commit()
        await self.session.refresh(ticket)

        return ticket
    
    async def get_by_id(self, ticket_id: int) -> Ticket | None:
        result = await self.session.execute(
            select(Ticket).where(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()
    
    async def delete(self, ticket: Ticket) -> None:
        await self.session.delete(ticket)
        await self.session.commit()


    async def save_analysis(
        self,
        ticket: Ticket,
        analysis: TicketAnalysisResponse,
    ) -> Ticket:
        ticket.ai_category = analysis.category
        ticket.ai_priority = analysis.priority
        ticket.ai_summary = analysis.summary
        ticket.analyzed_at = datetime.now(timezone.utc)
        ticket.ai_suggested_resolution = analysis.suggested_resolution

        await self.session.commit()
        await self.session.refresh(ticket)

        return ticket