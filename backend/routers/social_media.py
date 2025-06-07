from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.crud.social_post import crud_social_post
from backend.models.user import User
from backend.pydanticschemas.social_post import SocialMediaPostCreate, SocialMediaPostSchema
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/admin/social-posts", tags=["Social Media"])

@router.get("/", response_model=List[SocialMediaPostSchema])
async def list_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return crud_social_post.get_all(db)

@router.post("/", response_model=SocialMediaPostSchema, status_code=status.HTTP_201_CREATED)
async def create_post(post_in: SocialMediaPostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return crud_social_post.create(db, post_in)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    crud_social_post.delete(db, post_id)
    return {"detail": f"Post {post_id} deleted"}

