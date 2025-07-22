import pytest
from fastapi.testclient import TestClient


def test_signup(client):
    """Test user signup"""
    user_data = {
        "email": "newuser@example.com",
        "password": "password123",
        "full_name": "New User"
    }
    
    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data


def test_signup_duplicate_email(client, test_user):
    """Test signup with duplicate email"""
    # Create first user
    response = client.post("/auth/signup", json=test_user)
    assert response.status_code == 200
    
    # Try to create user with same email
    response = client.post("/auth/signup", json=test_user)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_login_success(client, test_user):
    """Test successful login"""
    # Create user
    client.post("/auth/signup", json=test_user)
    
    # Login
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials"""
    # Create user
    client.post("/auth/signup", json=test_user)
    
    # Try login with wrong password
    login_data = {
        "email": test_user["email"],
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "password123"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401
