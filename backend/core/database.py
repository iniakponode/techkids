# backend/core/database.py

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

# For now, let's use SQLite by default for local development and testing.
_default_db_url = "sqlite:///./techkids.db"
_running_tests = "pytest" in sys.modules or os.getenv("PYTEST_CURRENT_TEST")
_raw_db_url = os.getenv("DATABASE_URL", _default_db_url)
if _running_tests:
    # When running the test suite default to an isolated SQLite database to
    # avoid relying on external services such as MySQL. Drop any existing file
    # to ensure a clean slate between test runs.
    _raw_db_url = os.getenv("TEST_DATABASE_URL", "sqlite:///./techkids_test.db")
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

if DB_URL.startswith("sqlite:"):
    engine = create_engine(
        DB_URL,
        connect_args={"check_same_thread": False},
        echo=True,
    )
else:
    engine = create_engine(DB_URL, echo=True)

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
