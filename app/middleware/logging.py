import time
import uuid
import typing
from fastapi import Request, Response
from loguru import logger


async def log_requests(
    request: Request, call_next: typing.Callable[[Request], typing.Awaitable[Response]]
) -> Response:
    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Store request_id in request state for access in endpoints if needed
    request.state.request_id = request_id

    response = await call_next(request)

    process_time = time.time() - start_time

    logger.info(
        "Request processed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "latency_ms": round(process_time * 1000, 2),
        },
    )

    response.headers["X-Request-ID"] = request_id
    return response
