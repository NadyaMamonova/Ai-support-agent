import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_tool_call import AgentToolCall


class AgentToolCallRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        result: str,
        ticket_id: int | None = None,
    ) -> AgentToolCall:
        tool_call = AgentToolCall(
            ticket_id=ticket_id,
            tool_name=tool_name,
            arguments=json.dumps(arguments, ensure_ascii=False),
            result=result,
        )

        self.session.add(tool_call)
        await self.session.commit()
        await self.session.refresh(tool_call)

        return tool_call