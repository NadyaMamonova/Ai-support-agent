from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import TicketCreate, TicketRead, TicketStatusUpdate
from app.services.llm_service import LLMService
from app.services.ticket_service import TicketService

router = APIRouter()
llm_service = LLMService()


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


@router.post("/{ticket_id}/analyze", response_model=TicketRead)
async def analyze_existing_ticket(
    ticket_id: int,
    service: TicketService = Depends(get_ticket_service),
) -> TicketRead:
    ticket = await service.analyze_ticket(
        ticket_id=ticket_id,
        llm_service=llm_service,
    )

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@router.patch("/{ticket_id}/status", response_model=TicketRead)
async def update_ticket_status(
    ticket_id: int,
    data: TicketStatusUpdate,
    service: TicketService = Depends(get_ticket_service),
) -> TicketRead:
    ticket = await service.update_ticket_status(
        ticket_id=ticket_id,
        status=data.status,
    )

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@router.get("/{ticket_id}", response_model=TicketRead)
async def get_ticket(
    ticket_id: int,
    service: TicketService = Depends(get_ticket_service),
) -> TicketRead:
    ticket = await service.get_ticket_by_id(ticket_id)

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: int,
    service: TicketService = Depends(get_ticket_service),
) -> Response:
    deleted = await service.delete_ticket(ticket_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)