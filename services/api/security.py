"""
Security utilities including rate limiting, input validation, and CORS configuration.
"""
from fastapi import Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Optional
import time
import os
import re
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple in-memory rate limiter.

    For production, use Redis-backed rate limiting (e.g., slowapi or fastapi-limiter).
    """

    def __init__(self):
        self.requests = defaultdict(list)
        self.blocked_ips = {}

    def is_rate_limited(
        self,
        key: str,
        max_requests: int = 100,
        window_seconds: int = 60,
        block_duration: int = 300
    ) -> bool:
        """
        Check if a key (IP address or user ID) has exceeded rate limit.

        Args:
            key: Identifier (IP address or user ID)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            block_duration: How long to block after exceeding limit (seconds)

        Returns:
            True if rate limited, False otherwise
        """
        now = time.time()

        # Check if currently blocked
        if key in self.blocked_ips:
            block_until = self.blocked_ips[key]
            if now < block_until:
                logger.warning(f"Rate limit: {key} is blocked until {block_until}")
                return True
            else:
                # Block expired, remove it
                del self.blocked_ips[key]

        # Clean old requests outside the window
        cutoff = now - window_seconds
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > cutoff]

        # Check if over limit
        if len(self.requests[key]) >= max_requests:
            # Block this key
            self.blocked_ips[key] = now + block_duration
            logger.warning(f"Rate limit exceeded for {key}. Blocked for {block_duration}s")
            return True

        # Record this request
        self.requests[key].append(now)
        return False

    def get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""
        # Check for forwarded IP (behind proxy/load balancer)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # X-Forwarded-For can be a comma-separated list
            return forwarded.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct connection IP
        if request.client:
            return request.client.host

        return "unknown"


# Global rate limiter instance
rate_limiter = RateLimiter()


async def check_rate_limit(request: Request):
    """
    Dependency for rate limiting endpoints.

    Usage:
        @app.get("/endpoint", dependencies=[Depends(check_rate_limit)])
    """
    client_ip = rate_limiter.get_client_ip(request)

    # Different limits for different endpoints
    if request.url.path.startswith("/auth/login") or request.url.path.startswith("/auth/register"):
        # Stricter limits for auth endpoints (prevent brute force)
        max_requests = 5
        window_seconds = 60
    else:
        # General API limits
        max_requests = 100
        window_seconds = 60

    if rate_limiter.is_rate_limited(client_ip, max_requests, window_seconds):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )


class InputValidator:
    """Input validation and sanitization utilities."""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password strength.

        Returns:
            (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"

        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"

        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one number"

        # Optional: Check for special characters
        # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        #     return False, "Password must contain at least one special character"

        return True, None

    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """
        Sanitize string input.

        - Remove null bytes
        - Trim whitespace
        - Limit length
        """
        if not value:
            return ""

        # Remove null bytes
        value = value.replace('\x00', '')

        # Trim whitespace
        value = value.strip()

        # Limit length
        if len(value) > max_length:
            value = value[:max_length]

        return value

    @staticmethod
    def validate_repo_url(url: str) -> bool:
        """
        Validate repository URL.

        Only allow GitHub, GitLab, Bitbucket URLs.
        """
        if not url:
            return True  # Optional field

        allowed_patterns = [
            r'^https://github\.com/[\w-]+/[\w-]+(?:\.git)?$',
            r'^https://gitlab\.com/[\w-]+/[\w-]+(?:\.git)?$',
            r'^https://bitbucket\.org/[\w-]+/[\w-]+(?:\.git)?$',
        ]

        for pattern in allowed_patterns:
            if re.match(pattern, url):
                return True

        return False

    @staticmethod
    def validate_path(path: str) -> bool:
        """
        Validate file path to prevent path traversal attacks.

        Blocks: .., absolute paths, null bytes
        """
        if not path:
            return False

        # Check for null bytes
        if '\x00' in path:
            return False

        # Check for path traversal
        if '..' in path:
            return False

        # Check for absolute paths (should be relative)
        if path.startswith('/'):
            return False

        return True


def setup_cors(app, allowed_origins: Optional[list] = None):
    """
    Setup CORS middleware with secure defaults.

    Args:
        app: FastAPI application
        allowed_origins: List of allowed origins (default: from environment)
    """
    # Get allowed origins from environment or use defaults
    if allowed_origins is None:
        origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
        allowed_origins = [origin.strip() for origin in origins_str.split(",")]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
        max_age=3600,  # Cache preflight requests for 1 hour
    )

    logger.info(f"CORS enabled for origins: {allowed_origins}")


def get_secret_key() -> str:
    """
    Get secret key from environment variable with validation.

    Raises:
        ValueError: If SECRET_KEY is not set or is insecure
    """
    secret_key = os.getenv("SECRET_KEY")

    if not secret_key:
        raise ValueError(
            "SECRET_KEY environment variable is not set. "
            "Generate a secure key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
        )

    # Validate minimum length
    if len(secret_key) < 32:
        raise ValueError(
            "SECRET_KEY must be at least 32 characters long. "
            "Generate a secure key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
        )

    # Warn about common insecure values
    insecure_values = [
        "your-secret-key-change-this-in-production",
        "secret",
        "password",
        "12345678",
        "changeme"
    ]

    if secret_key.lower() in insecure_values:
        raise ValueError(
            "SECRET_KEY is set to an insecure default value. "
            "Generate a secure key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
        )

    return secret_key


class SecurityHeaders:
    """Add security headers to responses."""

    @staticmethod
    async def add_security_headers(request: Request, call_next):
        """Middleware to add security headers."""
        response = await call_next(request)

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # XSS protection (legacy but doesn't hurt)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy (adjust as needed)
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"

        # HSTS (only enable if using HTTPS)
        if os.getenv("ENABLE_HSTS", "false").lower() == "true":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
