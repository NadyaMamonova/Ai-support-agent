from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from app.models.ticket import TicketStatus


class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=10, max_length=2000)


class TicketRead(BaseModel):
    id: int
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TicketStatusUpdate(BaseModel):
    status: TicketStatus