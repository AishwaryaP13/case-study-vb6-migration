from typing import Optional
from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Provider(Base):
    __tablename__ = "Providers"

    provider_id: Mapped[int] = mapped_column("ProviderID", Integer, primary_key=True, autoincrement=True)
    provider_name: Mapped[Optional[str]] = mapped_column("ProviderName", Text)
    contact_first_name: Mapped[Optional[str]] = mapped_column("ContactFirstName", Text)
    contact_last_name: Mapped[Optional[str]] = mapped_column("ContactLastName", Text)
    contact_title: Mapped[Optional[str]] = mapped_column("ContactTitle", Text)
    address: Mapped[Optional[str]] = mapped_column("Address", Text)
    city: Mapped[Optional[str]] = mapped_column("City", Text)
    state_or_province: Mapped[Optional[str]] = mapped_column("StateOrProvince", Text)
    postal_code: Mapped[Optional[str]] = mapped_column("PostalCode", Text)
    country_region: Mapped[Optional[str]] = mapped_column("Country/Region", Text)
    phone_number: Mapped[Optional[str]] = mapped_column("PhoneNumber", Text)
    fax_number: Mapped[Optional[str]] = mapped_column("FaxNumber", Text)
    extension: Mapped[Optional[str]] = mapped_column("Extension", Text)
    email_address: Mapped[Optional[str]] = mapped_column("EmailAddress", Text)
    payment_terms: Mapped[Optional[str]] = mapped_column("PaymentTerms", Text)
    notes: Mapped[Optional[str]] = mapped_column("Notes", Text)
