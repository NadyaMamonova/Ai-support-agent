from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import TicketCreate, TicketRead
from app.services.ticket_service import TicketService

router = APIRouter()


def get_ticket_service(
    session: AsyncSession = Depends(get_db_session),
) -> TicketService:
    repository = TicketRepository(session)
    return TicketService(repository)


@router.post(
    "",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_ticket(
    data: TicketCreate,
    service: TicketService = Depends(get_ticket_service),
) -> TicketRead:
    return await service.create_ticket(data)


@router.get("", response_model=list[TicketRead])
async def list_tickets(
    service: TicketService = Depends(get_ticket_service),
) -> list[TicketRead]:
    return await service.list_tickets()