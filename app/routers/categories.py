from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.category import Category
from app.schemas.inventory import CategoryCreate, CategoryOut

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Category).filter(Category.owner_id == user.id).order_by(Category.name).all()


@router.post("", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cat = Category(owner_id=user.id, name=payload.name.strip(), description=payload.description)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == category_id, Category.owner_id == user.id).first()
    if not cat:
        raise HTTPException(404, "Category not found")
    return cat


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == category_id, Category.owner_id == user.id).first()
    if not cat:
        raise HTTPException(404, "Category not found")
    db.delete(cat)
    db.commit()
    return None
