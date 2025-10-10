from __future__ import annotations

from datetime import datetime
from typing import Callable, Dict, Optional

from sqlalchemy import or_

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.core.config import settings
from backend.core.database import SessionLocal
from backend.models.social_post import SocialMediaPost
from backend.services.social_media import (
    DispatchResult,
    PlatformCredentials,
    apply_dispatch_side_effects,
    determine_max_attempts,
    determine_retry_backoff,
    ensure_preview_values,
    record_dispatch_result,
    resolve_platform_credentials,
)


# Platform posting simulations -------------------------------------------------


def _simulate_metrics(post: SocialMediaPost) -> dict[str, int]:
    base = max(len(post.content), 1)
    return {
        "impressions": base * 3,
        "clicks": max(base // 10, 1),
        "comments": max(base // 25, 0),
        "shares": max(base // 30, 0),
    }


def _simulate_publish(
    post: SocialMediaPost,
    credentials: Optional[PlatformCredentials],
    *,
    prefix: str,
) -> DispatchResult:
    if not credentials or not credentials.access_token:
        raise ValueError(f"Missing credentials for {post.platform}")
    metrics = _simulate_metrics(post)
    timestamp = int(datetime.utcnow().timestamp())
    return DispatchResult(
        success=True,
        platform_post_id=f"{prefix}_{post.id}_{timestamp}",
        diagnostics=f"payload_length={len(post.content)}",
        impressions=metrics["impressions"],
        clicks=metrics["clicks"],
        comments=metrics["comments"],
        shares=metrics["shares"],
    )


def post_to_facebook(
    post: SocialMediaPost, credentials: Optional[PlatformCredentials]
) -> DispatchResult:
    return _simulate_publish(post, credentials, prefix="fb")


def post_to_x(post: SocialMediaPost, credentials: Optional[PlatformCredentials]) -> DispatchResult:
    return _simulate_publish(post, credentials, prefix="x")


def post_to_instagram(
    post: SocialMediaPost, credentials: Optional[PlatformCredentials]
) -> DispatchResult:
    return _simulate_publish(post, credentials, prefix="ig")


PLATFORM_HANDLERS: Dict[
    str, Callable[[SocialMediaPost, Optional[PlatformCredentials]], DispatchResult]
] = {
    "facebook": post_to_facebook,
    "x": post_to_x,
    "twitter": post_to_x,
    "instagram": post_to_instagram,
}


# Core dispatch logic ----------------------------------------------------------


def _send_post(db, post: SocialMediaPost) -> DispatchResult:
    handler = PLATFORM_HANDLERS.get(post.platform.lower())
    if not handler:
        return DispatchResult(success=False, error_message="Unsupported platform")

    ensure_preview_values(post)
    credentials = resolve_platform_credentials(db, post.platform)

    try:
        result = handler(post, credentials)
    except Exception as exc:  # pragma: no cover - safety net
        result = DispatchResult(success=False, error_message=str(exc))

    record_dispatch_result(db, post, result)
    apply_dispatch_side_effects(
        post,
        result,
        retry_backoff_seconds=determine_retry_backoff(),
        max_attempts=determine_max_attempts(),
    )
    db.add(post)
    return result


def dispatch_due_posts() -> None:
    """Publish all due posts and update their status."""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        max_attempts = determine_max_attempts()
        due_posts = (
            db.query(SocialMediaPost)
            .filter(
                SocialMediaPost.status.in_(["draft", "queued", "failed"]),
            )
            .filter(
                or_(
                    SocialMediaPost.scheduled_at.is_(None),
                    SocialMediaPost.scheduled_at <= now,
                )
            )
            .filter(SocialMediaPost.attempt_count < max_attempts)
            .all()
        )
        processed = False
        for post in due_posts:
            _send_post(db, post)
            processed = True
        if processed:
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
