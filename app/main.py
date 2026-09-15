import logging
import time
import uuid

from fastapi import FastAPI
from fastapi import Request

from app.api.routes import router as api_router
from app.core.config import get_settings
from app.core.logging import configure_logging


settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(api_router)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    started = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Request-ID"] = request_id
    logging.getLogger("app.requests").info(
        "%s %s -> %s (%.1f ms) request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
        request_id,
    )
    return response
