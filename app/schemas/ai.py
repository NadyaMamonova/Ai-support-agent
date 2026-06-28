from enum import StrEnum

from pydantic import BaseModel, Field


class TicketCategory(StrEnum):
    BILLING = "billing"
    DATABASE = "database"
    AUTH = "auth"
    INFRASTRUCTURE = "infrastructure"
    BUG = "bug"
    OTHER = "other"
    INVALID = "invalid"


class TicketPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketAnalysisRequest(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=10, max_length=2000)


class TicketAnalysisResponse(BaseModel):
    category: TicketCategory
    priority: TicketPriority
    summary: str
    suggested_resolution: list[str]


class TicketAnalysisResult(BaseModel):
    analysis: TicketAnalysisResponse
    prompt: str
    raw_response: str
    model: str