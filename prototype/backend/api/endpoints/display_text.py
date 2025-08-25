"""Simple endpoint for storing and retrieving display text."""

from typing import Dict

from fastapi import APIRouter
from pydantic import BaseModel


class TextPayload(BaseModel):
    """Request/response model for text content."""

    text: str = ""


router = APIRouter()

_text_store = TextPayload()


@router.get("/display_text", response_model=TextPayload)
async def get_display_text() -> TextPayload:
    """Return the currently stored text."""

    return _text_store


@router.post("/display_text")
async def set_display_text(payload: TextPayload) -> Dict[str, bool]:
    """Update the stored text."""

    _text_store.text = payload.text
    return {"success": True}
