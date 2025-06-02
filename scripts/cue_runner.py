import argparse
import asyncio
import json
from pathlib import Path

import websockets
import yaml


async def run_cues(path: Path, ws_url: str) -> None:
    with path.open() as f:
        cues = yaml.safe_load(f)
    start = asyncio.get_event_loop().time()
    async with websockets.connect(ws_url) as ws:
        for cue in cues:
            when = cue.get("time", 0)
            await asyncio.sleep(max(0, start + when - asyncio.get_event_loop().time()))
            await ws.send(json.dumps(cue.get("action", {})))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run cue sheet over WebSocket")
    parser.add_argument("file", type=Path, help="Path to YAML/JSON cue sheet")
    parser.add_argument("--ws", default="ws://localhost:8000/ws", help="WebSocket URL")
    args = parser.parse_args()
    asyncio.run(run_cues(args.file, args.ws))


if __name__ == "__main__":
    main()
