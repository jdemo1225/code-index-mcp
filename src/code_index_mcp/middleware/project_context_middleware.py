"""
Project Context Middleware - Extract project path from HTTP header.

This middleware reads the `Mcp-Project-Path` header from incoming requests
and sets the request context for per-project index manager isolation.
"""

from __future__ import annotations

import logging

from ..request_context import reset_request_project_path, set_request_project_path

logger = logging.getLogger(__name__)


class ProjectContextMiddleware:
    """Middleware to extract and set project context from HTTP headers.

    The proxy sends the project path via the `Mcp-Project-Path` header,
    allowing this middleware to set the request-scoped context before
    the request is processed.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract project path from header (case-insensitive)
        project_path = None
        for name, value in scope.get("headers", []):
            if name.decode("utf-8").lower() == "mcp-project-path":
                project_path = value.decode("utf-8")
                break

        if project_path:
            logger.debug(f"[Middleware] Project path from header: {project_path}")

        token = set_request_project_path(project_path)

        try:
            await self.app(scope, receive, send)
        finally:
            # Restore any previous context after request completes
            reset_request_project_path(token)
