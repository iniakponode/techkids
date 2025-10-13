"""
Social Media Platform Dispatchers

This package contains the real-world integrations with social media platforms.
Each dispatcher handles authentication, posting, media uploads, and analytics
for its respective platform.
"""

from typing import Dict, Type

from backend.services.dispatchers.base import BasePlatformDispatcher

# Import platform-specific dispatchers as they're implemented
from backend.services.dispatchers.telegram_dispatcher import TelegramDispatcher
from backend.services.dispatchers.twitter_dispatcher import TwitterDispatcher
# from backend.services.dispatchers.facebook_dispatcher import FacebookDispatcher
# from backend.services.dispatchers.instagram_dispatcher import InstagramDispatcher
# from backend.services.dispatchers.whatsapp_dispatcher import WhatsAppDispatcher

# Registry of available dispatchers
PLATFORM_DISPATCHERS: Dict[str, Type[BasePlatformDispatcher]] = {
    "telegram": TelegramDispatcher,
    "twitter": TwitterDispatcher,
    "x": TwitterDispatcher,  # X is the new name for Twitter
    # "facebook": FacebookDispatcher,
    # "instagram": InstagramDispatcher,
    # "whatsapp": WhatsAppDispatcher,
}


def get_dispatcher(platform: str) -> BasePlatformDispatcher:
    """
    Get the appropriate dispatcher for a given platform.
    
    Args:
        platform: The platform name (e.g., 'facebook', 'instagram', 'x')
    
    Returns:
        An instance of the platform's dispatcher
    
    Raises:
        ValueError: If the platform is not supported
    """
    platform_normalized = platform.lower()
    dispatcher_class = PLATFORM_DISPATCHERS.get(platform_normalized)
    
    if not dispatcher_class:
        raise ValueError(
            f"Platform '{platform}' is not supported. "
            f"Available platforms: {', '.join(PLATFORM_DISPATCHERS.keys())}"
        )
    
    return dispatcher_class()


__all__ = [
    "BasePlatformDispatcher",
    "PLATFORM_DISPATCHERS",
    "get_dispatcher",
]
