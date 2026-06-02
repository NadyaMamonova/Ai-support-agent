from app.schemas.ticket import TicketCreate, TicketRead


class TicketService:
    def __init__(self) -> None:
        self._tickets: list[TicketRead] = []
        self._next_id = 1

    def create_ticket(self, data: TicketCreate) -> TicketRead:
        ticket = TicketRead(
            id=self._next_id,
            title=data.title,
            description=data.description,
            status="open",
        )
        self._tickets.append(ticket)
        self._next_id += 1
        return ticket

    def list_tickets(self) -> list[TicketRead]:
        return self._tickets