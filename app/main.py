from fastapi import FastAPI

from app.api.v1.health import router as health_router
from app.api.v1.tickets import router as tickets_router

app = FastAPI(
    title="AI Ops Desk API",
    version="0.1.0",
)

app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(tickets_router, prefix="/api/v1/tickets", tags=["tickets"])