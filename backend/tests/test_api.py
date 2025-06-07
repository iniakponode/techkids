import pytest
import pytest_asyncio
from httpx import AsyncClient
from main import app
from fastapi.testclient import TestClient

# Use TestClient for initial fast setup
client = TestClient(app)


@pytest_asyncio.fixture
async def async_client():
    """
    Fixture to provide an async HTTP client for testing.
    """
    async with AsyncClient(base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_get_users(async_client):
    """
    Test fetching all users
    """
    response = await async_client.get("/users/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_user(async_client):
    """
    Test creating a new user
    """
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    response = await async_client.post("/users/", json=user_data)
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_courses(async_client):
    """
    Test fetching all courses
    """
    response = await async_client.get("/courses/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_course(async_client):
    """
    Test creating a new course
    """
    course_data = {
        "title": "AI for Kids",
        "image_url": "https://example.com/image.jpg",
        "description": "Learn AI with fun exercises!",
        "price": 99.99,
        "age_group": "8-12",
        "duration": "6 weeks",
        "rating": 4.5
    }
    response = await async_client.post("/courses/", json=course_data)
    assert response.status_code == 201
    assert response.json()["title"] == "AI for Kids"

