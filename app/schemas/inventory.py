from datetime import datetime
from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class CategoryOut(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class LocationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class LocationOut(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    serial_number: str | None = None
    status: str = Field(default="available", max_length=40)
    quantity: int = Field(default=1, ge=1)
    purchase_value: float | None = None
    category_id: int | None = None
    location_id: int | None = None


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    serial_number: str | None = None
    status: str | None = Field(default=None, max_length=40)
    quantity: int | None = Field(default=None, ge=1)
    purchase_value: float | None = None
    category_id: int | None = None
    location_id: int | None = None


class ItemOut(BaseModel):
    id: int
    name: str
    description: str | None
    serial_number: str | None
    status: str
    quantity: int
    purchase_value: float | None
    category_id: int | None
    location_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MovementCreate(BaseModel):
    to_location: str | None = None
    to_status: str | None = None
    notes: str | None = None


class MovementOut(BaseModel):
    id: int
    item_id: int
    from_location: str | None
    to_location: str | None
    from_status: str | None
    to_status: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
