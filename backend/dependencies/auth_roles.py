# backend/dependencies/auth_roles.py
from fastapi import Depends, HTTPException, status
from backend.routers.auth import get_current_user
from backend.models.user import User

def require_role(allowed_roles: list[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough privileges"
            )
        return current_user
    return role_checker