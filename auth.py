"""Authentication helpers for admin-protected endpoints."""

import os
from functools import wraps
from typing import Any

from flask import jsonify, request

from logger_config import logger


def require_admin_token(f):
    """Decorator that gates an endpoint behind a Bearer token check.

    Compares the ``Authorization: Bearer <token>`` header value against
    the ``ADMIN_TOKEN`` environment variable.  Returns 401 if the token
    is missing, empty, or does not match.
    """

    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        admin_token = os.environ.get("ADMIN_TOKEN", "").strip()
        if not admin_token:
            logger.warning(
                "Admin endpoint '%s' accessed but ADMIN_TOKEN is not configured.",
                request.path,
            )
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": "Admin access is not configured on this server.",
                        "error_code": "ADMIN_NOT_CONFIGURED",
                    }
                ),
                401,
            )

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            logger.warning(
                "Unauthorized access attempt on '%s' — missing or malformed Authorization header.",
                request.path,
            )
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": "Authentication required.",
                        "error_code": "AUTH_REQUIRED",
                    }
                ),
                401,
            )

        token = auth_header[len("Bearer "):]
        if token != admin_token:
            logger.warning(
                "Unauthorized access attempt on '%s' — invalid token.",
                request.path,
            )
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": "Invalid authentication token.",
                        "error_code": "INVALID_TOKEN",
                    }
                ),
                401,
            )

        return f(*args, **kwargs)

    return decorated
