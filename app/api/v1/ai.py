from fastapi import APIRouter, HTTPException

from app.schemas.ai import TicketAnalysisRequest, TicketAnalysisResponse
from app.services.llm_service import LLMService

router = APIRouter()
llm_service = LLMService()


@router.post("/ticket-analysis", response_model=TicketAnalysisResponse)
async def analyze_ticket(
    data: TicketAnalysisRequest,
) -> TicketAnalysisResponse:
    try:
        return await llm_service.analyze_ticket(data)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM provider error: {exc}",
        ) from exc