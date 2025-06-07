from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
from backend.models.registration import Registration
from backend.pydanticschemas.registration import RegistrationCreate, RegistrationResponse
import logging

logger = logging.getLogger(__name__)


class CRUDRegistration:
    """
    CRUD operations for Registration.

    Methods:
    - **create**: Adds a new Registration record.
    - **get_by_id**: Retrieves a Registration by ID.
    - **get_all**: Retrieves all Registrations.
    - **update**: Updates a Registration record.
    - **delete**: Deletes a Registration record.
    """

    def __init__(self, model):
        self.model = model

    def create(self, db: Session, obj_in: RegistrationCreate) -> Registration:
        """
        Create a new Registration.
        """
        # Convert courseId to course_id to match model field name
        registration_data = obj_in.dict()
        if 'courseId' in registration_data:
            registration_data['course_id'] = registration_data.pop('courseId')
            
        new_registration = self.model(**registration_data)
        db.add(new_registration)
        try:
            db.commit()
            logger.info(f"Created Registration for {new_registration.fullName}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating Registration: {str(e)}")
            raise HTTPException(status_code=500, detail="Error creating Registration.")
        db.refresh(new_registration)
        return new_registration

    def get_by_id(self, db: Session, registration_id: int) -> Optional[Registration]:
        """
        Retrieve a Registration by ID.
        """
        registration = (
            db.query(self.model).filter(self.model.id == registration_id).first()
        )
        if not registration:
            logger.warning(f"Registration with ID {registration_id} not found.")
        return registration

    def get_all(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[Registration]:
        """
        Retrieve all Registrations.
        """
        registrations = db.query(self.model).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(registrations)} registrations.")
        return registrations

    def update(
        self, db: Session, registration_id: int, obj_in: RegistrationCreate
    ) -> Registration:
        """
        Update a Registration by ID.
        """
        registration = self.get_by_id(db, registration_id)
        if not registration:
            raise HTTPException(
                status_code=404,
                detail=f"Registration with ID {registration_id} not found.",
            )
        registration_data = obj_in.dict()
        if 'courseId' in registration_data:
            registration_data['course_id'] = registration_data.pop('courseId')
        
        for key, value in registration_data.items():
            setattr(registration, key, value)
        db.add(registration)
        try:
            db.commit()
            logger.info(f"Updated Registration with ID: {registration_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating Registration: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Error updating Registration."
            )
        db.refresh(registration)
        return registration

    def delete(self, db: Session, registration_id: int) -> Optional[Registration]:
        """
        Delete a Registration by ID.
        """
        registration = self.get_by_id(db, registration_id)
        if not registration:
            raise HTTPException(
                status_code=404,
                detail=f"Registration with ID {registration_id} not found.",
            )
        db.delete(registration)
        try:
            db.commit()
            logger.info(f"Deleted Registration with ID: {registration_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting Registration: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Error deleting Registration."
            )
        return registration


# Initialize CRUD instance for Registration
crud_registration = CRUDRegistration(Registration)
