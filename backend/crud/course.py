from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException
from typing import List, Optional
from backend.models.course import Course
from backend.pydanticschemas.course import CourseCreate, CourseSchema
from backend.models.registration import Registration
import logging

logger = logging.getLogger(__name__)


class CRUDCourse:
    """
    CRUD operations for Course.

    Methods:
    - **create**: Adds a new Course record.
    - **get_by_id**: Retrieves a Course by ID.
    - **get_all**: Retrieves all Courses.
    - **update**: Updates a Course record.
    - **delete**: Deletes a Course record.
    """

    def __init__(self, model):
        self.model = model

    def create(self, db: Session, obj_in: CourseCreate) -> Course:
        """
        Create a new Course.
        """
        obj_data = obj_in.model_dump()
        obj_data["image_url"] = str(obj_data["image_url"]) if obj_data["image_url"] else None  # ✅ Convert HttpUrl to str

        new_course = self.model(**obj_data)
        db.add(new_course)
        try:
            db.commit()
            logger.info(f"Created Course: {obj_data['title']}")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        db.refresh(new_course)
        return new_course

    def get_by_id(self, db: Session, course_id: int) -> Optional[Course]:
        """
        Retrieve a Course by ID.
        """
        course = db.query(self.model).filter(self.model.id == course_id).first()
        if not course:
            logger.warning(f"Course with ID {course_id} not found.")
        return course

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Course]:
        """
        Retrieve all Courses.
        """
        courses = db.query(self.model).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(courses)} courses.")
        return courses

    def get_filtered(
        self,
        db: Session,
        search: str | None = None,
        category: str | None = None,
        age: str | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
    ) -> List[Course]:
        query = db.query(self.model)
        if search:
            like = f"%{search}%"
            query = query.filter(
                or_(
                    self.model.title.ilike(like),
                    self.model.category.ilike(like),
                    self.model.age_group.ilike(like),
                )
            )
        if category:
            query = query.filter(self.model.category == category)
        if age:
            like_age = f"%{age}%"
            query = query.filter(self.model.age_group.ilike(like_age))
        if price_min is not None:
            query = query.filter(self.model.price >= price_min)
        if price_max is not None:
            query = query.filter(self.model.price <= price_max)
        return query.all()

    def get_hero_course(self, db: Session) -> Optional[Course]:
        result = (
            db.query(self.model, func.count(Registration.id).label("c"))
            .outerjoin(Registration, Registration.course_id == self.model.id)
            .group_by(self.model.id)
            .order_by(func.count(Registration.id).desc())
            .first()
        )
        return result[0] if result else None

    def get_top_courses(
        self, db: Session, limit: int = 3, exclude_course_id: int | None = None
    ) -> List[Course]:
        query = (
            db.query(self.model, func.count(Registration.id).label("c"))
            .outerjoin(Registration, Registration.course_id == self.model.id)
            .group_by(self.model.id)
            .order_by(func.count(Registration.id).desc())
        )
        if exclude_course_id is not None:
            query = query.filter(self.model.id != exclude_course_id)
        results = query.limit(limit).all()
        return [r[0] for r in results]

    def update(self, db: Session, course_id: int, obj_in: CourseCreate) -> Course:
        """
        Update a Course by ID.
        """
        course = self.get_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=404, detail=f"Course with ID {course_id} not found."
            )
        for key, value in obj_in.dict().items():
            setattr(course, key, value)
        db.add(course)
        try:
            db.commit()
            logger.info(f"Updated Course with ID: {course_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating Course: {str(e)}")
            raise HTTPException(status_code=500, detail="Error updating Course.")
        db.refresh(course)
        return course

    def delete(self, db: Session, course_id: int) -> Optional[Course]:
        """
        Delete a Course by ID.
        """
        course = self.get_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=404, detail=f"Course with ID {course_id} not found."
            )
        db.delete(course)
        try:
            db.commit()
            logger.info(f"Deleted Course with ID: {course_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting Course: {str(e)}")
            raise HTTPException(status_code=500, detail="Error deleting Course.")
        return course


# Initialize CRUD instance for Course
crud_course = CRUDCourse(Course)
