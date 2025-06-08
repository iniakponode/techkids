import os
import shutil
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from typing import List
from backend.models.course import Course
from backend.models.user import User
from backend.pydanticschemas.course import CourseCreate, CourseSchema, CourseUpdate
from backend.core.database import get_db
from backend.crud.course import crud_course
from backend.dependencies.auth_roles import require_role
from backend.routers.auth import get_current_user

router = APIRouter()


# Create a Course
@router.post("/add-course", response_model=CourseSchema, status_code=status.HTTP_201_CREATED)
def create_course(course: CourseCreate, 
                  db: Session = Depends(get_db),
                #   current_user: User = Depends(require_role(["admin"]))
                  ):
    """
    Create a new course.
    """
    
    # course_data = course.model_dump()
    # course_data["image_url"] = str(course_data["image_url"]) if course_data["image_url"] else None  # ✅ Convert HttpUrl to str
    
    return crud_course.create(db=db, obj_in=course)


# Get all Courses
@router.get("/", response_model=List[CourseSchema])
def get_courses(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    category: str | None = None,
    age: str | None = None,
    price_min: str | None = None,
    price_max: str | None = None,
):
    """Retrieve courses with optional filtering."""
    price_min_val = float(price_min) if price_min not in (None, "") else None
    price_max_val = float(price_max) if price_max not in (None, "") else None
    if search or category or age or price_min_val is not None or price_max_val is not None:
        return crud_course.get_filtered(
            db=db,
            search=search,
            category=category,
            age=age,
            price_min=price_min_val,
            price_max=price_max_val,
        )
    return crud_course.get_all(db=db, skip=skip, limit=limit)


# Get a Course by ID
@router.get("/{course_id}", response_model=CourseSchema)
def get_course_by_id(course_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a course by ID.
    """
    course = crud_course.get_by_id(db=db, course_id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found.",
        )
    return course




# Update a Course
# @router.put("/{course_id}", response_model=CourseSchema)
# def update_course(course_id: int, updated_course: CourseCreate, db: Session = Depends(get_db)):
#     """
#     Update a course by ID.
#     """
#     return crud_course.update(db=db, course_id=course_id, obj_in=updated_course)


