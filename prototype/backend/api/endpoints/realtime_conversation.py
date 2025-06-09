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
        logger.info("WebSocket disconnected during chunk iteration")
        return
    except Exception as e:
        logger.error(f"Error during chunk iteration: {e}")
        return


@router.websocket("/real-time/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    try:
        logger.info("New real-time WebSocket connection attempt")
        await websocket.accept()
        logger.info("Real-time WebSocket connection accepted")
        
        service = RealtimeConversationService()
        connection_active = True
        
        try:
            async for audio in service.stream_conversation(_iter_chunks(websocket)):
                # 檢查連接是否仍然活躍
                if not connection_active:
                    logger.info("Connection no longer active, stopping audio stream")
                    break
                    
                try:
                    await websocket.send_bytes(audio)
                except WebSocketDisconnect:
                    logger.info("WebSocket disconnected during audio send")
                    connection_active = False
                    break
                except Exception as e:
                    logger.error(f"Error sending audio bytes: {e}")
                    connection_active = False
                    break
        except Exception as e:
            logger.error(f"Error in audio stream processing: {e}")
            connection_active = False
                
    except WebSocketDisconnect:
        logger.info("Real-time WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error in real-time WebSocket endpoint: {e}")
    finally:
        try:
            if websocket.client_state.name != "DISCONNECTED":
                await websocket.close()
        except Exception:
            pass
