from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.products import Category, Product
from app.schemas.products import CategoryOut, ProductIn, ProductOut


def _product_to_out(p: Product) -> ProductOut:
    return ProductOut(
        product_id=p.product_id,
        product_name=p.product_name,
        product_description=p.product_description,
        serial_number=p.serial_number,
        lead_time=p.lead_time,
        unit=p.unit,
        unit_price=p.unit_price,
        quantity_per_unit=p.quantity_per_unit,
        units_in_stock=p.units_in_stock,
        units_on_order=p.units_on_order,
        reorder_level=p.reorder_level,
        category_id=p.category_id,
        discontinued=p.discontinued,
    )


def list_categories(db: Session) -> list[CategoryOut]:
    rows = db.query(Category).order_by(Category.category_id).all()
    return [CategoryOut(category_id=r.category_id, category_name=r.category_name) for r in rows]


def list_products(
    db: Session,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
) -> list[ProductOut]:
    q = db.query(Product)
    if search and search.strip():
        q = q.filter(func.lower(Product.product_name).contains(search.strip().lower()))
    if category_id is not None:
        q = q.filter(Product.category_id == category_id)
    return [_product_to_out(p) for p in q.order_by(Product.product_id).all()]


def get_product(db: Session, product_id: str) -> Optional[ProductOut]:
    p = db.get(Product, product_id.strip().upper())
    return _product_to_out(p) if p else None


def create_product(db: Session, data: ProductIn) -> ProductOut:
    product = Product(
        product_id=data.product_id,
        product_name=data.product_name,
        product_description=data.product_description,
        serial_number=data.serial_number,
        lead_time=data.lead_time,
        unit=data.unit,
        unit_price=data.unit_price,
        quantity_per_unit=data.quantity_per_unit,
        units_in_stock=data.units_in_stock,
        units_on_order=data.units_on_order,
        reorder_level=data.reorder_level,
        category_id=data.category_id,
        discontinued=data.discontinued,
    )
    db.add(product)
    db.flush()
    return _product_to_out(product)


def update_product(db: Session, product_id: str, data: ProductIn) -> Optional[ProductOut]:
    product = db.get(Product, product_id.strip().upper())
    if product is None:
        return None
    product.product_name = data.product_name
    product.product_description = data.product_description
    product.serial_number = data.serial_number
    product.lead_time = data.lead_time
    product.unit = data.unit
    product.unit_price = data.unit_price
    product.quantity_per_unit = data.quantity_per_unit
    product.units_in_stock = data.units_in_stock
    product.units_on_order = data.units_on_order
    product.reorder_level = data.reorder_level
    product.category_id = data.category_id
    product.discontinued = data.discontinued
    db.flush()
    return _product_to_out(product)


def delete_product(db: Session, product_id: str) -> bool:
    product = db.get(Product, product_id.strip().upper())
    if product is None:
        return False
    db.delete(product)
    db.flush()
    return True
