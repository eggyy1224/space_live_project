import asyncio
import importlib.util
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

spec = importlib.util.spec_from_file_location(
    "script_player",
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "services", "script_player.py")
    ),
)
script_player = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script_player)
ScriptPlayer = script_player.ScriptPlayer


class SimpleHandler(BaseHTTPRequestHandler):
    def _respond(self) -> None:
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"{}")

    def do_POST(self) -> None:  # noqa: D401
        self._respond()

    def do_PUT(self) -> None:  # noqa: D401
        self._respond()

    def log_message(self, format, *args):  # noqa: D401, ANN001
        return


def start_server() -> tuple[HTTPServer, threading.Thread, int]:
    server = HTTPServer(("localhost", 0), SimpleHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server, thread, port


def stop_server(server: HTTPServer, thread: threading.Thread) -> None:
    server.shutdown()
    thread.join()


def test_script_player_runs() -> None:
    server, thread, port = start_server()
    try:
        player = ScriptPlayer(script_dir="prototype/backend/json_scripts")
        results = player.play("meta_self", f"http://localhost:{port}")
        assert results
        assert all(r.get("status_code") == 200 for r in results)
    finally:
        stop_server(server, thread)
