import base64
import os
from io import BytesIO
from pathlib import Path

from PIL import Image
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright, Browser, BrowserContext, Playwright

BASE_DIR = Path(__file__).parent.parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"

env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


def image_to_data_uri(path: str) -> str:
    data = Path(path).read_bytes()
    b64 = base64.b64encode(data).decode()
    ext = Path(path).suffix.lstrip(".")
    return f"data:image/{ext};base64,{b64}"


def render_html(ctx: dict, template_name: str) -> str:
    return env.get_template(template_name).render(**ctx)


class ScreenshotService:
    def __init__(self):
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    async def start(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            executable_path=os.getenv("CHROMIUM_PATH", None),  # alpine: /usr/bin/chromium-browser
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--single-process",          # важно для alpine/docker
                "--no-zygote",
            ],
        )
        self._context = await self._browser.new_context(
            viewport={"width": 393, "height": 852},
            device_scale_factor=2,
        )

    async def stop(self):
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def render_screenshot(self, ctx: dict, template_name: str) -> bytes:
        html = render_html(ctx, template_name)
        page = await self._context.new_page()
        try:
            await page.set_content(html, wait_until="networkidle")
            png_bytes = await page.screenshot(full_page=False)
        finally:
            await page.close()

        img = Image.open(BytesIO(png_bytes)).convert("RGB")
        buf = BytesIO()
        img.save(buf, "JPEG", quality=95)
        return buf.getvalue()


screenshot_service = ScreenshotService()
