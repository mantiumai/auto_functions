import time
from http import HTTPStatus
from typing import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from auto_functions.context import bind_context_from_headers, set_headers_from_context
from auto_functions.logger import get_logger
from auto_functions.routes.api_specs.api_specs import api_spec_router

app = FastAPI(
    title="Auto Functions API",
    description="Use OpenAPI specs to automatically generate OpenAI function tool parameters",
    version="0.1.0",
)

app.include_router(api_spec_router)

# TODO: Initialize telemetry and segment and JWT validation
# TODO: Connect to metadata database
# TODO: Configure OAuth

# TODO: Disconnect from metadata database

# Add CORS middleware
cors_kwargs = dict(
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Mantium-Request-Id", "X-Mantium-Debug-Logging"],
)

app.add_middleware(CORSMiddleware, **cors_kwargs)


# Add logging and exception handling middleware
async def log_request(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """Log a request"""
    user_agent = request.headers.get("user-agent", "UNKNOWN")

    bind_context_from_headers(request.headers)
    log = get_logger().bind(
        user_agent=user_agent,
        method=request.method,
        url=str(request.url),
        host=request.client.host if request.client else "UNKNOWN",
    )

    # Skip logging if it's a health check or the user-agent matches our exclusion list
    skip_request_logging = str(request.url).endswith("health-check") or any(
        s for s in ["kube-probe", "tilt-probe"] if s in user_agent
    )

    if not skip_request_logging:
        await log.adebug("Request starting")

    start_time = time.perf_counter()
    try:
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        if not skip_request_logging:
            await log.ainfo("Request completed", status_code=response.status_code, duration_seconds=process_time)
        set_headers_from_context(response.headers)
    except Exception:
        process_time = time.perf_counter() - start_time
        await log.ainfo("Request failed", duration_seconds=process_time)
        raise

    return response


app.add_middleware(BaseHTTPMiddleware, dispatch=log_request)


# Add standard routes
def health_check() -> str:
    """Verify that the app is running."""
    return "OK"


app.get("/health-check", summary="Verify that the service is running", status_code=HTTPStatus.OK)(health_check)
