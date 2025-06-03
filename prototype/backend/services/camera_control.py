from typing import Dict, Optional


class CameraControlService:
    """Service to manage camera presets for API control."""

    def __init__(self) -> None:
        self._presets: Dict[str, Dict[str, float]] = {}

    def save_preset(
        self, name: str, pitch: float, yaw: float, roll: float, fov: Optional[float] = None
    ) -> None:
        self._presets[name] = {
            "pitch": pitch,
            "yaw": yaw,
            "roll": roll,
        }
        if fov is not None:
            self._presets[name]["fov"] = fov

    def get_preset(self, name: str) -> Optional[Dict[str, float]]:
        return self._presets.get(name)

    def list_presets(self) -> Dict[str, Dict[str, float]]:
        return self._presets
