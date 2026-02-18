import asyncio
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from starlette.responses import HTMLResponse

from api.v1.request_models.screenshots import PhantomScreenshot
from api.v1.response_models.screenshots import ScreenshotTaskResponse
from api.v1.services.screenshot_generator import screenshot_service
from core.caching.in_redis import cache

router = APIRouter(tags=["Screenshots"])

PROJECT_ROOT = (
    Path(__file__).resolve().parents[3]
)


@router.post(
    "/phantom",
    response_model=ScreenshotTaskResponse,
    responses={200: {"content": {"image/jpeg": {}}}},
)
async def generate_phantom_screenshot(ctx: PhantomScreenshot) -> ScreenshotTaskResponse:
    task_id = f"phantom_{uuid.uuid4()}"
    try:
        asyncio.create_task(screenshot_service.render_screenshot(
            ctx.model_dump(),
            template_name="phantom_wallet.html",
            task_id=task_id
        ))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ScreenshotTaskResponse(status="OK", task_id=task_id)


@router.get(
    "/phantom",
    response_class=HTMLResponse,
    responses={200: {"content": {"image/jpeg": {}}}},
)
async def get_generation_page() -> HTMLResponse:
    HTML_PATH = PROJECT_ROOT / "statics" / "phantom.html"
    html_content = HTML_PATH.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content, status_code=200)


@router.get(
    "/result",
    response_class=Response
)
async def get_result(task_id: str):
    result = await cache.get(task_id, raw=True)
    if result is None:
        return None
    return Response(content=result, media_type="image/jpeg", headers={"Content-Disposition": 'inline; filename="phantom.jpg"'},)


@router.get(
    "",
    response_class=HTMLResponse,
    responses={200: {"content": {"image/jpeg": {}}}},
)
async def get_generation_page() -> HTMLResponse:
    HTML_PATH = PROJECT_ROOT / "statics" / "index.html"
    html_content = HTML_PATH.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content, status_code=200)
