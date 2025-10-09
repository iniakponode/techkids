"""API endpoints for managing course learning paths and learner progress."""

from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.dependencies.auth_roles import require_role
from backend.models.course import Course
from backend.models.course_lesson import CourseLesson
from backend.models.course_module import CourseModule
from backend.models.family import FamilyLink
from backend.models.registration import Registration
from backend.models.user import User
from backend.pydanticschemas.learning_paths import (
    LearningPathProgress,
    LessonCreate,
    LessonProgressStatus,
    LessonProgressUpdate,
    LessonUpdate,
    LessonWithProgress,
    ModuleCreate,
    ModuleUpdate,
    ModuleWithLessons,
)
from backend.services.learning_paths import (
    build_learning_path_progress,
    ensure_registration_progress,
    sync_course_progress_records,
    sync_registration_progress,
)

router = APIRouter(prefix="/learning-paths", tags=["learning_paths"])


def _get_course_or_404(db: Session, course_id: int) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found.",
        )
    return course


def _serialize_module(module: CourseModule) -> ModuleWithLessons:
    lessons_payload: List[LessonWithProgress] = []
    for lesson in sorted(module.lessons, key=lambda les: les.position):
        lessons_payload.append(
            LessonWithProgress(
                id=lesson.id,
                title=lesson.title,
                content=lesson.content,
                position=lesson.position,
                duration_minutes=lesson.duration_minutes,
                resource_url=lesson.resource_url,
                status=LessonProgressStatus.NOT_STARTED,
                completed_at=None,
            )
        )

    return ModuleWithLessons(
        id=module.id,
        title=module.title,
        description=module.description,
        position=module.position,
        lessons=lessons_payload,
    )


def _get_registration_with_access(
    db: Session,
    registration_id: int,
    current_user: User,
) -> Registration:
    registration = db.query(Registration).filter(Registration.id == registration_id).first()
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found.",
        )

    if current_user.role == "admin" or registration.user_id == current_user.id:
        return registration

    if current_user.role == "parent":
        link_exists = (
            db.query(FamilyLink)
            .filter(
                FamilyLink.parent_id == current_user.id,
                FamilyLink.child_id == registration.user_id,
            )
            .first()
        )
        if link_exists:
            return registration

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have access to this registration.",
    )


@router.get(
    "/courses/{course_id}",
    response_model=List[ModuleWithLessons],
)
def get_course_learning_path(course_id: int, db: Session = Depends(get_db)) -> List[ModuleWithLessons]:
    """Return the published learning path for a course."""

    course = _get_course_or_404(db, course_id)
    modules = sorted(course.modules, key=lambda mod: mod.position)
    return [_serialize_module(module) for module in modules]


@router.post(
    "/courses/{course_id}/modules",
    response_model=ModuleWithLessons,
    status_code=status.HTTP_201_CREATED,
)
def create_module(
    course_id: int,
    payload: ModuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
) -> ModuleWithLessons:
    """Create a new module for the specified course."""

    course = _get_course_or_404(db, course_id)

    module = CourseModule(
        course_id=course.id,
        title=payload.title,
        description=payload.description,
        position=payload.position,
    )

    db.add(module)
    db.commit()
    db.refresh(module)

    sync_course_progress_records(db, course.id)
    db.refresh(course)

    return _serialize_module(module)


@router.patch(
    "/modules/{module_id}",
    response_model=ModuleWithLessons,
)
def update_module(
    module_id: int,
    payload: ModuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
) -> ModuleWithLessons:
    """Update the attributes of a course module."""

    module = db.query(CourseModule).filter(CourseModule.id == module_id).first()
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found.")

    if payload.title is not None:
        module.title = payload.title
    if payload.description is not None:
        module.description = payload.description
    if payload.position is not None:
        module.position = payload.position

    db.commit()
    db.refresh(module)

    sync_course_progress_records(db, module.course_id)

    return _serialize_module(module)


@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
) -> None:
    """Remove a module and its nested lessons."""

    module = db.query(CourseModule).filter(CourseModule.id == module_id).first()
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found.")

    course_id = module.course_id
    db.delete(module)
    db.commit()

    sync_course_progress_records(db, course_id)


@router.post(
    "/modules/{module_id}/lessons",
    response_model=LessonWithProgress,
    status_code=status.HTTP_201_CREATED,
)
def create_lesson(
    module_id: int,
    payload: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
) -> LessonWithProgress:
    """Create a new lesson within a module."""

    module = db.query(CourseModule).filter(CourseModule.id == module_id).first()
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found.")

    lesson = CourseLesson(
        module_id=module.id,
        title=payload.title,
        content=payload.content,
        position=payload.position,
        duration_minutes=payload.duration_minutes,
        resource_url=payload.resource_url,
    )

    db.add(lesson)
    db.commit()
    db.refresh(lesson)

    sync_course_progress_records(db, module.course_id)

    return LessonWithProgress(
        id=lesson.id,
        title=lesson.title,
        content=lesson.content,
        position=lesson.position,
        duration_minutes=lesson.duration_minutes,
        resource_url=lesson.resource_url,
        status=LessonProgressStatus.NOT_STARTED,
        completed_at=None,
    )


@router.patch(
    "/lessons/{lesson_id}",
    response_model=LessonWithProgress,
)
def update_lesson(
    lesson_id: int,
    payload: LessonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
) -> LessonWithProgress:
    """Update the attributes of a lesson."""

    lesson = db.query(CourseLesson).filter(CourseLesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found.")

    if payload.title is not None:
        lesson.title = payload.title
    if payload.content is not None:
        lesson.content = payload.content
    if payload.position is not None:
        lesson.position = payload.position
    if payload.duration_minutes is not None:
        lesson.duration_minutes = payload.duration_minutes
    if payload.resource_url is not None:
        lesson.resource_url = payload.resource_url

    db.commit()
    db.refresh(lesson)

    sync_course_progress_records(db, lesson.module.course_id)

    return LessonWithProgress(
        id=lesson.id,
        title=lesson.title,
        content=lesson.content,
        position=lesson.position,
        duration_minutes=lesson.duration_minutes,
        resource_url=lesson.resource_url,
        status=LessonProgressStatus.NOT_STARTED,
        completed_at=None,
    )


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
) -> None:
    """Delete a lesson."""

    lesson = db.query(CourseLesson).filter(CourseLesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found.")

    course_id = lesson.module.course_id
    db.delete(lesson)
    db.commit()

    sync_course_progress_records(db, course_id)


@router.get(
    "/registrations/{registration_id}/progress",
    response_model=LearningPathProgress,
)
def get_registration_progress(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["student", "child", "parent", "admin"])),
) -> LearningPathProgress:
    """Return the detailed learning path progress for a registration."""

    registration = _get_registration_with_access(db, registration_id, current_user)

    return build_learning_path_progress(db, registration)


@router.patch(
    "/registrations/{registration_id}/lessons/{lesson_id}",
    response_model=LearningPathProgress,
)
def update_lesson_progress_endpoint(
    registration_id: int,
    lesson_id: int,
    payload: LessonProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["student", "child", "parent", "admin"])),
) -> LearningPathProgress:
    """Update the completion status for a lesson and return the updated progress."""

    registration = _get_registration_with_access(db, registration_id, current_user)

    course = registration.course
    if not course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration is not associated with a course.",
        )

    lesson = (
        db.query(CourseLesson)
        .join(CourseModule)
        .filter(
            CourseLesson.id == lesson_id,
            CourseModule.course_id == course.id,
        )
        .first()
    )
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found for this course.")

    progress = ensure_registration_progress(db, registration)
    entry = next((lp for lp in progress.lesson_progress if lp.lesson_id == lesson.id), None)

    if entry is None:
        # Ensure the structures are up to date, then try again.
        progress, _ = sync_registration_progress(db, registration)
        entry = next((lp for lp in progress.lesson_progress if lp.lesson_id == lesson.id), None)

    if entry is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to prepare lesson progress entry.")

    new_status = payload.status.value
    status_changed = entry.status != new_status

    entry.status = new_status
    if new_status == LessonProgressStatus.COMPLETED.value:
        entry.completed_at = datetime.utcnow()
    elif status_changed:
        entry.completed_at = None

    sync_registration_progress(db, registration, update_timestamp=status_changed)
    db.commit()

    return build_learning_path_progress(db, registration)
