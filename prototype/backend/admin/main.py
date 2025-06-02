import os

from fastapi import APIRouter, FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = os.path.dirname(__file__)
router = APIRouter(include_in_schema=False)


@router.get("/admin")
async def admin_page() -> HTMLResponse:
    """Return the admin interface with Swagger UI and console."""
    html_path = os.path.join(BASE_DIR, "templates", "admin.html")
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)


def setup_admin(app: FastAPI) -> None:
    """Mount static files and include the admin route."""
    static_dir = os.path.join(BASE_DIR, "static")
    app.mount("/admin-static", StaticFiles(directory=static_dir), name="admin-static")
    app.include_router(router)
