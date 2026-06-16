from pydantic import BaseModel, Field


class TicketAnalysisRequest(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=10, max_length=2000)


class TicketAnalysisResponse(BaseModel):
    category: str
    priority: str
    summary: str