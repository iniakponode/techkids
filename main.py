from __future__ import annotations

import logging
import os
from pathlib import Path

import dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

from backend.middleware import blacklist_middleware
from backend.routers import api_router, pages_router
from backend.routers.course import router as course_router
from backend.routers.social_media import router as social_media_router
from backend.routers.teacher_application import router as teacher_application_router
from backend.routers.user import router as user_router
from backend.services.social_scheduler import start_scheduler
from backend.core.database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)

# Load environment variables early so that local development picks up values from
# a .env file without affecting production environments.
dotenv.load_dotenv(override=False)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "techkids-development-secret")
DEBUG = os.getenv("DEBUG") == "True"

app = FastAPI(
    title="TechKids Website",
    description="This is an API powering Techkids App",
    version="1.0.0",
)

# Define allowed CORS origins
default_origins = [
    "https://techkids.ungozu.com",
]
allow_origins = default_origins if ENVIRONMENT == "production" else ["*"]

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Session Middleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.middleware("http")(blacklist_middleware)

# Mount static folder for CSS/JS
static_folder_path = Path(__file__).resolve().parent / "frontend" / "static"
app.mount("/static", StaticFiles(directory=static_folder_path), name="static")

# Include the API router with /api prefix
app.include_router(api_router, prefix="/api")

# Include the pages router for frontend routes
app.include_router(pages_router)

# Public user routes
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(course_router, prefix="/courses", tags=["courses"])
app.include_router(social_media_router, tags=["Social Media"])
app.include_router(teacher_application_router, tags=["teacher_applications"])

# Ensure database tables exist when the application starts up.
init_db()


@app.on_event("startup")
def start_background_tasks() -> None:
    """Start recurring schedulers."""
    init_db()
    start_scheduler()


# Alembic configuration file path
ALEMBIC_CONFIG_PATH = "./alembic.ini"


# Run the app using uvicorn when executed directly
if __name__ == "__main__":

    @app.get("/")
    def read_root():
        return {"message": "Welcome to Tech Kids App!"}

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()],
    )

    # Set host and port based on environment
    host = "0.0.0.0" if ENVIRONMENT == "production" else "127.0.0.1"
    port = int(os.environ.get("PORT", 8002))  # Use Heroku's $PORT or default for local

    uvicorn.run("main:app", reload=(ENVIRONMENT == "development"), host=host, port=port)