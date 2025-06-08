from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
import os
import uuid
import shutil
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.crud.social_post import crud_social_post
from backend.models.user import User
from backend.pydanticschemas.social_post import SocialMediaPostCreate, SocialMediaPostSchema
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/admin/social-posts", tags=["Social Media"])

# Directory to store uploaded media
UPLOAD_DIR = os.path.join("frontend/static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=List[SocialMediaPostSchema])
async def list_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return crud_social_post.get_all(db)

@router.post("/", response_model=SocialMediaPostSchema, status_code=status.HTTP_201_CREATED)
async def create_post(
    platform: str = Form(...),
    content: str = Form(...),
    content_type: str = Form(...),
    scheduled_at: Optional[str] = Form(None),
    image: UploadFile | None = File(None),
    video: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    image_url = None
    video_url = None

    if image and image.filename:
        file_ext = os.path.splitext(image.filename)[1]
        unique_name = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = f"/static/uploads/{unique_name}"

    if video and video.filename:
        file_ext = os.path.splitext(video.filename)[1]
        unique_name = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        video_url = f"/static/uploads/{unique_name}"

    post_data = SocialMediaPostCreate(
        platform=platform,
        content=content,
        content_type=content_type,
        image_url=image_url,
        video_url=video_url,
        scheduled_at=scheduled_at,
    )
    return crud_social_post.create(db, post_data)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    crud_social_post.delete(db, post_id)
    return {"detail": f"Post {post_id} deleted"}

