import logging
import time
from collections import defaultdict

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("security")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.rpm = requests_per_minute
        self._hits: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        hits = self._hits[client_ip]
        self._hits[client_ip] = [t for t in hits if t > now - 60]
        self._hits[client_ip].append(now)

        if len(self._hits[client_ip]) > self.rpm:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Забагато запитів. Спробуйте пізніше."},
                headers={"Retry-After": "60"},
            )
        return await call_next(request)


class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response: Response = await call_next(request)
        elapsed_ms = round((time.time() - start) * 1000, 1)

        if response.status_code >= 400:
            client_ip = request.client.host if request.client else "-"
            logger.info(
                "%s %s -> %s (%sms) ip=%s",
                request.method, request.url.path,
                response.status_code, elapsed_ms, client_ip,
            )
        return response
