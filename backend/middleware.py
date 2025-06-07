from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.models import BlacklistedToken

async def blacklist_middleware(request: Request, call_next):
    access_token = request.cookies.get("access_token")
    if access_token:
        db: Session = SessionLocal()
        blacklisted = db.query(BlacklistedToken).filter(BlacklistedToken.token == access_token).first()
        db.close()
        if blacklisted:
            return JSONResponse(status_code=401, content={"detail": "Token blacklisted"})

    response = await call_next(request)
    return response