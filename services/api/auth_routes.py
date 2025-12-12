"""
Authentication and authorization routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta

from services.api.database import get_db
from services.api import models
from services.api.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    generate_api_key,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["authentication"])


# Pydantic schemas
class UserRegister(BaseModel):
    email: EmailStr
    name: str
    password: str
    department: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str
    name: str
    role: str


class APIKeyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    expires_in_days: Optional[int] = None


class APIKeyResponse(BaseModel):
    id: int
    key: str
    name: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: str
    expires_at: Optional[str]

    class Config:
        from_attributes = True


@router.post("/register", response_model=Token)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = models.User(
        email=user_data.email,
        name=user_data.name,
        password_hash=hashed_password,
        department=user_data.department,
        role="developer"  # Default role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create access token
    access_token = create_access_token(
        data={"sub": new_user.id, "email": new_user.email, "role": new_user.role}
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        role=new_user.role
    )


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password."""
    user = authenticate_user(credentials.email, credentials.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role}
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        name=user.name,
        role=user.role
    )


@router.get("/me")
def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """Get current user information."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role,
        "department": current_user.department,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }


@router.post("/api-keys", response_model=APIKeyResponse)
def create_api_key(
    key_data: APIKeyCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new API key for the current user."""
    from datetime import datetime, timedelta

    api_key = models.APIKey(
        user_id=current_user.id,
        key=generate_api_key(),
        name=key_data.name,
        description=key_data.description,
        expires_at=datetime.utcnow() + timedelta(days=key_data.expires_in_days) if key_data.expires_in_days else None
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return APIKeyResponse(
        id=api_key.id,
        key=api_key.key,
        name=api_key.name,
        description=api_key.description,
        is_active=api_key.is_active,
        created_at=api_key.created_at.isoformat(),
        expires_at=api_key.expires_at.isoformat() if api_key.expires_at else None
    )


@router.get("/api-keys")
def list_api_keys(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all API keys for the current user (excluding the actual key value)."""
    keys = db.query(models.APIKey).filter(models.APIKey.user_id == current_user.id).all()

    return [
        {
            "id": k.id,
            "name": k.name,
            "description": k.description,
            "is_active": k.is_active,
            "created_at": k.created_at.isoformat(),
            "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
            "expires_at": k.expires_at.isoformat() if k.expires_at else None,
            "key_preview": k.key[:10] + "..." if k.key else None  # Show first 10 chars only
        }
        for k in keys
    ]


@router.delete("/api-keys/{key_id}")
def delete_api_key(
    key_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an API key."""
    api_key = db.query(models.APIKey).filter(
        models.APIKey.id == key_id,
        models.APIKey.user_id == current_user.id
    ).first()

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    db.delete(api_key)
    db.commit()

    return {"message": "API key deleted successfully"}
