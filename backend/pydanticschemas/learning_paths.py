"""Pydantic schemas for course learning paths and lesson progress."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class LessonProgressStatus(str, Enum):
    """Enumeration of supported lesson states."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ModuleCreate(BaseModel):
    """Payload for creating a course module."""

    title: str
    description: Optional[str] = None
    position: int = Field(0, ge=0)


class ModuleUpdate(BaseModel):
    """Payload for updating a course module."""

    title: Optional[str] = None
    description: Optional[str] = None
    position: Optional[int] = Field(None, ge=0)


class LessonCreate(BaseModel):
    """Payload for creating a lesson."""

    title: str
    content: Optional[str] = None
    position: int = Field(0, ge=0)
    duration_minutes: Optional[int] = Field(None, ge=0)
    resource_url: Optional[str] = None


class LessonUpdate(BaseModel):
    """Payload for updating a lesson."""

    title: Optional[str] = None
    content: Optional[str] = None
    position: Optional[int] = Field(None, ge=0)
    duration_minutes: Optional[int] = Field(None, ge=0)
    resource_url: Optional[str] = None


class LessonProgressUpdate(BaseModel):
    """Payload for updating an individual lesson's progress."""

    status: LessonProgressStatus


class LessonWithProgress(BaseModel):
    """Lesson representation enriched with completion details."""

    id: int
    title: str
    content: Optional[str]
    position: int
    duration_minutes: Optional[int]
    resource_url: Optional[str]
    status: LessonProgressStatus
    completed_at: Optional[datetime]

    class Config:
        orm_mode = True


class ModuleWithLessons(BaseModel):
    """Module representation with nested lesson progress."""

    id: int
    title: str
    description: Optional[str]
    position: int
    lessons: List[LessonWithProgress]

    class Config:
        orm_mode = True


class LearningPathProgress(BaseModel):
    """Full view of a learner's progress across a course."""

    registration_id: int
    course_id: Optional[int]
    course_title: Optional[str]
    completion_percentage: float
    completed_lessons: int
    total_lessons: int
    current_module: Optional[str]
    current_lesson: Optional[str]
    last_activity_at: Optional[datetime]
    modules: List[ModuleWithLessons]

    class Config:
        orm_mode = True
