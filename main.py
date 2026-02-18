from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import api
from api.v1.services.screenshot_generator import screenshot_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    await screenshot_service.start()
    yield
    await screenshot_service.stop()


def register_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        title="Screenshot Generator API",
        version="0.0.1",
        description="API for generating screenshots",
        docs_url="/api/docs",
        redoc_url=None,
        openapi_url="/api/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api.router, prefix="/api")

    return app


app = register_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
