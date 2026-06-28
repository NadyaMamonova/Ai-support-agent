from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_audit_log import AIAuditLog


class AIAuditLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        ticket_id: int,
        model: str,
        prompt: str,
        response: str,
    ) -> AIAuditLog:
        log = AIAuditLog(
            ticket_id=ticket_id,
            model=model,
            prompt=prompt,
            response=response,
        )

        self.session.add(log)
        await self.session.commit()
        await self.session.refresh(log)

        return log