from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.location import Location
from app.schemas.inventory import LocationCreate, LocationOut

router = APIRouter(prefix="/api/locations", tags=["locations"])


@router.get("", response_model=list[LocationOut])
def list_locations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Location).filter(Location.owner_id == user.id).order_by(Location.name).all()


@router.post("", response_model=LocationOut, status_code=201)
def create_location(payload: LocationCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    loc = Location(owner_id=user.id, name=payload.name.strip(), description=payload.description)
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


@router.get("/{location_id}", response_model=LocationOut)
def get_location(location_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    loc = db.query(Location).filter(Location.id == location_id, Location.owner_id == user.id).first()
    if not loc:
        raise HTTPException(404, "Location not found")
    return loc


@router.delete("/{location_id}", status_code=204)
def delete_location(location_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    loc = db.query(Location).filter(Location.id == location_id, Location.owner_id == user.id).first()
    if not loc:
        raise HTTPException(404, "Location not found")
    db.delete(loc)
    db.commit()
    return None
