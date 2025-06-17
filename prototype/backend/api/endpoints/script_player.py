import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.script_player import ScriptPlayer

logger = logging.getLogger(__name__)
router = APIRouter()
player = ScriptPlayer()


class PlayScriptRequest(BaseModel):
    script_name: str
    base_url: str = "http://localhost:8000/api"


@router.post("/play_script")
async def play_script(request: PlayScriptRequest):
    try:
        results = player.play(request.script_name, request.base_url)
        return {"results": results}
    except FileNotFoundError as exc:
        logger.error("Script not found: %s", exc)
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to play script: %s", exc)
        raise HTTPException(status_code=500, detail="Script execution failed")
