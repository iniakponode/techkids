from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional

from backend.models.social_post import SocialMediaPost
from backend.pydanticschemas.social_post import SocialMediaPostCreate

class CRUDSocialPost:
    def __init__(self, model):
        self.model = model

    def create(self, db: Session, obj_in: SocialMediaPostCreate) -> SocialMediaPost:
        post = self.model(**obj_in.model_dump())
        db.add(post)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        db.refresh(post)
        return post

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[SocialMediaPost]:
        query = db.query(self.model)
        query = query.order_by(self.model.scheduled_at.is_(None), self.model.scheduled_at, self.model.created_at.desc())
        return query.offset(skip).limit(limit).all()

    def delete(self, db: Session, post_id: int) -> Optional[SocialMediaPost]:
        post = db.query(self.model).filter(self.model.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        db.delete(post)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        return post

crud_social_post = CRUDSocialPost(SocialMediaPost)

