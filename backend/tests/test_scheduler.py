import datetime
import pytest

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
except ModuleNotFoundError:
    pytest.skip("sqlalchemy is required", allow_module_level=True)

from backend.models.social_post import SocialMediaPost
from backend.core.database import Base
from backend.services import social_scheduler


def setup_in_memory_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    return engine, TestingSessionLocal


def test_dispatch_due_posts(monkeypatch):
    engine, TestSession = setup_in_memory_db()
    monkeypatch.setattr(social_scheduler, "SessionLocal", TestSession)

    sent = []

    def fake_handler(post):
        sent.append(post.id)

    social_scheduler.PLATFORM_HANDLERS["facebook"] = fake_handler

    db = TestSession()
    post = SocialMediaPost(
        platform="facebook",
        content="hello",
        content_type="feed",
        scheduled_at=datetime.datetime.utcnow() - datetime.timedelta(minutes=1),
        status="draft",
    )
    db.add(post)
    db.commit()

    social_scheduler.dispatch_due_posts()

    db.refresh(post)
    assert post.status == "posted"
    assert sent == [post.id]

    db.close()
    engine.dispose()
