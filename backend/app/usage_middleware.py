"""
Middleware for usage tracking and limit enforcement
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import time

from database import get_db
from auth_models import User, UsageLog
from subscription_routes import check_usage_limit, increment_usage


class UsageTrackingMiddleware:
    """Middleware to track API usage and enforce limits"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # Skip usage tracking for certain paths
        skip_paths = [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/auth/",
            "/subscription/plans"
        ]

        path = request.url.path
        should_skip = any(path.startswith(skip_path) for skip_path in skip_paths)

        if should_skip:
            await self.app(scope, receive, send)
            return

        # Track usage for protected endpoints
        start_time = time.time()
        user: Optional[User] = None
        action_type = None
        resource_id = None

        # Determine action type from path
        if "/analyze" in path:
            action_type = "section_analysis"
        elif "/memo" in path:
            action_type = "memo_generation"
        elif "/cases/search" in path:
            action_type = "case_search"
        elif path.startswith("/api/"):
            action_type = "api_call"

        # Only track if we have an action type
        if action_type and request.method in ["POST", "GET"]:
            # Try to get user from authorization header
            try:
                auth_header = request.headers.get("authorization", "")
                if auth_header.startswith("Bearer "):
                    token = auth_header.replace("Bearer ", "")

                    # Import here to avoid circular dependency
                    from auth_utils import decode_token

                    payload = decode_token(token)
                    if payload:
                        email = payload.get("sub")
                        if email:
                            # Get database session
                            db_gen = get_db()
                            db = next(db_gen)

                            try:
                                user = db.query(User).filter(User.email == email).first()

                                # Check usage limits before processing request
                                if user and not check_usage_limit(user, action_type, db):
                                    # Limit exceeded
                                    response = JSONResponse(
                                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                                        content={
                                            "detail": f"Usage limit exceeded for {action_type.replace('_', ' ')}. Please upgrade your subscription.",
                                            "action_type": action_type,
                                            "subscription_tier": user.subscription.tier.value if user.subscription else "free"
                                        }
                                    )
                                    await response(scope, receive, send)
                                    return
                            finally:
                                db.close()

            except Exception as e:
                # Don't block the request if tracking fails
                print(f"Usage tracking error: {e}")

        # Process the request
        status_code = 200

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        await self.app(scope, receive, send_wrapper)

        # Log usage after request completes
        if user and action_type:
            response_time = (time.time() - start_time) * 1000  # Convert to ms

            db_gen = get_db()
            db = next(db_gen)

            try:
                # Only increment if request was successful
                if 200 <= status_code < 300:
                    increment_usage(user, action_type, db)

                # Log the usage
                usage_log = UsageLog(
                    user_id=user.id,
                    action_type=action_type,
                    resource_id=resource_id,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent", ""),
                    status_code=status_code,
                    response_time_ms=response_time
                )
                db.add(usage_log)
                db.commit()
            except Exception as e:
                print(f"Error logging usage: {e}")
            finally:
                db.close()


def track_usage(action_type: str, resource_id: str = None):
    """
    Decorator to track usage for specific endpoints

    Usage:
        @router.post("/analyze")
        @track_usage("section_analysis")
        async def analyze_section(...)
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # The middleware handles the actual tracking
            # This decorator is just for clarity and future extensions
            return await func(*args, **kwargs)
        return wrapper
    return decorator
