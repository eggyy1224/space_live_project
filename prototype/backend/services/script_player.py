import json
import logging
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ScriptPlayer:
    """Playback system for JSON-based scripts."""

    def __init__(self, script_dir: Optional[str] = None) -> None:
        self.script_dir = script_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "json_scripts"
        )

    def _load_script(self, script_name: str) -> Dict[str, Any]:
        path = os.path.join(self.script_dir, f"{script_name}.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Script '{script_name}' not found at {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def play(self, script_name: str, base_url: str) -> List[Dict[str, Any]]:
        script = self._load_script(script_name)
        actions = script.get("actions", [])
        results: List[Dict[str, Any]] = []

        for index, action in enumerate(actions):
            method = action.get("method", "GET").upper()
            url = action.get("url", "").replace("{base_url}", base_url)
            headers = action.get("headers") or {}
            body = action.get("body")
            delay = action.get("delay")

            logger.info("Executing action %s %s", method, url)
            data = json.dumps(body).encode("utf-8") if body is not None else None
            request = urllib.request.Request(url, data=data, method=method)
            for k, v in headers.items():
                request.add_header(k, v)
            try:
                with urllib.request.urlopen(request) as resp:
                    resp_body = resp.read().decode()
                    result = {
                        "index": index,
                        "status_code": resp.getcode(),
                        "body": resp_body,
                    }
            except urllib.error.URLError as exc:
                logger.error("Action %s failed: %s", index, exc)
                result = {"index": index, "error": str(exc)}
            results.append(result)

            if delay:
                time.sleep(float(delay))

        return results
