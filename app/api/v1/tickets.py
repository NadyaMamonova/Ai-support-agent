from fastapi import APIRouter, status

from app.schemas.ticket import TicketCreate, TicketRead
from app.services.ticket_service import TicketService

router = APIRouter()
ticket_service = TicketService()


@router.post(
    "",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_ticket(data: TicketCreate) -> TicketRead:
    return ticket_service.create_ticket(data)


@router.get("", response_model=list[TicketRead])
async def list_tickets() -> list[TicketRead]:
    return ticket_service.list_tickets()