from typing import Optional
from pydantic import BaseModel, field_validator


_REQUIRED_FIELDS = (
    "provider_name", "payment_terms", "email_address", "postal_code",
    "city", "state_or_province", "country_region", "fax_number",
    "contact_title", "contact_first_name", "notes",
)


class ProviderIn(BaseModel):
    # Required per frmProviders.Save() validation
    provider_name: str
    payment_terms: str
    email_address: str
    postal_code: str
    city: str
    state_or_province: str
    country_region: str
    fax_number: str
    contact_title: str
    contact_first_name: str
    notes: str
    # Optional — not checked in VB6 Save() or not on the form
    phone_number: Optional[str] = None
    extension: Optional[str] = None
    contact_last_name: Optional[str] = None
    address: Optional[str] = None  # in DB but not on the VB6 form

    @field_validator(*_REQUIRED_FIELDS)
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v


class ProviderOut(BaseModel):
    provider_id: int
    provider_name: Optional[str]
    payment_terms: Optional[str]
    email_address: Optional[str]
    postal_code: Optional[str]
    city: Optional[str]
    state_or_province: Optional[str]
    country_region: Optional[str]
    fax_number: Optional[str]
    contact_title: Optional[str]
    contact_first_name: Optional[str]
    notes: Optional[str]
    phone_number: Optional[str]
    extension: Optional[str]
    contact_last_name: Optional[str]
    address: Optional[str]

    model_config = {"from_attributes": True}
