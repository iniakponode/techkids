"""
Admin Courses Router

This module provides endpoints for admin users to add courses.
Admins can either:
  - Upload an image file from their local computer, or
  - Provide an online image URL.
  
Uploaded images are saved to the local filesystem (e.g. /static/uploads/),
and the Course record stores the corresponding URL.

Endpoints:
  - POST /admin/courses/add: Add a new course.
"""

import os
import uuid
import shutil
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, File, status
from sqlalchemy.orm import Session

from backend.crud.course import crud_course

from backend.core.database import get_db
from backend.models.course import Course
from backend.models.user import User
from backend.pydanticschemas.course import CourseSchema, CourseUpdate
from backend.routers.auth import get_current_user

logger = logging.getLogger(__name__)

# Configure logging (if not already configured elsewhere)
# if not logger.handlers:
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/courses", tags=["Admin Courses"])

# Directory to store uploaded images
UPLOAD_DIR = os.path.join("frontend/static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/add", response_model=CourseSchema)
async def add_course(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str | None = Form(None),
    age_group: str = Form(...),
    duration: str = Form(...),
    preview_link: str | None = Form(None),
    rating: Optional[float] = Form(0.0),
    image_url: Optional[str] = Form(None),
    image_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Add a new course.

    Admins can either upload an image file or provide an image URL.

    Parameters:
      - title (str): Title of the course.
      - description (str): Detailed description.
      - price (float): Price of the course.
      - age_group (str): Target age group.
      - duration (str): Course duration.
      - rating (float, optional): Initial rating (default 0.0).
      - image_url (str, optional): An online image URL.
      - image_file (UploadFile, optional): An image file uploaded from local computer.

    Returns:
      CourseResponse: The newly created course details.

    Raises:
      HTTPException: 500 if an error occurs during file saving or DB commit.
    """
    # If an image file is provided, save it and generate its URL.
    if image_file:
        try:
            file_extension = os.path.splitext(image_file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image_file.file, buffer)
            # static files are served at "/static/uploads/"
            image_url = f"/static/uploads/{unique_filename}"
        except Exception as e:
            logger.error(f"Error saving uploaded image: {str(e)}")
            raise HTTPException(status_code=500, detail="Error saving uploaded image.")

    course_data = {
        "title": title,
        "description": description,
        "price": price,
        "category": category,
        "age_group": age_group,
        "duration": duration,
        "preview_link": preview_link,
        "rating": rating,
        "image_url": image_url,
    }

    try:
        new_course = Course(**course_data)
        db.add(new_course)
        db.commit()
        db.refresh(new_course)
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating course: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating course.")

    return new_course

# Delete a Course
@router.delete("/delete/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """
    Delete a course by ID.
    """
    crud_course.delete(db=db, course_id=course_id)
    return {"message": f"Course with ID {course_id} successfully deleted."}

@router.put("/{course_id}", response_model=CourseUpdate)
async def update_course(
    course_id: int,
    title: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    category: str = Form(None),
    age_group: str = Form(None),
    duration: str = Form(None),
    preview_link: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    if title:
        db_course.title = title
        
    if description:
        db_course.description = description
        
    if price:
        db_course.price = price

    if category is not None:
        db_course.category = category

    if age_group:
        db_course.age_group = age_group
        
    if duration:
        db_course.duration = duration

    if preview_link is not None:
        db_course.preview_link = preview_link

    if image:
        upload_dir = os.path.join("frontend/static", "uploads")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        file_path = os.path.join(upload_dir, image.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        db_course.image_url = f"/static/uploads/{image.filename}"

    try:
        db.flush()
        logger.info(f"db_course before commit: {db_course}")
        db.commit()
        logger.info("Database commit successful.")
        logger.info(f"db_course after commit: {db_course}")
        updated_course = db.query(Course).filter(Course.id == course_id).first()
        logger.info(f"updated_course age_group: {updated_course.age_group}")
        logger.info(f"Course {course_id} updated successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating course {course_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error updating course.")
    return db_course