# backend/core/database.py

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

# For now, let's use SQLite by default for local development and testing.
_default_db_url = "sqlite:///./aitechkids.db"
_running_tests = "pytest" in sys.modules or os.getenv("PYTEST_CURRENT_TEST")

# Debug: Print environment info for production debugging
_environment = os.getenv("ENVIRONMENT", "development")
print(f"[DATABASE] Environment: {_environment}")
print(f"[DATABASE] Working directory: {os.getcwd()}")

_raw_db_url = os.getenv("DATABASE_URL", _default_db_url)
print(f"[DATABASE] Raw DATABASE_URL: {_raw_db_url[:50]}..." if _raw_db_url and len(_raw_db_url) > 50 else f"[DATABASE] Raw DATABASE_URL: {_raw_db_url}")
if _running_tests:
    # When running the test suite default to an isolated SQLite database to
    # avoid relying on external services such as MySQL. Drop any existing file
    # to ensure a clean slate between test runs.
    _raw_db_url = os.getenv("TEST_DATABASE_URL", "sqlite:///./aitechkids_test.db")
    url_obj = make_url(_raw_db_url)
    if url_obj.drivername.startswith("sqlite") and url_obj.database:
        db_path = Path(url_obj.database)
        if not db_path.is_absolute():
            db_path = Path.cwd() / db_path
        if db_path.is_file():
            db_path.unlink()

# Some hosting environments wrap environment variables in quotes. Strip them out so
# SQLAlchemy can parse the URL correctly.
DB_URL = _raw_db_url.strip().strip('"\'')

print(f"[DATABASE] Final DB_URL: {DB_URL[:50]}..." if DB_URL and len(DB_URL) > 50 else f"[DATABASE] Final DB_URL: {DB_URL}")
print(f"[DATABASE] Database type: {'MySQL' if 'mysql' in DB_URL.lower() else 'SQLite'}")

if DB_URL.startswith("sqlite:"):
    engine = create_engine(
        DB_URL,
        connect_args={"check_same_thread": False},
        echo=os.getenv("ENVIRONMENT") != "production",  # Disable SQL logging in production
    )
else:
    # MySQL/PostgreSQL configuration with connection pooling
    engine = create_engine(
        DB_URL, 
        echo=os.getenv("ENVIRONMENT") != "production",  # Disable SQL logging in production
        pool_size=10,  # Number of connections to maintain in the pool
        max_overflow=20,  # Maximum number of connections that can overflow the pool
        pool_timeout=30,  # Timeout for getting connection from pool
        pool_recycle=3600,  # Recycle connections after 1 hour
        pool_pre_ping=True,  # Validate connections before use
    )

# engine = create_engine(DB_URL, connect_args={"check_same_thread": False}, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

def get_db():
    """
    Dependency function that provides a database session.
    Use 'get_db' in your routers to get a session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """Create all database tables if they don't exist."""
    # Import models lazily to ensure SQLAlchemy is aware of all mapped classes
    # before attempting to create tables.
    import backend.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
