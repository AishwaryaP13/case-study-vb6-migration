from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.customers import Customer
from app.schemas.customers import CustomerIn, CustomerOut


def _to_out(c: Customer) -> CustomerOut:
    return CustomerOut(
        customer_id=c.customer_id,
        company_name=c.company_name,
        company_or_department=c.company_or_department,
        contact_first_name=c.contact_first_name,
        contact_last_name=c.contact_last_name,
        contact_title=c.contact_title,
        billing_address=c.billing_address,
        city=c.city,
        state_or_province=c.state_or_province,
        postal_code=c.postal_code,
        country_region=c.country_region,
        phone_number=c.phone_number,
        fax_number=c.fax_number,
        extension=c.extension,
        email_address=c.email_address,
        notes=c.notes,
    )


def list_customers(db: Session, search: Optional[str] = None) -> list[CustomerOut]:
    q = db.query(Customer)
    if search and search.strip():
        q = q.filter(func.lower(Customer.company_name).contains(search.strip().lower()))
    return [_to_out(c) for c in q.order_by(Customer.customer_id).all()]


def get_customer(db: Session, customer_id: int) -> Optional[CustomerOut]:
    c = db.get(Customer, customer_id)
    return _to_out(c) if c else None


def create_customer(db: Session, data: CustomerIn) -> CustomerOut:
    customer = Customer(
        company_name=data.company_name,
        company_or_department=data.company_or_department,
        contact_first_name=data.contact_first_name,
        contact_last_name=data.contact_last_name,
        contact_title=data.contact_title,
        billing_address=data.billing_address,
        city=data.city,
        state_or_province=data.state_or_province,
        postal_code=data.postal_code,
        country_region=data.country_region,
        phone_number=data.phone_number,
        fax_number=data.fax_number,
        extension=data.extension,
        email_address=data.email_address,
        notes=data.notes,
    )
    db.add(customer)
    db.flush()
    return _to_out(customer)


def update_customer(db: Session, customer_id: int, data: CustomerIn) -> Optional[CustomerOut]:
    customer = db.get(Customer, customer_id)
    if customer is None:
        return None
    customer.company_name = data.company_name
    customer.company_or_department = data.company_or_department
    customer.contact_first_name = data.contact_first_name
    customer.contact_last_name = data.contact_last_name
    customer.contact_title = data.contact_title
    customer.billing_address = data.billing_address
    customer.city = data.city
    customer.state_or_province = data.state_or_province
    customer.postal_code = data.postal_code
    customer.country_region = data.country_region
    customer.phone_number = data.phone_number
    customer.fax_number = data.fax_number
    customer.extension = data.extension
    customer.email_address = data.email_address
    customer.notes = data.notes
    db.flush()
    return _to_out(customer)


def delete_customer(db: Session, customer_id: int) -> bool:
    customer = db.get(Customer, customer_id)
    if customer is None:
        return False
    db.delete(customer)
    db.flush()
    return True
