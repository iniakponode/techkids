from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.pydanticschemas.teacher_application import TeacherApplicationCreate
from backend.crud.teacher_application import crud_teacher_application

router = APIRouter()

@router.post("/teacher-applications", status_code=status.HTTP_201_CREATED)
def submit_application(data: TeacherApplicationCreate, db: Session = Depends(get_db)):
    """Create a teacher application."""
    return crud_teacher_application.create(db, obj_in=data)
