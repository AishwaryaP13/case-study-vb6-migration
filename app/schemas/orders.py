from typing import Literal, Optional
from pydantic import BaseModel, field_validator, model_validator


class OrderLineIn(BaseModel):
    product_id: str
    quantity: float
    unit_price: float
    sale_price: float
    discount: float = 0.0
    sales_tax: float = 0.0

    @field_validator("product_id")
    @classmethod
    def product_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("product_id must not be empty")
        return v.strip().upper()

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("quantity must be greater than 0")
        return v


class OrderIn(BaseModel):
    direction: Literal["SALE", "PURCHASE"]
    partner_id: int
    lines: list[OrderLineIn]
    required_by_date: Optional[str] = None
    promised_by_date: Optional[str] = None
    freight_charge: Optional[float] = None
    sales_tax_rate: Optional[float] = None
    notes: Optional[str] = None
    purchase_order_number: Optional[str] = None

    @model_validator(mode="after")
    def at_least_one_line(self) -> "OrderIn":
        if not self.lines:
            raise ValueError("order must have at least one line")
        return self


class OrderLineOut(BaseModel):
    order_detail_id: int
    product_id: Optional[str]
    quantity: Optional[float]
    unit_price: Optional[float]
    sale_price: Optional[float]
    discount: Optional[float]
    sales_tax: Optional[float]
    line_total: Optional[float]
    date_sold: Optional[str]


class OrderOut(BaseModel):
    order_id: int
    direction: str
    partner_id: Optional[int]
    status: Optional[str]
    order_date: Optional[str]
    required_by_date: Optional[str]
    promised_by_date: Optional[str]
    freight_charge: Optional[float]
    sales_tax_rate: Optional[float]
    notes: Optional[str]
    changed_by: Optional[str]
    changed_date: Optional[str]
    lines: list[OrderLineOut] = []
