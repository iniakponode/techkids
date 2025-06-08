from sqlalchemy.orm import Session
from backend.models.teacher_application import TeacherApplication
from backend.pydanticschemas.teacher_application import TeacherApplicationCreate

class CRUDTeacherApplication:
    def __init__(self, model):
        self.model = model

    def create(self, db: Session, obj_in: TeacherApplicationCreate) -> TeacherApplication:
        data = obj_in.model_dump()
        record = self.model(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

crud_teacher_application = CRUDTeacherApplication(TeacherApplication)
