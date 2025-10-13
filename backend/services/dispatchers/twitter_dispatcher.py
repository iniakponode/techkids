"""
X (Twitter) API v2 Dispatcher

Implements posting to X/Twitter using the Twitter API v2 with OAuth 1.0a authentication.

Documentation: https://developer.twitter.com/en/docs/twitter-api
API Reference: https://developer.twitter.com/en/docs/twitter-api/tweets/manage-tweets/introduction
"""

import logging
import hashlib
import hmac
import time
import secrets
from urllib.parse import quote
from typing import Optional
import httpx
from pathlib import Path
import base64

from backend.services.dispatchers.base import (
    BasePlatformDispatcher,
    MediaUploadResult,
    PlatformCredentials,
    PostContent,
    PostResult,
)

logger = logging.getLogger(__name__)

TWITTER_API_BASE = "https://api.twitter.com"
TWITTER_UPLOAD_BASE = "https://upload.twitter.com"


class TwitterDispatcher(BasePlatformDispatcher):
    """
    Dispatcher for posting to X/Twitter via Twitter API v2.
    
    Setup:
    1. Create a Twitter Developer account at https://developer.twitter.com
    2. Create a project and app
    3. Generate API keys and tokens
    4. Store credentials:
       - access_token: API Key (Consumer Key)
       - refresh_token: API Secret (Consumer Secret)
       - metadata: {"access_token": "User Access Token", "access_token_secret": "User Access Token Secret"}
    
    Authentication: OAuth 1.0a (required for posting)
    """
    
    @property
    def platform_name(self) -> str:
        return "twitter"
    
    @property
    def supports_scheduled_posts(self) -> bool:
        # Twitter doesn't support native scheduled posts via API
        # We handle scheduling ourselves
        return False
    
    @property
    def max_text_length(self) -> int:
        # Twitter extended limit (with Twitter Blue/Premium)
        # Standard limit is 280, but we'll use 280 to be safe
        return 280
    
    @property
    def supported_content_types(self) -> list[str]:
        return ["Post"]
    
    def _get_oauth_credentials(self, credentials: PlatformCredentials) -> dict[str, str]:
        """Extract OAuth 1.0a credentials from PlatformCredentials"""
        # API Key (Consumer Key)
        api_key = credentials.access_token
        # API Secret (Consumer Secret)
        api_secret = credentials.refresh_token
        
        # User Access Token and Secret from metadata
        metadata = credentials.metadata or {}
        if isinstance(metadata, dict):
            access_token = metadata.get('access_token')
            access_token_secret = metadata.get('access_token_secret')
        else:
            raise ValueError("Twitter credentials metadata must contain access_token and access_token_secret")
        
        if not all([api_key, api_secret, access_token, access_token_secret]):
            raise ValueError("Missing required Twitter OAuth credentials")
        
        return {
            'api_key': api_key,
            'api_secret': api_secret,
            'access_token': access_token,
            'access_token_secret': access_token_secret
        }
    
    def _generate_oauth_signature(
        self,
        method: str,
        url: str,
        params: dict[str, str],
        api_secret: str,
        token_secret: str
    ) -> str:
        """Generate OAuth 1.0a signature"""
        # Sort parameters
        sorted_params = sorted(params.items())
        param_string = '&'.join([f"{quote(str(k), safe='')}={quote(str(v), safe='')}" for k, v in sorted_params])
        
        # Create signature base string
        signature_base = f"{method}&{quote(url, safe='')}&{quote(param_string, safe='')}"
        
        # Create signing key
        signing_key = f"{quote(api_secret, safe='')}&{quote(token_secret, safe='')}"
        
        # Generate signature
        signature = hmac.new(
            signing_key.encode('utf-8'),
            signature_base.encode('utf-8'),
            hashlib.sha1
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    def _build_oauth_header(
        self,
        method: str,
        url: str,
        oauth_creds: dict[str, str],
        extra_params: dict[str, str] = None
    ) -> str:
        """Build OAuth 1.0a Authorization header"""
        # OAuth parameters
        oauth_params = {
            'oauth_consumer_key': oauth_creds['api_key'],
            'oauth_token': oauth_creds['access_token'],
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': secrets.token_hex(16),
            'oauth_version': '1.0'
        }
        
        # Combine with extra params for signature
        all_params = {**oauth_params, **(extra_params or {})}
        
        # Generate signature
        signature = self._generate_oauth_signature(
            method,
            url,
            all_params,
            oauth_creds['api_secret'],
            oauth_creds['access_token_secret']
        )
        
        oauth_params['oauth_signature'] = signature
        
        # Build header
        header_params = ', '.join([f'{quote(k)}="{quote(str(v))}"' for k, v in sorted(oauth_params.items())])
        return f"OAuth {header_params}"
    
    def validate_credentials(self, credentials: PlatformCredentials) -> bool:
        """
        Validate Twitter credentials by calling the verify_credentials endpoint.
        
        Returns:
            True if credentials are valid
        """
        try:
            oauth_creds = self._get_oauth_credentials(credentials)
            
            # Use Twitter API v1.1 for credential verification (v2 doesn't have this endpoint)
            url = "https://api.twitter.com/1.1/account/verify_credentials.json"
            
            auth_header = self._build_oauth_header("GET", url, oauth_creds)
            
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    url,
                    headers={"Authorization": auth_header}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Twitter credentials validated: @{data.get('screen_name')}")
                    return True
                else:
                    logger.error(f"Twitter validation failed: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Twitter validation error: {e}", exc_info=True)
            return False
    
    def publish_post(
        self,
        content: PostContent,
        credentials: PlatformCredentials,
    ) -> PostResult:
        """
        Publish content to X/Twitter.
        
        Supports:
        - Text-only tweets
        - Tweets with images (up to 4)
        - Tweets with videos (1 per tweet)
        """
        try:
            logger.info(f"Twitter publish_post called with content_type={content.content_type}, text_length={len(content.text)}, has_image={bool(content.image_path or content.image_url)}, has_video={bool(content.video_path or content.video_url)}")
            
            # Validate content
            is_valid, error_msg = self.validate_content(content)
            if not is_valid:
                logger.error(f"Twitter content validation failed: {error_msg}")
                return PostResult(
                    success=False,
                    error_message=error_msg,
                    diagnostics="Content validation failed"
                )
            
            logger.info("Twitter content validation passed")
            
            # Get OAuth credentials
            try:
                oauth_creds = self._get_oauth_credentials(credentials)
                logger.info("Twitter OAuth credentials extracted successfully")
            except ValueError as e:
                logger.error(f"Twitter credential extraction failed: {e}")
                return PostResult(
                    success=False,
                    error_message=str(e),
                    diagnostics="Invalid credentials format"
                )
            
            # Upload media if present
            media_ids = []
            if content.image_path or content.image_url:
                logger.info("Twitter: uploading image")
                media_result = self._upload_media(content.image_path or content.image_url, "image", oauth_creds)
                if not media_result.success:
                    return PostResult(
                        success=False,
                        error_message=media_result.error_message,
                        diagnostics="Image upload failed"
                    )
                media_ids.append(media_result.media_id)
            
            if content.video_path or content.video_url:
                logger.info("Twitter: uploading video")
                media_result = self._upload_media(content.video_path or content.video_url, "video", oauth_creds)
                if not media_result.success:
                    return PostResult(
                        success=False,
                        error_message=media_result.error_message,
                        diagnostics="Video upload failed"
                    )
                media_ids.append(media_result.media_id)
            
            # Create tweet
            logger.info("Twitter: creating tweet")
            return self._create_tweet(content.text, media_ids, oauth_creds)
        
        except Exception as e:
            logger.error(f"Twitter publish error: {e}", exc_info=True)
            return PostResult(
                success=False,
                error_message=str(e),
                diagnostics=f"Unexpected error: {type(e).__name__}"
            )
    
    def _upload_media(
        self,
        media_path_or_url: str,
        media_type: str,
        oauth_creds: dict[str, str]
    ) -> MediaUploadResult:
        """
        Upload media to Twitter using the upload API.
        
        Twitter uses a chunked upload process for larger files.
        For simplicity, we'll use simple upload for smaller files.
        """
        try:
            # Read media file
            if media_path_or_url.startswith('http'):
                # Download from URL
                with httpx.Client(timeout=30.0) as client:
                    response = client.get(media_path_or_url)
                    if response.status_code != 200:
                        return MediaUploadResult(
                            success=False,
                            error_message=f"Failed to download media from {media_path_or_url}"
                        )
                    media_data = response.content
            else:
                # Read from local file
                path = Path(media_path_or_url)
                if not path.exists():
                    return MediaUploadResult(
                        success=False,
                        error_message=f"Media file not found: {media_path_or_url}"
                    )
                media_data = path.read_bytes()
            
            # Upload using Twitter Upload API v1.1
            url = f"{TWITTER_UPLOAD_BASE}/1.1/media/upload.json"
            
            auth_header = self._build_oauth_header("POST", url, oauth_creds)
            
            # Determine media category
            media_category = "tweet_image" if media_type == "image" else "tweet_video"
            
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    url,
                    headers={"Authorization": auth_header},
                    files={"media": media_data},
                    data={"media_category": media_category}
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    media_id = str(data['media_id_string'])
                    logger.info(f"Twitter media uploaded: {media_id}")
                    return MediaUploadResult(
                        success=True,
                        media_id=media_id
                    )
                else:
                    error_msg = response.text
                    logger.error(f"Twitter media upload failed: {response.status_code} - {error_msg}")
                    return MediaUploadResult(
                        success=False,
                        error_message=f"Upload failed: {error_msg}"
                    )
        
        except Exception as e:
            logger.error(f"Twitter media upload exception: {e}", exc_info=True)
            return MediaUploadResult(
                success=False,
                error_message=str(e)
            )
    
    def _create_tweet(
        self,
        text: str,
        media_ids: list[str],
        oauth_creds: dict[str, str]
    ) -> PostResult:
        """Create a tweet using Twitter API v2"""
        try:
            url = f"{TWITTER_API_BASE}/2/tweets"
            
            # Build tweet payload
            payload = {"text": text}
            if media_ids:
                payload["media"] = {"media_ids": media_ids}
            
            auth_header = self._build_oauth_header("POST", url, oauth_creds)
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    url,
                    headers={
                        "Authorization": auth_header,
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    tweet_id = data['data']['id']
                    logger.info(f"Twitter tweet created: {tweet_id}")
                    return PostResult(
                        success=True,
                        platform_post_id=tweet_id,
                        diagnostics=f"Tweet posted successfully"
                    )
                else:
                    error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    error_msg = error_data.get('detail') or error_data.get('title') or response.text
                    logger.error(f"Twitter tweet creation failed: {response.status_code} - {error_msg}")
                    return PostResult(
                        success=False,
                        error_message=error_msg,
                        diagnostics=f"API error code: {response.status_code}"
                    )
        
        except Exception as e:
            logger.error(f"Twitter create tweet exception: {e}", exc_info=True)
            return PostResult(
                success=False,
                error_message=str(e),
                diagnostics="Exception during tweet creation"
            )
    
    def upload_media(
        self,
        media_path: str,
        media_type: str,
        credentials: PlatformCredentials,
    ) -> MediaUploadResult:
        """
        Upload media file to Twitter.
        This is a public method that wraps _upload_media.
        """
        try:
            oauth_creds = self._get_oauth_credentials(credentials)
            return self._upload_media(media_path, media_type, oauth_creds)
        except Exception as e:
            logger.error(f"Twitter media upload error: {e}", exc_info=True)
            return MediaUploadResult(
                success=False,
                error_message=str(e)
            )
    
    def get_post_analytics(
        self,
        platform_post_id: str,
        credentials: PlatformCredentials,
    ) -> dict:
        """
        Get analytics for a specific tweet.
        
        Note: Twitter API v2 analytics require elevated access.
        For now, we return basic success status.
        """
        logger.info(f"Twitter analytics not yet implemented for post {platform_post_id}")
        return {
            "impressions": 0,
            "clicks": 0,
            "comments": 0,
            "shares": 0,
            "note": "Analytics not yet implemented"
        }
    
    def refresh_access_token(
        self,
        credentials: PlatformCredentials,
    ) -> Optional[PlatformCredentials]:
        """
        Refresh access token.
        
        Note: Twitter OAuth 1.0a tokens don't expire, so no refresh needed.
        OAuth 2.0 tokens would need refresh, but we're using OAuth 1.0a.
        """
        logger.info("Twitter OAuth 1.0a tokens don't require refresh")
        return credentials
    
    def delete_post(
        self,
        post_id: str,
        credentials: PlatformCredentials,
    ) -> PostResult:
        """
        Delete a tweet by ID.
        """
        try:
            oauth_creds = self._get_oauth_credentials(credentials)
            url = f"{TWITTER_API_BASE}/2/tweets/{post_id}"
            
            auth_header = self._build_oauth_header("DELETE", url, oauth_creds)
            
            with httpx.Client(timeout=30.0) as client:
                response = client.delete(
                    url,
                    headers={"Authorization": auth_header}
                )
                
                if response.status_code in [200, 204]:
                    logger.info(f"Twitter tweet deleted: {post_id}")
                    return PostResult(
                        success=True,
                        platform_post_id=post_id,
                        diagnostics="Tweet deleted successfully"
                    )
                else:
                    error_msg = response.text
                    logger.error(f"Twitter delete failed: {response.status_code} - {error_msg}")
                    return PostResult(
                        success=False,
                        error_message=error_msg,
                        diagnostics=f"Delete failed with status {response.status_code}"
                    )
        except Exception as e:
            logger.error(f"Twitter delete exception: {e}", exc_info=True)
            return PostResult(
                success=False,
                error_message=str(e),
                diagnostics="Exception during delete"
            )
