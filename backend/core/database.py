# backend/core/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# For now, let's use SQLite
DB_URL = os.getenv("DATABASE_URL", "mysql+pymysql://techkids:ProgressIniks2018@localhost:3306/aitechkids")

if DB_URL.startswith("sqlite:"):
    engine = create_engine(DB_URL, connect_args={"check_same_thread": False}, echo=True)
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
    Base.metadata.create_all(bind=engine)
