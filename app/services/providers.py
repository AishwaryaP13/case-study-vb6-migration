from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.providers import Provider
from app.schemas.providers import ProviderIn, ProviderOut


def _to_out(p: Provider) -> ProviderOut:
    return ProviderOut(
        provider_id=p.provider_id,
        provider_name=p.provider_name,
        payment_terms=p.payment_terms,
        email_address=p.email_address,
        postal_code=p.postal_code,
        city=p.city,
        state_or_province=p.state_or_province,
        country_region=p.country_region,
        fax_number=p.fax_number,
        contact_title=p.contact_title,
        contact_first_name=p.contact_first_name,
        notes=p.notes,
        phone_number=p.phone_number,
        extension=p.extension,
        contact_last_name=p.contact_last_name,
        address=p.address,
    )


def list_providers(db: Session, search: Optional[str] = None) -> list[ProviderOut]:
    q = db.query(Provider)
    if search and search.strip():
        q = q.filter(func.lower(Provider.provider_name).contains(search.strip().lower()))
    return [_to_out(p) for p in q.order_by(Provider.provider_id).all()]


def get_provider(db: Session, provider_id: int) -> Optional[ProviderOut]:
    p = db.get(Provider, provider_id)
    return _to_out(p) if p else None


def create_provider(db: Session, data: ProviderIn) -> ProviderOut:
    provider = Provider(
        provider_name=data.provider_name,
        payment_terms=data.payment_terms,
        email_address=data.email_address,
        postal_code=data.postal_code,
        city=data.city,
        state_or_province=data.state_or_province,
        country_region=data.country_region,
        fax_number=data.fax_number,
        contact_title=data.contact_title,
        contact_first_name=data.contact_first_name,
        notes=data.notes,
        phone_number=data.phone_number,
        extension=data.extension,
        contact_last_name=data.contact_last_name,
        address=data.address,
    )
    db.add(provider)
    db.flush()
    return _to_out(provider)


def update_provider(db: Session, provider_id: int, data: ProviderIn) -> Optional[ProviderOut]:
    provider = db.get(Provider, provider_id)
    if provider is None:
        return None
    provider.provider_name = data.provider_name
    provider.payment_terms = data.payment_terms
    provider.email_address = data.email_address
    provider.postal_code = data.postal_code
    provider.city = data.city
    provider.state_or_province = data.state_or_province
    provider.country_region = data.country_region
    provider.fax_number = data.fax_number
    provider.contact_title = data.contact_title
    provider.contact_first_name = data.contact_first_name
    provider.notes = data.notes
    provider.phone_number = data.phone_number
    provider.extension = data.extension
    provider.contact_last_name = data.contact_last_name
    provider.address = data.address
    db.flush()
    return _to_out(provider)


def delete_provider(db: Session, provider_id: int) -> bool:
    provider = db.get(Provider, provider_id)
    if provider is None:
        return False
    db.delete(provider)
    db.flush()
    return True
