"""
Telegram Bot API Dispatcher

Implements posting to Telegram channels using the Telegram Bot API.
This is one of the simplest social media integrations to implement.

Documentation: https://core.telegram.org/bots/api
"""

import logging
from typing import Optional
import httpx
from pathlib import Path

from backend.services.dispatchers.base import (
    BasePlatformDispatcher,
    MediaUploadResult,
    PlatformCredentials,
    PostContent,
    PostResult,
)

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org"


class TelegramDispatcher(BasePlatformDispatcher):
    """
    Dispatcher for posting to Telegram channels via Bot API.
    
    Setup:
    1. Create a bot with @BotFather on Telegram
    2. Get your bot token
    3. Create a channel and add your bot as administrator
    4. Get the channel ID (e.g., @your_channel or -1001234567890)
    
    The bot token should be stored in credentials.access_token
    The channel ID should be stored in credentials.metadata['channel_id']
    """
    
    @property
    def platform_name(self) -> str:
        return "telegram"
    
    @property
    def supports_scheduled_posts(self) -> bool:
        # Telegram doesn't support native scheduled posts via Bot API
        return False
    
    @property
    def max_text_length(self) -> int:
        # Telegram allows up to 4096 characters per message
        return 4096
    
    @property
    def supported_content_types(self) -> list[str]:
        return ["Post"]
    
    def _get_api_url(self, bot_token: str, method: str) -> str:
        """Construct the API URL for a given method"""
        return f"{TELEGRAM_API_BASE}/bot{bot_token}/{method}"
    
    def _get_channel_id(self, credentials: PlatformCredentials) -> str:
        """Extract channel ID from credentials metadata"""
        if credentials.metadata and isinstance(credentials.metadata, dict):
            channel_id = credentials.metadata.get('channel_id')
            if channel_id:
                return channel_id
        
        # Fallback: try to get from metadata string
        if credentials.metadata and isinstance(credentials.metadata, str):
            # Assume it's the channel ID directly
            return credentials.metadata
        
        raise ValueError("Channel ID not found in credentials metadata")
    
    def validate_credentials(self, credentials: PlatformCredentials) -> bool:
        """
        Validate bot token by calling getMe API method.
        
        Returns:
            True if the bot token is valid
        """
        try:
            url = self._get_api_url(credentials.access_token, "getMe")
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                data = response.json()
                
                if data.get("ok"):
                    logger.info(f"Telegram bot validated: {data['result']['username']}")
                    return True
                else:
                    logger.error(f"Telegram validation failed: {data.get('description')}")
                    return False
        except Exception as e:
            logger.error(f"Telegram validation error: {e}")
            return False
    
    def publish_post(
        self,
        content: PostContent,
        credentials: PlatformCredentials,
    ) -> PostResult:
        """
        Publish content to a Telegram channel.
        
        Supports:
        - Text-only messages
        - Messages with photos
        - Messages with videos
        """
        try:
            # Validate content
            is_valid, error_msg = self.validate_content(content)
            if not is_valid:
                return PostResult(
                    success=False,
                    error_message=error_msg,
                    diagnostics=f"Content validation failed"
                )
            
            # Get channel ID
            try:
                channel_id = self._get_channel_id(credentials)
            except ValueError as e:
                return PostResult(
                    success=False,
                    error_message=str(e),
                    diagnostics="Channel ID not configured"
                )
            
            # Determine which API method to use based on content
            if content.image_path or content.image_url:
                return self._send_photo(content, credentials, channel_id)
            elif content.video_path or content.video_url:
                return self._send_video(content, credentials, channel_id)
            else:
                return self._send_message(content, credentials, channel_id)
        
        except Exception as e:
            logger.error(f"Telegram publish error: {e}", exc_info=True)
            return PostResult(
                success=False,
                error_message=str(e),
                diagnostics=f"Unexpected error: {type(e).__name__}"
            )
    
    def _send_message(
        self,
        content: PostContent,
        credentials: PlatformCredentials,
        channel_id: str,
    ) -> PostResult:
        """Send a text-only message"""
        try:
            url = self._get_api_url(credentials.access_token, "sendMessage")
            
            payload = {
                "chat_id": channel_id,
                "text": content.text,
                "parse_mode": "HTML",  # Support HTML formatting
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload)
                data = response.json()
                
                if data.get("ok"):
                    message_id = data["result"]["message_id"]
                    logger.info(f"Telegram message sent: {message_id}")
                    return PostResult(
                        success=True,
                        platform_post_id=str(message_id),
                        diagnostics=f"Sent to {channel_id}"
                    )
                else:
                    error_desc = data.get("description", "Unknown error")
                    logger.error(f"Telegram sendMessage failed: {error_desc}")
                    return PostResult(
                        success=False,
                        error_message=error_desc,
                        diagnostics=f"API error code: {data.get('error_code')}"
                    )
        
        except Exception as e:
            logger.error(f"Telegram sendMessage exception: {e}")
            return PostResult(
                success=False,
                error_message=str(e),
                diagnostics="Exception during message send"
            )
    
    def _send_photo(
        self,
        content: PostContent,
        credentials: PlatformCredentials,
        channel_id: str,
    ) -> PostResult:
        """Send a message with a photo"""
        try:
            url = self._get_api_url(credentials.access_token, "sendPhoto")
            
            # Prepare photo (either URL or file upload)
            photo_source = content.image_url or content.image_path
            
            if content.image_path and Path(content.image_path).exists():
                # Upload from local file
                with open(content.image_path, 'rb') as photo_file:
                    files = {'photo': photo_file}
                    data = {
                        'chat_id': channel_id,
                        'caption': content.text[:1024],  # Caption limit
                        'parse_mode': 'HTML',
                    }
                    
                    with httpx.Client(timeout=60.0) as client:
                        response = client.post(url, data=data, files=files)
                        result = response.json()
            else:
                # Use URL
                payload = {
                    "chat_id": channel_id,
                    "photo": photo_source,
                    "caption": content.text[:1024],
                    "parse_mode": "HTML",
                }
                
                with httpx.Client(timeout=60.0) as client:
                    response = client.post(url, json=payload)
                    result = response.json()
            
            if result.get("ok"):
                message_id = result["result"]["message_id"]
                logger.info(f"Telegram photo sent: {message_id}")
                return PostResult(
                    success=True,
                    platform_post_id=str(message_id),
                    diagnostics=f"Photo sent to {channel_id}"
                )
            else:
                error_desc = result.get("description", "Unknown error")
                logger.error(f"Telegram sendPhoto failed: {error_desc}")
                return PostResult(
                    success=False,
                    error_message=error_desc,
                    diagnostics=f"API error code: {result.get('error_code')}"
                )
        
        except Exception as e:
            logger.error(f"Telegram sendPhoto exception: {e}")
            return PostResult(
                success=False,
                error_message=str(e),
                diagnostics="Exception during photo send"
            )
    
    def _send_video(
        self,
        content: PostContent,
        credentials: PlatformCredentials,
        channel_id: str,
    ) -> PostResult:
        """Send a message with a video"""
        try:
            url = self._get_api_url(credentials.access_token, "sendVideo")
            
            video_source = content.video_url or content.video_path
            
            if content.video_path and Path(content.video_path).exists():
                # Upload from local file
                with open(content.video_path, 'rb') as video_file:
                    files = {'video': video_file}
                    data = {
                        'chat_id': channel_id,
                        'caption': content.text[:1024],
                        'parse_mode': 'HTML',
                    }
                    
                    with httpx.Client(timeout=120.0) as client:  # Videos take longer
                        response = client.post(url, data=data, files=files)
                        result = response.json()
            else:
                # Use URL
                payload = {
                    "chat_id": channel_id,
                    "video": video_source,
                    "caption": content.text[:1024],
                    "parse_mode": "HTML",
                }
                
                with httpx.Client(timeout=120.0) as client:
                    response = client.post(url, json=payload)
                    result = response.json()
            
            if result.get("ok"):
                message_id = result["result"]["message_id"]
                logger.info(f"Telegram video sent: {message_id}")
                return PostResult(
                    success=True,
                    platform_post_id=str(message_id),
                    diagnostics=f"Video sent to {channel_id}"
                )
            else:
                error_desc = result.get("description", "Unknown error")
                logger.error(f"Telegram sendVideo failed: {error_desc}")
                return PostResult(
                    success=False,
                    error_message=error_desc,
                    diagnostics=f"API error code: {result.get('error_code')}"
                )
        
        except Exception as e:
            logger.error(f"Telegram sendVideo exception: {e}")
            return PostResult(
                success=False,
                error_message=str(e),
                diagnostics="Exception during video send"
            )
    
    def upload_media(
        self,
        media_path: str,
        media_type: str,
        credentials: PlatformCredentials,
    ) -> MediaUploadResult:
        """
        Telegram doesn't require separate media upload.
        Media is uploaded as part of the sendPhoto/sendVideo call.
        """
        return MediaUploadResult(
            success=True,
            media_id=media_path,
            media_url=media_path,
        )
    
    def get_post_analytics(
        self,
        platform_post_id: str,
        credentials: PlatformCredentials,
    ) -> dict:
        """
        Telegram Bot API doesn't provide analytics for channel posts.
        Views count can be retrieved for channel posts, but detailed metrics are not available.
        
        For channel posts, we can only get basic message info.
        """
        try:
            channel_id = self._get_channel_id(credentials)
            url = self._get_api_url(credentials.access_token, "getChat")
            
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params={"chat_id": channel_id})
                data = response.json()
                
                if data.get("ok"):
                    # Telegram doesn't provide detailed analytics via Bot API
                    # This would require Telegram Analytics API or MTProto
                    return {
                        "impressions": 0,  # Not available
                        "clicks": 0,       # Not available
                        "comments": 0,     # Not available
                        "shares": 0,       # Not available
                        "note": "Telegram Bot API does not provide post analytics"
                    }
        
        except Exception as e:
            logger.error(f"Telegram analytics error: {e}")
        
        return {
            "impressions": 0,
            "clicks": 0,
            "comments": 0,
            "shares": 0,
        }
    
    def refresh_access_token(
        self,
        credentials: PlatformCredentials,
    ) -> Optional[PlatformCredentials]:
        """
        Telegram bot tokens don't expire and don't need refreshing.
        """
        return credentials
