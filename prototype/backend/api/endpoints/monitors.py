import json
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from services.monitor_manager import monitor_manager

from .websocket import manager

logger = logging.getLogger(__name__)

router = APIRouter()


class MonitorUpdateRequest(BaseModel):
    visible: Optional[bool] = None
    content: Optional[str] = None
    playback_speed: Optional[float] = Field(None, alias="playbackSpeed")
    volume: Optional[float] = None


@router.get("/monitors")
async def list_monitors():
    """Return state of all monitors."""
    return monitor_manager.list_states()


@router.get("/monitors/{monitor_id}")
async def get_monitor(monitor_id: str):
    state = monitor_manager.get_state(monitor_id)
    if not state:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return state


@router.put("/monitors/{monitor_id}")
async def update_monitor(monitor_id: str, request: MonitorUpdateRequest):
    try:
        state = monitor_manager.update_state(
            monitor_id,
            visible=request.visible,
            content=request.content,
            playback_speed=request.playback_speed,
            volume=request.volume,
        )
    except ValueError as e:
        logger.error("Monitor update failed: %s", e)
        raise HTTPException(status_code=400, detail=str(e))

    await manager.broadcast(
        json.dumps(
            {
                "type": "director-state",
                "payload": {"videoScreens": monitor_manager.list_states()},
            }
        )
    )
    return state
