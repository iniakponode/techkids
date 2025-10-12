"""
Enhanced authentication error responses with user-friendly messages
"""

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any


class AuthError:
    """Standardized authentication error messages and responses"""
    
    # Standard error messages
    SESSION_EXPIRED = "Your session has expired. Please log in again to continue."
    INVALID_TOKEN = "Your session is invalid. Please log in again."
    TOKEN_VALIDATION_FAILED = "Could not validate your session. Please log in again."
    USER_NOT_FOUND = "Your account could not be found. Please log in again."
    INSUFFICIENT_PERMISSIONS = "You don't have permission to access this resource."
    ACCOUNT_DISABLED = "Your account has been disabled. Please contact support."
    CSRF_TOKEN_MISMATCH = "Security token mismatch. Please refresh the page and try again."
    
    @staticmethod
    def session_expired(detail: Optional[str] = None) -> HTTPException:
        """Session expired error"""
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail or AuthError.SESSION_EXPIRED,
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    @staticmethod
    def invalid_token(detail: Optional[str] = None) -> HTTPException:
        """Invalid token error"""
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail or AuthError.INVALID_TOKEN,
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    @staticmethod
    def user_not_found(detail: Optional[str] = None) -> HTTPException:
        """User not found error"""
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail or AuthError.USER_NOT_FOUND,
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    @staticmethod
    def insufficient_permissions(detail: Optional[str] = None) -> HTTPException:
        """Insufficient permissions error"""
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail or AuthError.INSUFFICIENT_PERMISSIONS
        )
    
    @staticmethod
    def csrf_mismatch(detail: Optional[str] = None) -> HTTPException:
        """CSRF token mismatch error"""
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail or AuthError.CSRF_TOKEN_MISMATCH
        )
    
    @staticmethod
    def account_disabled(detail: Optional[str] = None) -> HTTPException:
        """Account disabled error"""
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail or AuthError.ACCOUNT_DISABLED
        )


class AuthResponse:
    """Helper for creating standardized authentication response formats"""
    
    @staticmethod
    def success(message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Success response format"""
        response = {"success": True, "message": message}
        if data:
            response.update(data)
        return response
    
    @staticmethod
    def error(message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Error response format"""
        response = {
            "success": False,
            "error": message
        }
        if error_code:
            response["error_code"] = error_code
        if details:
            response["details"] = details
        return response
    
    @staticmethod
    def login_success(user, redirect_url: Optional[str] = None, additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Standardized login success response"""
        response = {
            "success": True,
            "message": "Login successful",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "name": getattr(user, 'name', None)
            }
        }
        
        if redirect_url:
            response["redirect_url"] = redirect_url
            
        if additional_data:
            response.update(additional_data)
            
        return response
    
    @staticmethod
    def session_check_success(user) -> Dict[str, Any]:
        """Session check success response"""
        return {
            "authenticated": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "name": getattr(user, 'name', None)
            },
            "session_valid": True
        }


def create_auth_error_response(
    status_code: int,
    message: str,
    error_code: Optional[str] = None,
    user_message: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None
) -> JSONResponse:
    """
    Create a standardized authentication error response
    
    Args:
        status_code: HTTP status code
        message: Technical error message
        error_code: Optional error code for frontend handling
        user_message: User-friendly message (defaults to message)
        headers: Optional additional headers
    """
    content = {
        "detail": user_message or message,
        "error_code": error_code,
        "type": "authentication_error"
    }
    
    response_headers = {"WWW-Authenticate": "Bearer"}
    if headers:
        response_headers.update(headers)
    
    return JSONResponse(
        status_code=status_code,
        content=content,
        headers=response_headers
    )