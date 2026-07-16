from typing import Any

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ToolCall(BaseModel):
    tool: str
    arguments: dict[str, Any]


class ChatResponse(BaseModel):
    answer: str


class NativeToolCall(BaseModel):
    name: str
    arguments: dict[str, Any]