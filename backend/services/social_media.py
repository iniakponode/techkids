from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional

from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.models.social_post import (
    SocialMediaPost,
    SocialPlatformCredential,
    SocialPostDispatchLog,
)
from backend.pydanticschemas.social_post import (
    SocialMediaPostAnalytics,
    SocialPostDispatchLogSchema,
    SocialPostPreview,
)

DEFAULT_PREVIEW_LENGTH = 180
DEFAULT_RETRY_BACKOFF_SECONDS = 300
DEFAULT_MAX_ATTEMPTS = 3


@dataclass
class DispatchResult:
    success: bool
    platform_post_id: Optional[str] = None
    diagnostics: Optional[str] = None
    error_message: Optional[str] = None
    impressions: int = 0
    clicks: int = 0
    comments: int = 0
    shares: int = 0


@dataclass
class PlatformCredentials:
    platform: str
    access_token: str
    refresh_token: Optional[str] = None
    metadata: Optional[str] = None


def _compute_preview_title(post: SocialMediaPost) -> str:
    if post.preview_title:
        return post.preview_title
    first_line = post.content.strip().splitlines()[0] if post.content else ""
    return first_line[:80] if first_line else f"Upcoming {post.platform.title()} post"


def _compute_preview_description(post: SocialMediaPost) -> str:
    if post.preview_description:
        return post.preview_description
    snippet = post.content.strip().replace("\n", " ")
    if len(snippet) <= DEFAULT_PREVIEW_LENGTH:
        return snippet
    return snippet[: DEFAULT_PREVIEW_LENGTH - 3] + "..."


def build_preview(post: SocialMediaPost) -> SocialPostPreview:
    return SocialPostPreview(
        title=_compute_preview_title(post),
        description=_compute_preview_description(post),
        thumbnail_url=post.preview_image_url or post.image_url,
        platform=post.platform,
        content_type=post.content_type,
    )


def ensure_preview_values(post: SocialMediaPost) -> None:
    if not post.preview_title:
        post.preview_title = _compute_preview_title(post)
    if not post.preview_description:
        post.preview_description = _compute_preview_description(post)
    if not post.preview_image_url:
        post.preview_image_url = post.image_url


def record_dispatch_result(
    db: Session,
    post: SocialMediaPost,
    result: DispatchResult,
) -> None:
    log = SocialPostDispatchLog(
        post=post,
        success=result.success,
        platform_post_id=result.platform_post_id,
        diagnostics=result.diagnostics,
        error_message=result.error_message,
        impressions=result.impressions,
        clicks=result.clicks,
        comments=result.comments,
        shares=result.shares,
    )
    db.add(log)


def apply_dispatch_side_effects(
    post: SocialMediaPost,
    result: DispatchResult,
    retry_backoff_seconds: int | None = None,
    max_attempts: int | None = None,
) -> None:
    retry_backoff_seconds = retry_backoff_seconds or DEFAULT_RETRY_BACKOFF_SECONDS
    max_attempts = max_attempts or DEFAULT_MAX_ATTEMPTS

    post.attempt_count += 1
    post.last_attempt_at = datetime.utcnow()

    if result.success:
        post.status = "posted"
        post.posted_at = post.last_attempt_at
        post.last_error = None
    else:
        post.status = "failed"
        post.last_error = result.error_message or "Unknown error"
        if post.attempt_count < max_attempts:
            post.scheduled_at = datetime.utcnow() + timedelta(seconds=retry_backoff_seconds)
        else:
            post.scheduled_at = None


def aggregate_analytics(post: SocialMediaPost) -> SocialMediaPostAnalytics:
    totals: Dict[str, int] = {"impressions": 0, "clicks": 0, "comments": 0, "shares": 0}
    sorted_logs = sorted(
        post.dispatch_logs,
        key=lambda log: log.attempted_at or datetime.min,
    )
    logs = [SocialPostDispatchLogSchema.model_validate(log) for log in sorted_logs]
    for log in sorted_logs:
        totals["impressions"] += log.impressions
        totals["clicks"] += log.clicks
        totals["comments"] += log.comments
        totals["shares"] += log.shares
    return SocialMediaPostAnalytics(
        post_id=post.id,
        status=post.status,
        attempt_count=post.attempt_count,
        last_attempt_at=post.last_attempt_at,
        posted_at=post.posted_at,
        last_error=post.last_error,
        totals=totals,
        logs=logs,
    )


def upsert_platform_credential(
    db: Session,
    *,
    platform: str,
    access_token: str,
    refresh_token: str | None = None,
    metadata: str | None = None,
) -> SocialPlatformCredential:
    credential = (
        db.query(SocialPlatformCredential)
        .filter(SocialPlatformCredential.platform == platform.lower())
        .one_or_none()
    )
    if credential:
        credential.access_token = access_token
        credential.refresh_token = refresh_token
        credential.metadata_json = metadata
    else:
        credential = SocialPlatformCredential(
            platform=platform.lower(),
            access_token=access_token,
            refresh_token=refresh_token,
            metadata_json=metadata,
        )
        db.add(credential)
    db.commit()
    db.refresh(credential)
    return credential


def list_platform_credentials(db: Session) -> list[SocialPlatformCredential]:
    return db.query(SocialPlatformCredential).order_by(SocialPlatformCredential.platform).all()


def get_platform_credential(db: Session, platform: str) -> Optional[SocialPlatformCredential]:
    return (
        db.query(SocialPlatformCredential)
        .filter(SocialPlatformCredential.platform == platform.lower())
        .one_or_none()
    )


def determine_max_attempts() -> int:
    value = getattr(settings, "POST_DISPATCH_MAX_ATTEMPTS", None)
    if value is not None:
        return int(value)
    return DEFAULT_MAX_ATTEMPTS


def determine_retry_backoff() -> int:
    value = getattr(settings, "POST_DISPATCH_RETRY_BACKOFF", None)
    if value is not None:
        return int(value)
    return DEFAULT_RETRY_BACKOFF_SECONDS


def resolve_platform_credentials(db: Session, platform: str) -> Optional[PlatformCredentials]:
    credential = get_platform_credential(db, platform)
    if credential:
        return PlatformCredentials(
            platform=credential.platform,
            access_token=credential.access_token,
            refresh_token=credential.refresh_token,
            metadata=credential.metadata_json,
        )
    normalized = platform.lower()
    fallback_attr = f"{normalized.upper()}_API_TOKEN"
    if normalized == "twitter":
        fallback_attr = "X_API_TOKEN"
    fallback_token = getattr(settings, fallback_attr, None)
    if fallback_token:
        return PlatformCredentials(platform=normalized, access_token=fallback_token)
    return None


def get_post_with_analytics(db: Session, post_id: int) -> SocialMediaPostAnalytics:
    post = db.query(SocialMediaPost).filter(SocialMediaPost.id == post_id).first()
    if not post:
        raise ValueError("Post not found")
    return aggregate_analytics(post)
