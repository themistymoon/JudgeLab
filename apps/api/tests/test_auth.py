import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base, get_db
from main import app

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def test_client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as client:
        yield client
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_user_data():
    return {
        "email": "test@example.com",
        "display_name": "Test User",
        "password": "testpassword123"
    }


class TestAuthentication:

    def test_register_user(self, test_client, sample_user_data):
        """Test user registration."""
        response = test_client.post("/api/v1/auth/register", json=sample_user_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == sample_user_data["email"]
        assert data["user"]["display_name"] == sample_user_data["display_name"]
        assert data["user"]["role"] == "STUDENT"

    def test_register_duplicate_email(self, test_client, sample_user_data):
        """Test registration with duplicate email fails."""
        # First registration
        test_client.post("/api/v1/auth/register", json=sample_user_data)

        # Second registration with same email
        response = test_client.post("/api/v1/auth/register", json=sample_user_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_login_success(self, test_client, sample_user_data):
        """Test successful login."""
        # Register user first
        test_client.post("/api/v1/auth/register", json=sample_user_data)

        # Login
        login_data = {
            "username": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        response = test_client.post("/api/v1/auth/token", data=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

    def test_login_invalid_credentials(self, test_client):
        """Test login with invalid credentials."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = test_client.post("/api/v1/auth/token", data=login_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_get_current_user(self, test_client, sample_user_data):
        """Test getting current user info with valid token."""
        # Register and login
        test_client.post("/api/v1/auth/register", json=sample_user_data)
        login_data = {
            "username": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        login_response = test_client.post("/api/v1/auth/token", data=login_data)
        token = login_response.json()["access_token"]

        # Get user info
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["display_name"] == sample_user_data["display_name"]

    def test_get_current_user_invalid_token(self, test_client):
        """Test getting current user info with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = test_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]

    def test_get_current_user_no_token(self, test_client):
        """Test accessing protected endpoint without token."""
        response = test_client.get("/api/v1/auth/me")
        assert response.status_code == 401


class TestValidation:

    def test_register_invalid_email(self, test_client):
        """Test registration with invalid email format."""
        invalid_data = {
            "email": "invalid-email",
            "display_name": "Test User",
            "password": "testpassword123"
        }
        response = test_client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422

    def test_register_short_password(self, test_client):
        """Test registration with password too short."""
        invalid_data = {
            "email": "test@example.com",
            "display_name": "Test User",
            "password": "short"
        }
        response = test_client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422

    def test_register_empty_display_name(self, test_client):
        """Test registration with empty display name."""
        invalid_data = {
            "email": "test@example.com",
            "display_name": "",
            "password": "testpassword123"
        }
        response = test_client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422
