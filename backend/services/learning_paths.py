"""Service helpers for managing course learning paths and learner progress."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Tuple

from sqlalchemy.orm import Session

from backend.models.course import Course
from backend.models.course_lesson import CourseLesson
from backend.models.course_module import CourseModule
from backend.models.learning_progress import LearningProgress
from backend.models.lesson_progress import LessonProgress
from backend.models.registration import Registration
from backend.pydanticschemas.learning_paths import (
    LearningPathProgress,
    LessonProgressStatus,
    LessonWithProgress,
    ModuleWithLessons,
)


LessonOrdering = List[Tuple[CourseModule, CourseLesson]]


def _ordered_lessons(course: Course | None) -> LessonOrdering:
    """Return an ordered list of ``(module, lesson)`` pairs for a course."""

    if course is None:
        return []

    ordered: LessonOrdering = []
    for module in sorted(course.modules, key=lambda mod: mod.position):
        for lesson in sorted(module.lessons, key=lambda les: les.position):
            ordered.append((module, lesson))
    return ordered


def ensure_registration_progress(
    db: Session, registration: Registration
) -> LearningProgress:
    """Guarantee that a ``LearningProgress`` row exists for ``registration``."""

    progress = registration.progress
    if not progress:
        progress = LearningProgress(registration_id=registration.id)
        db.add(progress)
        db.flush()
    return progress


def sync_registration_progress(
    db: Session,
    registration: Registration,
    *,
    update_timestamp: bool = False,
) -> tuple[LearningProgress, bool]:
    """Ensure lesson progress entries line up with the course structure."""

    progress = ensure_registration_progress(db, registration)
    ordered_lessons = _ordered_lessons(registration.course)
    lesson_ids = {lesson.id for _, lesson in ordered_lessons}

    existing_entries: Dict[int, LessonProgress] = {
        entry.lesson_id: entry for entry in list(progress.lesson_progress)
    }
    changed = False

    # Remove orphaned progress rows if lessons were deleted.
    for entry in list(progress.lesson_progress):
        if entry.lesson_id not in lesson_ids:
            progress.lesson_progress.remove(entry)
            db.delete(entry)
            existing_entries.pop(entry.lesson_id, None)
            changed = True

    # Create missing progress rows for newly added lessons.
    for _, lesson in ordered_lessons:
        if lesson.id not in existing_entries:
            new_entry = LessonProgress(
                progress_id=progress.id,
                lesson_id=lesson.id,
                status=LessonProgressStatus.NOT_STARTED.value,
            )
            db.add(new_entry)
            progress.lesson_progress.append(new_entry)
            existing_entries[lesson.id] = new_entry
            changed = True

    total_lessons = len(ordered_lessons)
    if progress.total_lessons != total_lessons:
        progress.total_lessons = total_lessons
        changed = True

    completed = sum(
        1
        for entry in existing_entries.values()
        if entry.status == LessonProgressStatus.COMPLETED.value
    )
    if progress.completed_lessons != completed:
        progress.completed_lessons = completed
        changed = True

    percentage = (completed / total_lessons * 100.0) if total_lessons else 0.0
    if abs(progress.completion_percentage - percentage) > 1e-6:
        progress.completion_percentage = percentage
        changed = True

    next_module = None
    next_lesson = None
    for module, lesson in ordered_lessons:
        entry = existing_entries.get(lesson.id)
        if not entry or entry.status != LessonProgressStatus.COMPLETED.value:
            next_module = module.title
            next_lesson = lesson.title
            break

    if next_module is None and ordered_lessons:
        last_module, last_lesson = ordered_lessons[-1]
        next_module = last_module.title
        next_lesson = last_lesson.title

    if progress.current_module != next_module:
        progress.current_module = next_module
        changed = True

    if progress.current_lesson != next_lesson:
        progress.current_lesson = next_lesson
        changed = True

    if update_timestamp:
        progress.last_activity_at = datetime.utcnow()
        changed = True

    return progress, changed


def sync_course_progress_records(db: Session, course_id: int) -> None:
    """Resynchronise progress entries for all registrations of ``course_id``."""

    registrations = (
        db.query(Registration)
        .filter(Registration.course_id == course_id)
        .all()
    )

    any_changes = False
    for registration in registrations:
        _, changed = sync_registration_progress(db, registration)
        any_changes = any_changes or changed

    if any_changes:
        db.commit()


def build_learning_path_progress(
    db: Session, registration: Registration
) -> LearningPathProgress:
    """Return a serialisable progress payload for ``registration``."""

    progress, changed = sync_registration_progress(db, registration)
    if changed:
        db.commit()
        db.refresh(progress)

    lesson_progress_map: Dict[int, LessonProgress] = {
        entry.lesson_id: entry for entry in progress.lesson_progress
    }

    modules_payload: List[ModuleWithLessons] = []
    course = registration.course
    modules = sorted(course.modules, key=lambda mod: mod.position) if course else []

    for module in modules:
        lessons_payload: List[LessonWithProgress] = []
        for lesson in sorted(module.lessons, key=lambda les: les.position):
            entry = lesson_progress_map.get(lesson.id)
            status_value = (
                entry.status if entry else LessonProgressStatus.NOT_STARTED.value
            )
            lessons_payload.append(
                LessonWithProgress(
                    id=lesson.id,
                    title=lesson.title,
                    content=lesson.content,
                    position=lesson.position,
                    duration_minutes=lesson.duration_minutes,
                    resource_url=lesson.resource_url,
                    status=LessonProgressStatus(status_value),
                    completed_at=entry.completed_at if entry else None,
                )
            )

        modules_payload.append(
            ModuleWithLessons(
                id=module.id,
                title=module.title,
                description=module.description,
                position=module.position,
                lessons=lessons_payload,
            )
        )

    return LearningPathProgress(
        registration_id=registration.id,
        course_id=registration.course_id,
        course_title=course.title if course else None,
        completion_percentage=progress.completion_percentage,
        completed_lessons=progress.completed_lessons,
        total_lessons=progress.total_lessons,
        current_module=progress.current_module,
        current_lesson=progress.current_lesson,
        last_activity_at=progress.last_activity_at,
        modules=modules_payload,
    )
