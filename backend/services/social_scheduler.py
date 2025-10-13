from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
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
from backend.services.dispatchers import get_dispatcher, PLATFORM_DISPATCHERS
from backend.services.dispatchers.base import PostContent, PostResult

logger = logging.getLogger(__name__)


# Helper functions -------------------------------------------------------------


def _convert_post_result_to_dispatch_result(post_result: PostResult) -> DispatchResult:
    """Convert dispatcher PostResult to our DispatchResult format"""
    return DispatchResult(
        success=post_result.success,
        platform_post_id=post_result.platform_post_id,
        error_message=post_result.error_message,
        diagnostics=post_result.diagnostics,
        impressions=post_result.impressions,
        clicks=post_result.clicks,
        comments=post_result.comments,
        shares=post_result.shares,
    )


def _build_post_content(post: SocialMediaPost) -> PostContent:
    """Build PostContent from SocialMediaPost"""
    # Get actual values from the post object (SQLAlchemy resolves these at runtime)
    content = str(post.content) if post.content is not None else ""  # type: ignore
    content_type = str(post.content_type) if post.content_type is not None else "Post"  # type: ignore
    image_url_str = str(post.image_url) if post.image_url is not None else None  # type: ignore
    video_url_str = str(post.video_url) if post.video_url is not None else None  # type: ignore
    
    # Convert URLs to local paths if they're relative
    image_path = None
    video_path = None
    image_url = None
    video_url = None
    
    if image_url_str:
        if image_url_str.startswith('/static/'):
            # Convert /static/uploads/file.jpg to frontend/static/uploads/file.jpg
            image_path = str(Path('frontend') / image_url_str.lstrip('/'))
        elif image_url_str.startswith('http'):
            # It's an external URL, keep as URL
            image_url = image_url_str
        else:
            image_path = image_url_str
    
    if video_url_str:
        if video_url_str.startswith('/static/'):
            video_path = str(Path('frontend') / video_url_str.lstrip('/'))
        elif video_url_str.startswith('http'):
            video_url = video_url_str
        else:
            video_path = video_url_str
    
    return PostContent(
        text=content,
        content_type=content_type,
        image_url=image_url,
        video_url=video_url,
        image_path=image_path,
        video_path=video_path,
    )


def _build_platform_credentials(creds: Optional[PlatformCredentials]):  # type: ignore
    """Convert service PlatformCredentials to dispatcher PlatformCredentials"""
    if not creds:
        return None
    
    # Parse metadata JSON string to dict if needed
    metadata = creds.metadata  # type: ignore
    if isinstance(metadata, str):
        import json
        try:
            metadata = json.loads(metadata)
        except:
            metadata = None
    
    from backend.services.dispatchers.base import PlatformCredentials as DispatcherCreds
    return DispatcherCreds(
        platform=creds.platform,  # type: ignore
        access_token=creds.access_token,  # type: ignore
        refresh_token=creds.refresh_token,  # type: ignore
        metadata=metadata,
    )





def _simulate_metrics(post: SocialMediaPost) -> dict[str, int]:
    base = max(len(str(post.content)) if post.content else 0, 1)  # type: ignore
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
        raise ValueError(f"Missing credentials for {post.platform}")  # type: ignore
    metrics = _simulate_metrics(post)
    timestamp = int(datetime.utcnow().timestamp())
    content_len = len(str(post.content)) if post.content else 0  # type: ignore
    return DispatchResult(
        success=True,
        platform_post_id=f"{prefix}_{post.id}_{timestamp}",  # type: ignore
        diagnostics=f"payload_length={content_len}",
        impressions=metrics["impressions"],
        clicks=metrics["clicks"],
        comments=metrics["comments"],
        shares=metrics["shares"],
    )


def post_with_real_dispatcher(
    post: SocialMediaPost,
    credentials: Optional[PlatformCredentials],
) -> DispatchResult:
    """
    Post using the real platform dispatcher (Telegram, X, Facebook, etc.)
    """
    platform = str(post.platform).lower()  # type: ignore
    
    try:
        # Get the appropriate dispatcher
        dispatcher = get_dispatcher(platform)
        
        # Build content and credentials in dispatcher format
        content = _build_post_content(post)
        disp_creds = _build_platform_credentials(credentials)
        
        if not disp_creds:
            return DispatchResult(
                success=False,
                error_message=f"No credentials configured for {platform}",
                diagnostics="Missing platform credentials"
            )
        
        # Validate credentials first
        if not dispatcher.validate_credentials(disp_creds):
            return DispatchResult(
                success=False,
                error_message=f"Invalid credentials for {platform}",
                diagnostics="Credential validation failed"
            )
        
        # Publish the post
        logger.info(f"Publishing post {post.id} to {platform}")  # type: ignore
        result = dispatcher.publish_post(content, disp_creds)
        logger.info(f"Telegram publish result: success={result.success}, post_id={result.platform_post_id}, error={result.error_message}")
        
        # Convert PostResult to DispatchResult
        return _convert_post_result_to_dispatch_result(result)
        
    except ValueError as e:
        # Platform not supported - this means no dispatcher exists for it yet
        logger.warning(f"No dispatcher available for platform '{platform}': {e}")
        return DispatchResult(
            success=False,
            error_message=f"Platform '{platform}' not yet supported",
            diagnostics=str(e)
        )
    except Exception as e:
        logger.error(f"Error publishing to {platform}: {e}", exc_info=True)
        return DispatchResult(
            success=False,
            error_message=str(e),
            diagnostics=f"Exception during publish: {type(e).__name__}"
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
    # Real dispatchers (these will actually post to the platform)
    "telegram": post_with_real_dispatcher,
    "twitter": post_with_real_dispatcher,
    "x": post_with_real_dispatcher,
    
    # Simulated dispatchers (for platforms not yet implemented)
    "facebook": post_to_facebook,
    "instagram": post_to_instagram,
    "whatsapp": post_to_facebook,  # Use facebook sim for now
    "threads": post_to_x,  # Use x sim for now
}


# Core dispatch logic ----------------------------------------------------------


def _send_post(db, post: SocialMediaPost) -> DispatchResult:
    platform = str(post.platform).lower()  # type: ignore
    handler = PLATFORM_HANDLERS.get(platform)
    if not handler:
        return DispatchResult(success=False, error_message="Unsupported platform")

    ensure_preview_values(post)
    credentials = resolve_platform_credentials(db, platform)

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
        
        # Find posts that are due and not already being processed
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
        
        if not due_posts:
            return
            
        # Mark all due posts as processing to prevent duplicate dispatches
        for post in due_posts:
            post.status = "processing"
            db.add(post)
        db.commit()
        
        # Now dispatch each post
        for post in due_posts:
            try:
                _send_post(db, post)
            except Exception as e:
                logger.error(f"Error dispatching post {post.id}: {e}", exc_info=True)
                # Error handling is done in _send_post, but catch any unexpected issues
        
        db.commit()
    except Exception as e:
        logger.error(f"Error in dispatch_due_posts: {e}", exc_info=True)
        db.rollback()
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
