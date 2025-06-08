# backend/main.py

import logging
import os
import dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from starlette.middleware.sessions import SessionMiddleware # Import SessionMiddleware
import uvicorn
import uvicorn
from backend.middleware import blacklist_middleware
from backend.routers import api_router, pages_router
from backend.services.social_scheduler import start_scheduler
from backend.core.database import init_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)

app = FastAPI(
    title="TechKids Website",
    description="This is an API powering Techkids App",
    version="1.0.0",
    )

# Example usage of environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG") == "True"

# Load .env only for local development
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
if ENVIRONMENT == "development":
    dotenv.load_dotenv()
    
# Define allowed CORS origins
origins = [
    "https://techkids.ungozu.com",
    # Add other origins if necessary
]

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if ENVIRONMENT == "production" else ["*"],  # Allow all in local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Session Middleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY) # Add Session Middleware
app.middleware("http")(blacklist_middleware)
# Mount static folder for CSS/JS
static_folder_path = os.path.join(os.path.dirname(__file__), "frontend", "static")
app.mount("/static", StaticFiles(directory=static_folder_path), name="static")
# This serves files from the 'static' directory
# app.mount("/static", StaticFiles(directory="static"), name="static")
# static\uploads\7079151a-884b-4317-b066-2b88e6f478c8.jpg
# Include the API router with /api prefix
app.include_router(api_router, prefix="/api")

# Include the pages router for frontend routes
app.include_router(pages_router)


@app.on_event("startup")
def start_background_tasks() -> None:
    """Start recurring schedulers."""
    init_db()
    start_scheduler()



# Alembic configuration file path
ALEMBIC_CONFIG_PATH = "./alembic.ini"

# for route in app.routes:
#     print(route.path, route.name)


# @app.on_event("startup")
# async def on_startup():
#     # Run Alembic migrations programmatically
#     alembic_cfg = Config(ALEMBIC_CONFIG_PATH)
#     alembic_cfg.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
 
#     print("Running Alembic migrations...")
#     command.upgrade(alembic_cfg, "head")  # Upgrade database schema to latest
#     print("Migrations completed successfully.")
    

# Run the app using uvicorn when executed directly
if __name__ == "__main__":
    @app.get("/")
    def read_root():
        return {"message": "Welcome to Tech Kids App!"}

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )

    # Set host and port based on environment
    host = "0.0.0.0" if ENVIRONMENT == "production" else "127.0.0.1"
    port = int(os.environ.get("PORT", 8002))  # Use Heroku's $PORT or default for local

    uvicorn.run("main:app", reload=(ENVIRONMENT == "development"), host=host, port=port)