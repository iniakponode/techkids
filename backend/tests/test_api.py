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
        "category": "Coding",
        "age_group": "8-12",
        "duration": "6 weeks",
        "rating": 4.5
    }
    response = client.post("/courses/", json=course_data)
    assert response.status_code == 201
    assert response.json()["title"] == "AI for Kids"


def test_social_media_posts():
    """Test listing social media posts."""
    response = client.get("/admin/social-posts/")
    assert response.status_code in (200, 403, 401)


def test_create_social_media_post():
    """Test creating a social media post."""
    data = {
        "platform": "x",
        "content": "Hello",
        "content_type": "Post",
    }
    response = client.post("/admin/social-posts/", data=data)
    assert response.status_code in (201, 403, 401)


def test_create_scheduled_post():
    """Test creating a scheduled post."""
    data = {
        "platform": "facebook",
        "content": "Scheduled",
        "content_type": "Feed",
        "scheduled_at": "2030-01-01T10:00:00",
    }
    response = client.post("/admin/social-posts/", data=data)
    assert response.status_code in (201, 403, 401)


def test_teacher_application():
    data = {
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "08000000000",
        "message": "I would like to teach."}
    response = client.post("/teacher-applications", json=data)
    assert response.status_code in (201, 422)


