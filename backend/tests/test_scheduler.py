import datetime

import pytest

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
except ModuleNotFoundError:
    pytest.skip("sqlalchemy is required", allow_module_level=True)

from backend.models.social_post import (
    SocialMediaPost,
    SocialPlatformCredential,
    SocialPostDispatchLog,
)
from backend.core.database import Base
from backend.services import social_scheduler
from backend.services.social_media import DispatchResult


def setup_in_memory_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    return engine, TestingSessionLocal


def test_dispatch_due_posts(monkeypatch):
    engine, TestSession = setup_in_memory_db()
    monkeypatch.setattr(social_scheduler, "SessionLocal", TestSession)

    sent = []

    def fake_handler(post, _credentials):
        sent.append(post.id)
        return DispatchResult(success=True)

    social_scheduler.PLATFORM_HANDLERS["facebook"] = fake_handler

    db = TestSession()
    credential = SocialPlatformCredential(
        platform="facebook",
        access_token="token",
    )
    db.add(credential)
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

    refreshed_post = db.query(SocialMediaPost).filter(SocialMediaPost.id == post.id).one()
    assert refreshed_post.status == "posted"
    assert refreshed_post.attempt_count == 1
    assert refreshed_post.last_attempt_at is not None
    assert refreshed_post.preview_title
    logs = db.query(SocialPostDispatchLog).filter_by(post_id=post.id).all()
    assert len(logs) == 1
    assert logs[0].success is True
    assert sent == [post.id]

    db.close()
    engine.dispose()
