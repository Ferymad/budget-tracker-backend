import pytest
from fastapi.testclient import TestClient


def test_register_user(client: TestClient):
    """Test user registration"""
    response = client.post("/auth/register", json={
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "NewPassword123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "id" in data


def test_register_duplicate_email(client: TestClient):
    """Test registration with duplicate email"""
    # Register first user
    client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "full_name": "First User",
        "password": "Password123"
    })
    
    # Try to register with same email
    response = client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "full_name": "Second User",
        "password": "Password456"
    })
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_login_success(client: TestClient):
    """Test successful login"""
    # Register user first
    client.post("/auth/register", json={
        "email": "login@example.com",
        "full_name": "Login User",
        "password": "LoginPassword123"
    })
    
    # Login
    response = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "LoginPassword123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials"""
    response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_refresh_token(client: TestClient):
    """Test refresh token functionality"""
    # Register and login
    client.post("/auth/register", json={
        "email": "refresh@example.com",
        "full_name": "Refresh User",
        "password": "RefreshPassword123"
    })
    
    login_response = client.post("/auth/login", json={
        "email": "refresh@example.com",
        "password": "RefreshPassword123"
    })
    
    refresh_token = login_response.json()["refresh_token"]
    
    # Use refresh token
    response = client.post("/auth/refresh", json={
        "refresh_token": refresh_token
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_invalid_password_format(client: TestClient):
    """Test registration with invalid password format"""
    response = client.post("/auth/register", json={
        "email": "weak@example.com",
        "full_name": "Weak Password User",
        "password": "weak"
    })
    
    assert response.status_code == 422
    assert "Password must be at least 8 characters long" in str(response.json())