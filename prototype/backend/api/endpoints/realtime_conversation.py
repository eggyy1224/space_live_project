import json
import logging
from typing import AsyncIterator

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.realtime_conversation import RealtimeConversationService

router = APIRouter()
logger = logging.getLogger(__name__)


async def _iter_chunks(websocket: WebSocket) -> AsyncIterator[bytes]:
    """Yield binary chunks received from the websocket."""
    try:
        while True:
            chunk = await websocket.receive_bytes()
            yield chunk
    except WebSocketDisconnect:
        return


@router.websocket("/real-time/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    service = RealtimeConversationService()
    async for audio in service.stream_conversation(_iter_chunks(websocket)):
        await websocket.send_bytes(audio)
