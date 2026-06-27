from typing import Optional
from pydantic import BaseModel, field_validator


class CustomerIn(BaseModel):
    company_name: str
    company_or_department: Optional[str] = None
    contact_first_name: Optional[str] = None
    contact_last_name: Optional[str] = None
    contact_title: Optional[str] = None
    billing_address: Optional[str] = None
    city: Optional[str] = None
    state_or_province: Optional[str] = None
    postal_code: Optional[str] = None
    country_region: Optional[str] = None
    phone_number: Optional[str] = None
    fax_number: Optional[str] = None
    extension: Optional[str] = None
    email_address: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("company_name")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("company_name must not be empty")
        return v


class CustomerOut(BaseModel):
    customer_id: int
    company_name: Optional[str]
    company_or_department: Optional[str]
    contact_first_name: Optional[str]
    contact_last_name: Optional[str]
    contact_title: Optional[str]
    billing_address: Optional[str]
    city: Optional[str]
    state_or_province: Optional[str]
    postal_code: Optional[str]
    country_region: Optional[str]
    phone_number: Optional[str]
    fax_number: Optional[str]
    extension: Optional[str]
    email_address: Optional[str]
    notes: Optional[str]

    model_config = {"from_attributes": True}
