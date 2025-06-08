from sqlalchemy.orm import Session
from fastapi import HTTPException

from backend.models.category import Category
from backend.pydanticschemas.category import CategoryCreate

class CRUDCategory:
    def __init__(self, model):
        self.model = model

    def create(self, db: Session, obj_in: CategoryCreate) -> Category:
        data = obj_in.model_dump()
        record = self.model(**data)
        db.add(record)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        db.refresh(record)
        return record

    def get_all(self, db: Session):
        return db.query(self.model).order_by(self.model.name).all()

crud_category = CRUDCategory(Category)
