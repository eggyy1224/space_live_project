from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from config.video_resources import is_video_file_valid
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class MonitorState(BaseModel):
    id: str
    currentVideo: str = ""
    visible: bool = False
    playing: bool = False
    volume: float = 1.0
    currentTime: float = 0.0
    duration: float = 0.0
    playbackRate: float = 1.0


class MonitorManager:
    """Manage state of frontend monitors."""

    def __init__(self) -> None:
        self.monitors: Dict[str, MonitorState] = {
            f"screen{i}": MonitorState(id=f"screen{i}") for i in range(1, 4)
        }

    def get_state(self, monitor_id: str) -> Optional[MonitorState]:
        return self.monitors.get(monitor_id)

    def list_states(self) -> List[Dict[str, Any]]:
        return [state.dict() for state in self.monitors.values()]

    def update_state(
        self,
        monitor_id: str,
        *,
        visible: Optional[bool] = None,
        content: Optional[str] = None,
        playback_speed: Optional[float] = None,
        volume: Optional[float] = None,
    ) -> MonitorState:
        if monitor_id not in self.monitors:
            raise ValueError("Invalid monitor id")

        state = self.monitors[monitor_id]

        if content is not None:
            if not is_video_file_valid(content):
                raise ValueError(f"Unknown content id: {content}")
            state.currentVideo = content
            state.playing = True
            state.visible = True
            state.currentTime = 0.0

        if visible is not None:
            state.visible = visible
            if not visible:
                state.playing = False

        if playback_speed is not None:
            if not 0.25 <= playback_speed <= 4.0:
                raise ValueError("playback speed must be between 0.25 and 4.0")
            state.playbackRate = playback_speed

        if volume is not None:
            if not 0.0 <= volume <= 1.0:
                raise ValueError("volume must be between 0.0 and 1.0")
            state.volume = volume

        logger.info("Monitor %s updated: %s", monitor_id, state.json())
        return state


monitor_manager = MonitorManager()
