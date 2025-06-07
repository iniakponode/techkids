import pytest

try:
    import httpx  # noqa: F401
except ModuleNotFoundError:
    pytest.skip("httpx is required for API tests", allow_module_level=True)

from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_get_users():
    """Test fetching all users"""

    response = client.get("/users/")
    assert response.status_code == 200


def test_create_user():
    """Test creating a new user"""
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "role": "student"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"


def test_get_courses():
    """Test fetching all courses"""

    response = client.get("/courses/")
    assert response.status_code == 200


def test_create_course():
    """Test creating a new course"""
    course_data = {
        "title": "AI for Kids",
        "image_url": "https://example.com/image.jpg",
        "description": "Learn AI with fun exercises!",
        "price": 99.99,
        "age_group": "8-12",
        "duration": "6 weeks",
        "rating": 4.5
    }
    response = client.post("/courses/", json=course_data)
    assert response.status_code == 201
    assert response.json()["title"] == "AI for Kids"

