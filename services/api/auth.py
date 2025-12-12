"""
Authentication utilities for JWT and API key authentication.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import secrets

from services.api.database import get_db
from services.api import models

# Security configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_api_key() -> str:
    """Generate a secure API key."""
    return f"sk-{secrets.token_urlsafe(32)}"


def authenticate_user(email: str, password: str, db: Session) -> Optional[models.User]:
    """Authenticate a user by email and password."""
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    return user


def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[models.User]:
    """Get current user from JWT token or API key, returns None if not authenticated."""
    if not authorization:
        return None

    # Try JWT token first
    if authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        payload = decode_access_token(token)
        if payload:
            user_id = payload.get("sub")
            if user_id:
                user = db.query(models.User).filter(models.User.id == user_id).first()
                if user and user.is_active:
                    user.last_login = datetime.utcnow()
                    db.commit()
                    return user

    # Try API key
    api_key = db.query(models.APIKey).filter(
        models.APIKey.key == authorization,
        models.APIKey.is_active == True
    ).first()

    if api_key:
        # Update last used
        api_key.last_used_at = datetime.utcnow()
        db.commit()

        user = db.query(models.User).filter(models.User.id == api_key.user_id).first()
        if user and user.is_active:
            return user

    return None


def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(required_roles: list[str]):
    """Dependency to require specific roles."""
    def role_checker(current_user: models.User = Depends(get_current_user)) -> models.User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {required_roles}"
            )
        return current_user
    return role_checker


def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    """Dependency to require admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def check_project_access(
    project_id: int,
    user: models.User,
    db: Session,
    required_permission: str = "read"
) -> bool:
    """
    Check if user has access to a project.

    Args:
        project_id: Project ID to check
        user: User to check access for
        db: Database session
        required_permission: Permission level required (read, write, admin)

    Returns:
        True if user has access, raises HTTPException otherwise
    """
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Admin has access to everything
    if user.role == "admin":
        return True

    # Owner has full access
    if project.owner_id == user.id:
        return True

    # Check team access
    if project.team_id:
        team_member = db.query(models.TeamMember).filter(
            models.TeamMember.team_id == project.team_id,
            models.TeamMember.user_id == user.id
        ).first()

        if team_member:
            # Team leads and owners have full access
            if team_member.role in ["lead", "owner"]:
                return True
            # Regular members have read/write access
            if required_permission in ["read", "write"]:
                return True

    # Check visibility
    if project.visibility == "public" and required_permission == "read":
        return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have access to this project"
    )
