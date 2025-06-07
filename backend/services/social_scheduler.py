from datetime import datetime
from typing import Callable, Dict

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.core.config import settings
from backend.core.database import SessionLocal
from backend.models.social_post import SocialMediaPost


# Placeholder posting functions ---------------------------------------------

def post_to_facebook(post: SocialMediaPost) -> None:
    """Simulate sending a post to Facebook API."""
    # Here you would use settings.FACEBOOK_API_TOKEN etc.
    print(f"Posting to Facebook: {post.content}")


def post_to_x(post: SocialMediaPost) -> None:
    """Simulate sending a post to X/Twitter API."""
    print(f"Posting to X: {post.content}")


def post_to_instagram(post: SocialMediaPost) -> None:
    """Simulate sending a post to Instagram API."""
    print(f"Posting to Instagram: {post.content}")


PLATFORM_HANDLERS: Dict[str, Callable[[SocialMediaPost], None]] = {
    "facebook": post_to_facebook,
    "x": post_to_x,
    "twitter": post_to_x,
    "instagram": post_to_instagram,
}


# Core dispatch logic --------------------------------------------------------

def _send_post(post: SocialMediaPost) -> bool:
    handler = PLATFORM_HANDLERS.get(post.platform.lower())
    if not handler:
        return False
    try:
        handler(post)
        return True
    except Exception:
        return False


def dispatch_due_posts() -> None:
    """Publish all due posts and update their status."""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        due_posts = (
            db.query(SocialMediaPost)
            .filter(SocialMediaPost.status == "draft")
            .filter(SocialMediaPost.scheduled_at <= now)
            .all()
        )
        for post in due_posts:
            success = _send_post(post)
            post.status = "posted" if success else "failed"
            db.add(post)
        if due_posts:
            db.commit()
    finally:
        db.close()


_scheduler: BackgroundScheduler | None = None

def start_scheduler() -> None:
    """Start the background scheduler if not already running."""
    global _scheduler
    if _scheduler:
        return
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        dispatch_due_posts,
        IntervalTrigger(seconds=settings.POST_SCHEDULER_INTERVAL),
    )
    scheduler.start()
    _scheduler = scheduler
