from typing import Optional
from sqlalchemy import Integer, Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Category(Base):
    __tablename__ = "Categories"

    category_id: Mapped[int] = mapped_column("CategoryID", Integer, primary_key=True, autoincrement=True)
    category_name: Mapped[Optional[str]] = mapped_column("CategoryName", Text)


class Product(Base):
    __tablename__ = "Products"

    # ProductID is a TEXT primary key in the original — do not change
    product_id: Mapped[str] = mapped_column("ProductID", Text, primary_key=True)
    product_name: Mapped[Optional[str]] = mapped_column("ProductName", Text)
    product_description: Mapped[Optional[str]] = mapped_column("ProductDescription", Text)
    supplier_id: Mapped[Optional[int]] = mapped_column(
        "SupplierID", Integer, ForeignKey("Providers.ProviderID"), nullable=True
    )
    category_id: Mapped[Optional[int]] = mapped_column(
        "CategoryID", Integer, ForeignKey("Categories.CategoryID"), nullable=True
    )
    unit_price: Mapped[Optional[float]] = mapped_column("UnitPrice", Float)
    quantity_per_unit: Mapped[Optional[float]] = mapped_column("QuantityPerUnit", Float)
    unit: Mapped[Optional[str]] = mapped_column("Unit", Text)
    units_in_stock: Mapped[Optional[int]] = mapped_column("UnitsInStock", Integer)
    units_on_order: Mapped[Optional[int]] = mapped_column("UnitsOnOrder", Integer)
    reorder_level: Mapped[Optional[int]] = mapped_column("ReorderLevel", Integer)
    discontinued: Mapped[int] = mapped_column("Discontinued", Integer, nullable=False)
    lead_time: Mapped[Optional[str]] = mapped_column("LeadTime", Text)
    serial_number: Mapped[Optional[str]] = mapped_column("SerialNumber", Text)


class ProductsByCustomer(Base):
    __tablename__ = "ProductsByCustomer"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(
        "CustomerID", Integer, ForeignKey("Customers.CustomerID"), nullable=False
    )
    product_id: Mapped[str] = mapped_column(
        "ProductID", Text, ForeignKey("Products.ProductID"), nullable=False
    )


class ProductsByProvider(Base):
    __tablename__ = "ProductsByProvider"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True, autoincrement=True)
    provider_id: Mapped[int] = mapped_column(
        "ProviderID", Integer, ForeignKey("Providers.ProviderID"), nullable=False
    )
    product_id: Mapped[str] = mapped_column(
        "ProductID", Text, ForeignKey("Products.ProductID"), nullable=False
    )
