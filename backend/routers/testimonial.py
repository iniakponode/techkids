from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.crud.testimonial import crud_testimonial
from backend.pydanticschemas.testimonial import TestimonialCreate, TestimonialSchema, TestimonialUpdate
from backend.routers.auth import get_current_user
from backend.models.user import User

router = APIRouter()

@router.post("/testimonials", response_model=TestimonialSchema, status_code=status.HTTP_201_CREATED)
def create_testimonial(data: TestimonialCreate, db: Session = Depends(get_db)):
    return crud_testimonial.create(db, obj_in=data)

@router.get("/testimonials/approved", response_model=list[TestimonialSchema])
def get_approved(db: Session = Depends(get_db)):
    return crud_testimonial.get_approved(db)

@router.get("/admin/testimonials", response_model=list[TestimonialSchema])
def get_all(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return crud_testimonial.get_all(db)

@router.patch("/admin/testimonials/{testimonial_id}", response_model=TestimonialSchema)
def update_testimonial(testimonial_id: int, data: TestimonialUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return crud_testimonial.update(db, testimonial_id, data)


@router.delete("/admin/testimonials/{testimonial_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_testimonial(testimonial_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    crud_testimonial.delete(db, testimonial_id)
    return {"detail": f"Testimonial {testimonial_id} deleted"}
