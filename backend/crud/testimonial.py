from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.models.testimonial import Testimonial
from backend.pydanticschemas.testimonial import TestimonialCreate, TestimonialUpdate

class CRUDTestimonial:
    def __init__(self, model):
        self.model = model

    def create(self, db: Session, obj_in: TestimonialCreate) -> Testimonial:
        data = obj_in.model_dump()
        record = self.model(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get_all(self, db: Session):
        return db.query(self.model).all()

    def get_approved(self, db: Session):
        return db.query(self.model).filter(self.model.is_approved == True).all()

    def update(self, db: Session, testimonial_id: int, obj_in: TestimonialUpdate) -> Testimonial:
        record = db.query(self.model).filter(self.model.id == testimonial_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Testimonial not found")
        for key, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(record, key, value)
        db.commit()
        db.refresh(record)
        return record

    def delete(self, db: Session, testimonial_id: int) -> Testimonial:
        record = db.query(self.model).filter(self.model.id == testimonial_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Testimonial not found")
        db.delete(record)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        return record

crud_testimonial = CRUDTestimonial(Testimonial)
