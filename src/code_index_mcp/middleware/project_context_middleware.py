"""
Project Context Middleware - Extract project path from HTTP header.

This middleware reads the `Mcp-Project-Path` header from incoming requests
and sets the request context for per-project index manager isolation.
"""

from __future__ import annotations

import logging
from starlette.datastructures import Headers
from starlette.types import ASGIApp, Receive, Scope, Send

from ..request_context import reset_request_project_path, set_request_project_path

logger = logging.getLogger(__name__)


class ProjectContextMiddleware:
    """Middleware to extract and set project context from HTTP headers.

    The proxy sends the project path via the `Mcp-Project-Path` header,
    allowing this middleware to set the request-scoped context before
    the request is processed.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            headers = Headers(scope=scope)
            project_path = headers.get("mcp-project-path")

            if project_path:
                logger.debug("[Middleware] Project path from header: %s", project_path)

            token = set_request_project_path(project_path)

            try:
                await self.app(scope, receive, send)
            finally:
                reset_request_project_path(token)
        else:
            await self.app(scope, receive, send)
