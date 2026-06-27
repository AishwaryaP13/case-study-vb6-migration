from typing import Optional
from pydantic import BaseModel, field_validator


class CategoryOut(BaseModel):
    category_id: int
    category_name: Optional[str]

    model_config = {"from_attributes": True}


class ProductIn(BaseModel):
    product_id: str
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    serial_number: Optional[str] = None
    lead_time: Optional[str] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    quantity_per_unit: Optional[float] = None
    units_in_stock: Optional[int] = None
    units_on_order: Optional[int] = None
    reorder_level: Optional[int] = None
    category_id: Optional[int] = None
    discontinued: int = 0

    @field_validator("product_id")
    @classmethod
    def validate_product_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("product_id must not be empty")
        return v.strip().upper()

    @field_validator("discontinued")
    @classmethod
    def validate_discontinued(cls, v: int) -> int:
        if v not in (0, 1):
            raise ValueError("discontinued must be 0 or 1")
        return v


class ProductOut(BaseModel):
    product_id: str
    product_name: Optional[str]
    product_description: Optional[str]
    serial_number: Optional[str]
    lead_time: Optional[str]
    unit: Optional[str]
    unit_price: Optional[float]
    quantity_per_unit: Optional[float]
    units_in_stock: Optional[int]
    units_on_order: Optional[int]
    reorder_level: Optional[int]
    category_id: Optional[int]
    discontinued: int

    model_config = {"from_attributes": True}
