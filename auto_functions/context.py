from typing import overload
from uuid import uuid4

from starlette.datastructures import Headers, MutableHeaders
from structlog.contextvars import bind_contextvars, clear_contextvars, get_contextvars


def bind_context_from_headers(headers: Headers) -> None:
    """Bind Structlog context vars from request headers"""
    request_id = headers.get("X-Auto-Functions-Request-Id", str(uuid4()))
    clear_contextvars()
    bind_contextvars(request_id=request_id)


@overload
def set_headers_from_context(headers: MutableHeaders) -> MutableHeaders:
    """Add context headers to a response"""


@overload
def set_headers_from_context(headers: dict[str, str]) -> dict[str, str]:
    """Add context headers to a dictionary of response headers"""


def set_headers_from_context(headers: MutableHeaders | dict[str, str]) -> MutableHeaders | dict[str, str]:
    """Add context headers to a response or dictionary"""
    contextvars = get_contextvars()
    if "request_id" in contextvars:
        headers["X-Auto-Functions-Request-Id"] = contextvars["request_id"]

    return headers
