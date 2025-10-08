from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.models.blacklisted_tokens import BlacklistedToken


async def blacklist_middleware(request: Request, call_next):
    access_token = request.cookies.get("access_token")
    db: Session | None = None

    try:
        if access_token:
            db = SessionLocal()
            blacklisted = (
                db.query(BlacklistedToken)
                .filter(BlacklistedToken.token == access_token)
                .first()
            )
            if blacklisted:
                return JSONResponse(status_code=401, content={"detail": "Token blacklisted"})

        response = await call_next(request)
        return response
    finally:
        if db is not None:
            db.close()