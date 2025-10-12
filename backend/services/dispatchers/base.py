"""
Base Platform Dispatcher

Abstract base class that defines the interface for all social media platform dispatchers.
Each platform-specific dispatcher must implement these methods.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class PostResult:
    """Result of posting to a social media platform"""
    success: bool
    platform_post_id: Optional[str] = None
    error_message: Optional[str] = None
    diagnostics: Optional[str] = None
    impressions: int = 0
    clicks: int = 0
    comments: int = 0
    shares: int = 0


@dataclass
class MediaUploadResult:
    """Result of uploading media to a platform"""
    success: bool
    media_id: Optional[str] = None
    media_url: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class PlatformCredentials:
    """Credentials for authenticating with a platform"""
    platform: str
    access_token: str
    refresh_token: Optional[str] = None
    metadata: Optional[dict] = None


@dataclass
class PostContent:
    """Content to be posted to a social media platform"""
    text: str
    content_type: str  # e.g., 'Feed', 'Story', 'Reel', 'Post'
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    image_path: Optional[str] = None
    video_path: Optional[str] = None


class BasePlatformDispatcher(ABC):
    """
    Abstract base class for social media platform dispatchers.
    
    Each platform (Facebook, Instagram, X, etc.) must implement:
    - Authentication/token validation
    - Post publishing
    - Media uploads
    - Analytics retrieval
    """
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """The name of the platform (e.g., 'facebook', 'instagram')"""
        pass
    
    @property
    @abstractmethod
    def supports_scheduled_posts(self) -> bool:
        """Whether the platform supports native scheduled posting"""
        pass
    
    @property
    @abstractmethod
    def max_text_length(self) -> int:
        """Maximum characters allowed in a post"""
        pass
    
    @property
    @abstractmethod
    def supported_content_types(self) -> list[str]:
        """List of supported content types (e.g., ['Feed', 'Story', 'Reel'])"""
        pass
    
    @abstractmethod
    def validate_credentials(self, credentials: PlatformCredentials) -> bool:
        """
        Validate that the provided credentials are valid and have necessary permissions.
        
        Args:
            credentials: Platform credentials including access token
        
        Returns:
            True if credentials are valid, False otherwise
        """
        pass
    
    @abstractmethod
    def publish_post(
        self,
        content: PostContent,
        credentials: PlatformCredentials,
    ) -> PostResult:
        """
        Publish content to the platform.
        
        Args:
            content: The content to post (text, images, videos)
            credentials: Platform credentials for authentication
        
        Returns:
            PostResult with success status and platform post ID or error
        """
        pass
    
    @abstractmethod
    def upload_media(
        self,
        media_path: str,
        media_type: str,
        credentials: PlatformCredentials,
    ) -> MediaUploadResult:
        """
        Upload media (image or video) to the platform.
        
        Args:
            media_path: Local file path to the media
            media_type: 'image' or 'video'
            credentials: Platform credentials for authentication
        
        Returns:
            MediaUploadResult with media ID/URL or error
        """
        pass
    
    @abstractmethod
    def get_post_analytics(
        self,
        platform_post_id: str,
        credentials: PlatformCredentials,
    ) -> dict:
        """
        Retrieve analytics/metrics for a published post.
        
        Args:
            platform_post_id: The platform's unique post identifier
            credentials: Platform credentials for authentication
        
        Returns:
            Dictionary with metrics (impressions, clicks, comments, shares, etc.)
        """
        pass
    
    @abstractmethod
    def refresh_access_token(
        self,
        credentials: PlatformCredentials,
    ) -> Optional[PlatformCredentials]:
        """
        Refresh an expired access token using a refresh token.
        
        Args:
            credentials: Current credentials including refresh token
        
        Returns:
            New credentials with refreshed access token, or None if failed
        """
        pass
    
    def validate_content(self, content: PostContent) -> tuple[bool, Optional[str]]:
        """
        Validate content against platform-specific constraints.
        
        Args:
            content: The content to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check text length
        if len(content.text) > self.max_text_length:
            return False, f"Text exceeds maximum length of {self.max_text_length} characters"
        
        # Check content type
        if content.content_type not in self.supported_content_types:
            return False, f"Content type '{content.content_type}' not supported. " \
                         f"Supported types: {', '.join(self.supported_content_types)}"
        
        # Subclasses can override this method for additional validation
        return True, None
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} platform={self.platform_name}>"
