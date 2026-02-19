import asyncio
import datetime
import random
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from starlette.responses import HTMLResponse

from api.v1.request_models.screenshots import PhantomScreenshot
from api.v1.response_models.screenshots import ScreenshotTaskResponse
from api.v1.services.crypto_rates import get_crypto_price
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
    context = ctx.model_dump()
    rate = await get_crypto_price(
        "SOL", "usd"
    )
    context["solana_amount_usdt"] = round(random.uniform(500, 3000), 2)
    context["solana_amount"] = f"{round(context["solana_amount_usdt"] / rate["price"], 2):.2f}"
    context["solana_amount_change"] = round(random.uniform(0.01, 2) * random.choice([-1, 1]), 2)
    context["usdt_amount_change"] = round(random.uniform(0.01, 0.05) * random.choice([-1, 1]), 2)
    context["current_time"] = datetime.datetime.utcnow().strftime("%H:%M")
    context["token_amount_usd"] = round(ctx.token_amount * ctx.usd_price_per_token, 2)
    context["token_change"] = round(random.uniform(0.01, 1) * random.choice([-1, 1]), 2)
    context["total_diff"] = context["solana_amount_change"] + context["usdt_amount_change"] + context["token_change"]
    context["total"] = context["solana_amount_usdt"] + context["usdt_amount"] + context["token_amount_usd"]
    context["total_diff_percent"] = f'{round(context["total_diff"] / context["total"] * 100, 2):.2f}'
    context["token_change"] = f'{context["token_change"]:.2f}'
    context["solana_amount_change"] = f'{context["solana_amount_change"]:.2f}'
    context["usdt_amount_change"] = f'{context["usdt_amount_change"]:.2f}'
    context["solana_amount_usdt"] = f"{round(random.uniform(500, 3000), 2):.2f}"
    context["token_amount"] = f"{ctx.token_amount:.2f}"
    context["usdt_amount"] = f"{ctx.usdt_amount:.2f}"
    context["token_amount_usd"] = f"{context["token_amount_usd"]:.2f}"
    context["total_diff"] = f'{context["total_diff"]:.2f}'
    context["total"] = f'{context["total"]:.2f}'
    try:
        asyncio.create_task(screenshot_service.render_screenshot(
            context,
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
