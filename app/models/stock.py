from typing import Optional
from sqlalchemy import Integer, Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Stock(Base):
    __tablename__ = "Stocks"

    stock_id: Mapped[int] = mapped_column("StockID", Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[Optional[str]] = mapped_column(
        "ProductID", Text, ForeignKey("Products.ProductID"), nullable=True
    )
    stock: Mapped[Optional[float]] = mapped_column("Stock", Float)
    initial_stock: Mapped[Optional[float]] = mapped_column("InitialStock", Float)
    unit_price: Mapped[Optional[float]] = mapped_column("UnitPrice", Float)
    stock_price: Mapped[Optional[float]] = mapped_column("StockPrice", Float)
    date_started: Mapped[Optional[str]] = mapped_column("DateStarted", Text)
    date_modified: Mapped[Optional[str]] = mapped_column("DateModified", Text)
    user: Mapped[Optional[str]] = mapped_column("User", Text)


class ManualStock(Base):
    __tablename__ = "ManualStocks"

    manual_id: Mapped[int] = mapped_column("ManualID", Integer, primary_key=True, autoincrement=True)
    stock_id: Mapped[Optional[int]] = mapped_column(
        "StockID", Integer, ForeignKey("Stocks.StockID"), nullable=True
    )
    action: Mapped[Optional[str]] = mapped_column("Action", Text)
    quantity: Mapped[Optional[float]] = mapped_column("Quantity", Float)
    price: Mapped[Optional[float]] = mapped_column("Price", Float)
    date: Mapped[Optional[str]] = mapped_column("Date", Text)
    user: Mapped[Optional[str]] = mapped_column("User", Text)


class StockLog(Base):
    __tablename__ = "StockLog"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True, autoincrement=True)
    stock_id: Mapped[Optional[int]] = mapped_column(
        "StockID", Integer, ForeignKey("Stocks.StockID"), nullable=True
    )
    product_id: Mapped[Optional[str]] = mapped_column(
        "ProductID", Text, ForeignKey("Products.ProductID"), nullable=True
    )
    # DocType/DocID are a loose polymorphic reference — no FK constraint possible
    doc_type: Mapped[Optional[str]] = mapped_column("DocType", Text)
    doc_id: Mapped[Optional[int]] = mapped_column("DocID", Integer)
    quantity: Mapped[Optional[float]] = mapped_column("Quantity", Float)
    stock_price: Mapped[Optional[float]] = mapped_column("StockPrice", Float)
    date: Mapped[Optional[str]] = mapped_column("Date", Text)
    user: Mapped[Optional[str]] = mapped_column("User", Text)
