from typing import Optional
from sqlalchemy import Integer, Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class OrderRequest(Base):
    """Sales order header — selling stock to a Customer."""

    __tablename__ = "OrderRequests"

    order_id: Mapped[int] = mapped_column("OrderID", Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[Optional[int]] = mapped_column(
        "CustomerID", Integer, ForeignKey("Customers.CustomerID"), nullable=True
    )
    status: Mapped[Optional[str]] = mapped_column("Status", Text)
    order_date: Mapped[Optional[str]] = mapped_column("OrderDate", Text)
    required_by_date: Mapped[Optional[str]] = mapped_column("RequiredByDate", Text)
    promised_by_date: Mapped[Optional[str]] = mapped_column("PromisedByDate", Text)
    ship_date: Mapped[Optional[str]] = mapped_column("ShipDate", Text)
    ship_name: Mapped[Optional[str]] = mapped_column("ShipName", Text)
    ship_address: Mapped[Optional[str]] = mapped_column("ShipAddress", Text)
    ship_city: Mapped[Optional[str]] = mapped_column("ShipCity", Text)
    ship_state: Mapped[Optional[str]] = mapped_column("ShipState", Text)
    ship_state_or_province: Mapped[Optional[str]] = mapped_column("ShipStateOrProvince", Text)
    ship_postal_code: Mapped[Optional[str]] = mapped_column("ShipPostalCode", Text)
    ship_country: Mapped[Optional[str]] = mapped_column("ShipCountry", Text)
    ship_phone_number: Mapped[Optional[str]] = mapped_column("ShipPhoneNumber", Text)
    shipping_method_id: Mapped[Optional[int]] = mapped_column("ShippingMethodID", Integer)
    freight_charge: Mapped[Optional[float]] = mapped_column("FreightCharge", Float)
    sales_tax_rate: Mapped[Optional[float]] = mapped_column("SalesTaxRate", Float)
    purchase_order_number: Mapped[Optional[str]] = mapped_column("PurchaseOrderNumber", Text)
    employee_id: Mapped[Optional[str]] = mapped_column("EmployeeID", Text)
    notes: Mapped[Optional[str]] = mapped_column("Notes", Text)
    changed_by: Mapped[Optional[str]] = mapped_column("ChangedBy", Text)
    changed_date: Mapped[Optional[str]] = mapped_column("ChangedDate", Text)


class OrderRequestDetail(Base):
    """Sales order line item."""

    __tablename__ = "OrderRequestDetails"

    order_detail_id: Mapped[int] = mapped_column("OrderDetailID", Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[Optional[int]] = mapped_column(
        "OrderID", Integer, ForeignKey("OrderRequests.OrderID"), nullable=True
    )
    product_id: Mapped[Optional[str]] = mapped_column(
        "ProductID", Text, ForeignKey("Products.ProductID"), nullable=True
    )
    quantity: Mapped[Optional[float]] = mapped_column("Quantity", Float)
    unit_price: Mapped[Optional[float]] = mapped_column("UnitPrice", Float)
    sale_price: Mapped[Optional[float]] = mapped_column("SalePrice", Float)
    discount: Mapped[Optional[float]] = mapped_column("Discount", Float)
    sales_tax: Mapped[Optional[float]] = mapped_column("SalesTax", Float)
    line_total: Mapped[Optional[float]] = mapped_column("LineTotal", Float)
    date_sold: Mapped[Optional[str]] = mapped_column("DateSold", Text)


class OrderReception(Base):
    """Purchase order header — buying stock from a Provider."""

    __tablename__ = "OrderReceptions"

    order_id: Mapped[int] = mapped_column("OrderID", Integer, primary_key=True, autoincrement=True)
    provider_id: Mapped[Optional[int]] = mapped_column(
        "ProviderID", Integer, ForeignKey("Providers.ProviderID"), nullable=True
    )
    status: Mapped[Optional[str]] = mapped_column("Status", Text)
    order_date: Mapped[Optional[str]] = mapped_column("OrderDate", Text)
    required_by_date: Mapped[Optional[str]] = mapped_column("RequiredByDate", Text)
    promised_by_date: Mapped[Optional[str]] = mapped_column("PromisedByDate", Text)
    received_by: Mapped[Optional[str]] = mapped_column("ReceivedBy", Text)
    freight_charge: Mapped[Optional[float]] = mapped_column("FreightCharge", Float)
    sales_tax_rate: Mapped[Optional[float]] = mapped_column("SalesTaxRate", Float)
    purchase_order_number: Mapped[Optional[str]] = mapped_column("PurchaseOrderNumber", Text)
    notes: Mapped[Optional[str]] = mapped_column("Notes", Text)
    changed_by: Mapped[Optional[str]] = mapped_column("ChangedBy", Text)
    changed_date: Mapped[Optional[str]] = mapped_column("ChangedDate", Text)


class OrderReceptionDetail(Base):
    """Purchase order line item."""

    __tablename__ = "OrderReceptionDetails"

    order_detail_id: Mapped[int] = mapped_column("OrderDetailID", Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[Optional[int]] = mapped_column(
        "OrderID", Integer, ForeignKey("OrderReceptions.OrderID"), nullable=True
    )
    product_id: Mapped[Optional[str]] = mapped_column(
        "ProductID", Text, ForeignKey("Products.ProductID"), nullable=True
    )
    quantity: Mapped[Optional[float]] = mapped_column("Quantity", Float)
    unit_price: Mapped[Optional[float]] = mapped_column("UnitPrice", Float)
    sale_price: Mapped[Optional[float]] = mapped_column("SalePrice", Float)
    discount: Mapped[Optional[float]] = mapped_column("Discount", Float)
    sales_tax: Mapped[Optional[float]] = mapped_column("SalesTax", Float)
    line_total: Mapped[Optional[float]] = mapped_column("LineTotal", Float)
    date_sold: Mapped[Optional[str]] = mapped_column("DateSold", Text)
