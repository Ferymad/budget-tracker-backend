import pytest
from fastapi.testclient import TestClient


def test_create_category(client: TestClient, auth_headers: dict):
    """Test creating a new category"""
    response = client.post("/categories/", 
        json={
            "name": "Food & Dining",
            "description": "Restaurant and grocery expenses",
            "color": "#FF6B6B",
            "icon": "food"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Food & Dining"
    assert data["description"] == "Restaurant and grocery expenses"
    assert data["color"] == "#FF6B6B"
    assert data["icon"] == "food"


def test_get_categories(client: TestClient, auth_headers: dict):
    """Test getting user categories"""
    # Create a category first
    client.post("/categories/", 
        json={"name": "Transportation", "color": "#4ECDC4"},
        headers=auth_headers
    )
    
    response = client.get("/categories/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(cat["name"] == "Transportation" for cat in data)


def test_create_duplicate_category_name(client: TestClient, auth_headers: dict):
    """Test creating category with duplicate name"""
    # Create first category
    client.post("/categories/", 
        json={"name": "Entertainment"},
        headers=auth_headers
    )
    
    # Try creating another with same name
    response = client.post("/categories/", 
        json={"name": "Entertainment"},
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "Category with this name already exists" in response.json()["detail"]


def test_invalid_color_format(client: TestClient, auth_headers: dict):
    """Test creating category with invalid color"""
    response = client.post("/categories/", 
        json={
            "name": "Health",
            "color": "invalid-color"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 422
    assert "Color must be a valid hex color code" in str(response.json())


def test_unauthorized_access(client: TestClient):
    """Test accessing categories without authentication"""
    response = client.get("/categories/")
    
    assert response.status_code == 401