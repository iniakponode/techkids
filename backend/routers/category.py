from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.crud.category import crud_category
from backend.pydanticschemas.category import CategoryCreate, CategorySchema

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=list[CategorySchema])
def list_categories(db: Session = Depends(get_db)):
    return crud_category.get_all(db)

@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
def add_category(data: CategoryCreate, db: Session = Depends(get_db)):
    return crud_category.create(db, obj_in=data)
