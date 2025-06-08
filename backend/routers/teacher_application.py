from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.pydanticschemas.teacher_application import TeacherApplicationCreate
from backend.crud.teacher_application import crud_teacher_application

router = APIRouter()

@router.post("/teacher-applications", status_code=status.HTTP_201_CREATED)
async def submit_application(request: Request, db: Session = Depends(get_db)):
    """Create a teacher application from JSON or form data."""
    if request.headers.get("content-type", "").startswith("application/json"):
        payload = await request.json()
    else:
        form = await request.form()
        payload = dict(form)
    data = TeacherApplicationCreate(**payload)
    return crud_teacher_application.create(db, obj_in=data)
