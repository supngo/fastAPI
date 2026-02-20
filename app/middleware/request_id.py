import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app.request")

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        logger.info(
            "request_started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
            },
        )

        response = await call_next(request)

        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
            },
        )

        response.headers["X-Request-ID"] = request_id
        return response
