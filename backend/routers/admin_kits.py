import os
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.kit import Kit, KitSection, KitAsset
from backend.models.user import User
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/admin/kits", tags=["Admin Kits"])

UPLOAD_DIR = Path("frontend/static/uploads/kits")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _save_upload_file(upload_file) -> tuple[str, str | None, str | None]:
    file_extension = Path(upload_file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    file_url = f"/static/uploads/kits/{unique_filename}"
    file_type = file_extension.lstrip(".").lower() if file_extension else None
    return file_url, upload_file.filename, file_type


def _parse_int(value: str | None, default: int = 0) -> int:
    try:
        return int(value) if value is not None else default
    except ValueError:
        return default


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_kit(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    form = await request.form()
    title = form.get("title")
    description = form.get("description")
    price = form.get("price")
    status_value = form.get("status", "draft")

    if not title or not description or price is None:
        raise HTTPException(status_code=400, detail="Title, description, and price are required.")

    try:
        price_value = float(price)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid price value.") from exc

    thumbnail_url = None
    thumbnail_file = form.get("thumbnail_image")
    if thumbnail_file and getattr(thumbnail_file, "filename", None):
        thumbnail_url, _, _ = _save_upload_file(thumbnail_file)

    kit = Kit(
        title=title,
        description=description,
        price=price_value,
        status=status_value,
        thumbnail_url=thumbnail_url,
    )
    db.add(kit)
    db.flush()

    _build_sections_from_form(form, kit, db)

    db.commit()
    db.refresh(kit)
    return {"id": kit.id}


@router.put("/{kit_id}")
async def update_kit(
    kit_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    kit = db.query(Kit).filter(Kit.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")

    form = await request.form()
    title = form.get("title")
    description = form.get("description")
    price = form.get("price")
    status_value = form.get("status", kit.status)

    if not title or not description or price is None:
        raise HTTPException(status_code=400, detail="Title, description, and price are required.")

    try:
        price_value = float(price)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid price value.") from exc

    kit.title = title
    kit.description = description
    kit.price = price_value
    kit.status = status_value

    thumbnail_file = form.get("thumbnail_image")
    if thumbnail_file and getattr(thumbnail_file, "filename", None):
        thumbnail_url, _, _ = _save_upload_file(thumbnail_file)
        kit.thumbnail_url = thumbnail_url

    kit.sections.clear()
    db.flush()

    _build_sections_from_form(form, kit, db)

    db.commit()
    db.refresh(kit)
    return {"id": kit.id}


@router.delete("/{kit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kit(
    kit_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    kit = db.query(Kit).filter(Kit.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")

    db.delete(kit)
    db.commit()
    return None


def _build_sections_from_form(form, kit: Kit, db: Session) -> None:
    section_count = _parse_int(form.get("section_count"), 0)
    for i in range(section_count):
        section_name = form.get(f"section_{i}_name")
        if not section_name:
            continue
        section = KitSection(kit_id=kit.id, name=section_name, position=i)
        db.add(section)
        db.flush()

        asset_count = _parse_int(form.get(f"section_{i}_asset_count"), 0)
        for j in range(asset_count):
            upload_file = form.get(f"section_{i}_file_{j}")
            label = form.get(f"section_{i}_label_{j}")
            existing_url = form.get(f"section_{i}_existing_url_{j}")

            file_url = None
            file_name = None
            file_type = None

            if upload_file and getattr(upload_file, "filename", None):
                file_url, file_name, file_type = _save_upload_file(upload_file)
            elif existing_url:
                file_url = existing_url
                file_name = os.path.basename(existing_url)
                file_type = Path(file_name).suffix.lstrip(".").lower() if file_name else None

            if not file_url:
                continue

            asset = KitAsset(
                section_id=section.id,
                file_url=file_url,
                file_name=file_name,
                label=label,
                file_type=file_type,
            )
            db.add(asset)
