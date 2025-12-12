"""
Unit tests for authentication system.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.api.main import app
from services.api.database import Base, get_db
from services.api import models
import os

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Set test SECRET_KEY
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-at-least-32-chars-long"

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestAuthentication:
    """Test authentication endpoints."""

    def test_register_success(self):
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "SecurePass123",
                "department": "Engineering"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
        assert data["role"] == "developer"  # Default role

    def test_register_weak_password(self):
        """Test registration with weak password."""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "weak",  # Too short, no uppercase, no number
            }
        )

        assert response.status_code == 400
        assert "Password must be at least 8 characters" in response.json()["detail"]

    def test_register_no_uppercase(self):
        """Test password without uppercase letter."""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "lowercase123",
            }
        )

        assert response.status_code == 400
        assert "uppercase" in response.json()["detail"]

    def test_register_no_number(self):
        """Test password without number."""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "PasswordOnly",
            }
        )

        assert response.status_code == 400
        assert "number" in response.json()["detail"]

    def test_register_invalid_email(self):
        """Test registration with invalid email."""
        response = client.post(
            "/auth/register",
            json={
                "email": "not-an-email",
                "name": "Test User",
                "password": "SecurePass123",
            }
        )

        assert response.status_code == 400
        assert "Invalid email" in response.json()["detail"]

    def test_register_duplicate_email(self):
        """Test registration with existing email."""
        # First registration
        client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "SecurePass123",
            }
        )

        # Try to register again with same email
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "name": "Another User",
                "password": "SecurePass123",
            }
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_login_success(self):
        """Test successful login."""
        # Register user first
        client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "SecurePass123",
            }
        )

        # Login
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "SecurePass123",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["email"] == "test@example.com"

    def test_login_wrong_password(self):
        """Test login with wrong password."""
        # Register user
        client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "SecurePass123",
            }
        )

        # Try to login with wrong password
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword123",
            }
        )

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self):
        """Test login with non-existent user."""
        response = client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SecurePass123",
            }
        )

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_get_current_user(self):
        """Test getting current user info."""
        # Register and get token
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "SecurePass123",
            }
        )
        token = response.json()["access_token"]

        # Get current user
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
        assert data["role"] == "developer"

    def test_get_current_user_no_token(self):
        """Test getting current user without token."""
        response = client.get("/auth/me")

        assert response.status_code == 403  # No authorization header

    def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401


class TestAPIKeys:
    """Test API key functionality."""

    def test_create_api_key(self):
        """Test creating an API key."""
        # Register and get token
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "SecurePass123",
            }
        )
        token = response.json()["access_token"]

        # Create API key
        response = client.post(
            "/auth/api-keys",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Test API Key",
                "description": "For testing",
                "expires_in_days": 30
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "key" in data
        assert data["key"].startswith("sk-")
        assert data["name"] == "Test API Key"
        assert data["is_active"] is True

    def test_list_api_keys(self):
        """Test listing API keys."""
        # Register and get token
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "SecurePass123",
            }
        )
        token = response.json()["access_token"]

        # Create two API keys
        client.post(
            "/auth/api-keys",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Key 1"}
        )
        client.post(
            "/auth/api-keys",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Key 2"}
        )

        # List API keys
        response = client.get(
            "/auth/api-keys",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        keys = response.json()
        assert len(keys) == 2
        # Full key should not be returned (only preview)
        assert "key_preview" in keys[0]
        assert "key" not in keys[0]  # Full key should not be in list

    def test_delete_api_key(self):
        """Test deleting an API key."""
        # Register and get token
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "SecurePass123",
            }
        )
        token = response.json()["access_token"]

        # Create API key
        response = client.post(
            "/auth/api-keys",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Test Key"}
        )
        key_id = response.json()["id"]

        # Delete API key
        response = client.delete(
            f"/auth/api-keys/{key_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

    def test_delete_nonexistent_api_key(self):
        """Test deleting non-existent API key."""
        # Register and get token
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "SecurePass123",
            }
        )
        token = response.json()["access_token"]

        # Try to delete non-existent key
        response = client.delete(
            "/auth/api-keys/99999",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
