from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.item import Item
from app.models.category import Category
from app.models.location import Location
from app.models.movement import Movement
from app.schemas.inventory import ItemCreate, ItemUpdate, ItemOut, MovementCreate, MovementOut

router = APIRouter(prefix="/api/items", tags=["items"])


def _get_owned_item(db: Session, item_id: int, user: User) -> Item:
    item = db.query(Item).filter(Item.id == item_id, Item.owner_id == user.id).first()
    if not item:
        raise HTTPException(404, "Item not found")
    return item


@router.get("", response_model=list[ItemOut])
def list_items(
    status: str | None = None,
    category_id: int | None = None,
    location_id: int | None = None,
    q: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Item).filter(Item.owner_id == user.id)
    if status:
        query = query.filter(Item.status == status)
    if category_id:
        query = query.filter(Item.category_id == category_id)
    if location_id:
        query = query.filter(Item.location_id == location_id)
    if q:
        query = query.filter(Item.name.ilike(f"%{q}%"))
    items = query.order_by(Item.updated_at.desc()).offset(offset).limit(limit).all()
    return items


@router.post("", response_model=ItemOut, status_code=201)
def create_item(payload: ItemCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.category_id:
        cat = db.query(Category).filter(Category.id == payload.category_id, Category.owner_id == user.id).first()
        if not cat:
            raise HTTPException(400, "Invalid category")
    if payload.location_id:
        loc = db.query(Location).filter(Location.id == payload.location_id, Location.owner_id == user.id).first()
        if not loc:
            raise HTTPException(400, "Invalid location")

    item = Item(
        owner_id=user.id,
        name=payload.name.strip(),
        description=payload.description,
        serial_number=payload.serial_number,
        status=payload.status,
        quantity=payload.quantity,
        purchase_value=payload.purchase_value,
        category_id=payload.category_id,
        location_id=payload.location_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _get_owned_item(db, item_id, user)


@router.patch("/{item_id}", response_model=ItemOut)
def update_item(
    item_id: int,
    payload: ItemUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = _get_owned_item(db, item_id, user)
    data = payload.model_dump(exclude_unset=True)

    if "category_id" in data and data["category_id"] is not None:
        cat = db.query(Category).filter(Category.id == data["category_id"], Category.owner_id == user.id).first()
        if not cat:
            raise HTTPException(400, "Invalid category")
    if "location_id" in data and data["location_id"] is not None:
        loc = db.query(Location).filter(Location.id == data["location_id"], Location.owner_id == user.id).first()
        if not loc:
            raise HTTPException(400, "Invalid location")

    old_status = item.status
    old_location_id = item.location_id

    for k, v in data.items():
        setattr(item, k, v)

    # Automatic movement record when status or location changes
    if ("status" in data and data["status"] != old_status) or ("location_id" in data and data["location_id"] != old_location_id):
        movement = Movement(
            item_id=item.id,
            user_id=user.id,
            from_status=old_status if "status" in data else None,
            to_status=data.get("status"),
            notes="Updated via PATCH /items/{id}",
        )
        db.add(movement)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = _get_owned_item(db, item_id, user)
    db.delete(item)
    db.commit()
    return None


@router.get("/{item_id}/movements", response_model=list[MovementOut])
def list_movements(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = _get_owned_item(db, item_id, user)
    return (
        db.query(Movement)
        .filter(Movement.item_id == item.id)
        .order_by(Movement.created_at.desc())
        .limit(100)
        .all()
    )


@router.post("/{item_id}/movements", response_model=MovementOut, status_code=201)
def create_movement(
    item_id: int,
    payload: MovementCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = _get_owned_item(db, item_id, user)
    movement = Movement(
        item_id=item.id,
        user_id=user.id,
        from_status=item.status,
        to_status=payload.to_status or item.status,
        to_location=payload.to_location,
        notes=payload.notes,
    )
    if payload.to_status:
        item.status = payload.to_status
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement
