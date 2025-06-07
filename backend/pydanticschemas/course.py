from datetime import datetime
from pydantic import AnyHttpUrl, BaseModel, HttpUrl, Field
from typing import Optional
from uuid import UUID


# Base Schema for Shared Fields
class CourseBase(BaseModel):
    title: str = Field(..., max_length=255, description="Title of the course")
    image_url: Optional[str] = Field(None, description="Image URL of the course")
    description: str = Field(..., description="Detailed description of the course")
    price: float = Field(..., gt=0, description="Price of the course in USD")
    age_group: str = Field(..., max_length=50, description="Age group the course is designed for")
    duration: str = Field(..., max_length=100, description="Course duration (e.g., '6 weeks')")
    rating: Optional[float] = Field(0.0, ge=0.0, le=5.0, description="Course rating (0 to 5 stars)")

    def model_dump(self, **kwargs):
        """
        Override Pydantic model dump to convert HttpUrl to str.
        """
        data = super().model_dump(**kwargs)
        if isinstance(data.get("image_url"), AnyHttpUrl):
            data["image_url"] = str(data["image_url"])
        return data


# Schema for Creating a New Course
class CourseCreate(CourseBase):
    pass


# Schema for Updating a Course
class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255, description="Title of the course")
    image_url: Optional[str] = Field(None, description="Image URL of the course")
    description: Optional[str] = Field(None, description="Detailed description of the course")
    price: Optional[float] = Field(None, gt=0, description="Price of the course in USD")
    age_group: Optional[str] = Field(None, max_length=100, description="Age group the course is designed for")
    duration: Optional[str] = Field(None, max_length=100, description="Course duration (e.g., '6 weeks')")
    rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Course rating (0 to 5 stars)")
    # = Field(None, max_length=50, description="Age group the course is designed for")

    class Config:
        from_attributes=True
        json_encoders = {
            bytes: lambda b: b.hex() #This is the fix
        }

# Schema for Reading Course Data (Response Model)
class CourseSchema(CourseBase):
    id: int = Field(..., description="Unique ID of the course")
    created_at: datetime

    class Config:
        from_attributes = True  # This ensures compatibility with SQLAlchemy models
