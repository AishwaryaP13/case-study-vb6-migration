from datetime import date
from typing import Literal, Optional
from sqlalchemy.orm import Session

from app.models.orders import (
    OrderRequest, OrderRequestDetail,
    OrderReception, OrderReceptionDetail,
)
from app.models.products import Product
from app.schemas.orders import OrderIn, OrderLineOut, OrderOut


class OrderAlreadyApproved(Exception):
    pass


class OrderAlreadyCancelled(Exception):
    pass


_TODAY = lambda: date.today().isoformat()  # noqa: E731


def _line_out_from_request(d: OrderRequestDetail) -> OrderLineOut:
    return OrderLineOut(
        order_detail_id=d.order_detail_id,
        product_id=d.product_id,
        quantity=d.quantity,
        unit_price=d.unit_price,
        sale_price=d.sale_price,
        discount=d.discount,
        sales_tax=d.sales_tax,
        line_total=d.line_total,
        date_sold=d.date_sold,
    )


def _line_out_from_reception(d: OrderReceptionDetail) -> OrderLineOut:
    return OrderLineOut(
        order_detail_id=d.order_detail_id,
        product_id=d.product_id,
        quantity=d.quantity,
        unit_price=d.unit_price,
        sale_price=d.sale_price,
        discount=d.discount,
        sales_tax=d.sales_tax,
        line_total=d.line_total,
        date_sold=d.date_sold,
    )


def _order_request_to_out(o: OrderRequest, lines: list[OrderLineOut]) -> OrderOut:
    return OrderOut(
        order_id=o.order_id,
        direction="SALE",
        partner_id=o.customer_id,
        status=o.status,
        order_date=o.order_date,
        required_by_date=o.required_by_date,
        promised_by_date=o.promised_by_date,
        freight_charge=o.freight_charge,
        sales_tax_rate=o.sales_tax_rate,
        notes=o.notes,
        changed_by=o.changed_by,
        changed_date=o.changed_date,
        lines=lines,
    )


def _order_reception_to_out(o: OrderReception, lines: list[OrderLineOut]) -> OrderOut:
    return OrderOut(
        order_id=o.order_id,
        direction="PURCHASE",
        partner_id=o.provider_id,
        status=o.status,
        order_date=o.order_date,
        required_by_date=o.required_by_date,
        promised_by_date=o.promised_by_date,
        freight_charge=o.freight_charge,
        sales_tax_rate=o.sales_tax_rate,
        notes=o.notes,
        changed_by=o.changed_by,
        changed_date=o.changed_date,
        lines=lines,
    )


def create_order(db: Session, data: OrderIn, created_by: str) -> OrderOut:
    today = _TODAY()

    if data.direction == "SALE":
        header = OrderRequest(
            customer_id=data.partner_id,
            status="REQUESTED",
            order_date=today,
            required_by_date=data.required_by_date,
            promised_by_date=data.promised_by_date,
            freight_charge=data.freight_charge,
            sales_tax_rate=data.sales_tax_rate,
            notes=data.notes,
            purchase_order_number=data.purchase_order_number,
            employee_id=created_by,
        )
        db.add(header)
        db.flush()

        line_outs = []
        for line in data.lines:
            line_total = round(line.quantity * line.sale_price, 2)
            detail = OrderRequestDetail(
                order_id=header.order_id,
                product_id=line.product_id,
                quantity=line.quantity,
                unit_price=line.unit_price,
                sale_price=line.sale_price,
                discount=line.discount,
                sales_tax=line.sales_tax,
                line_total=line_total,
                date_sold=today,
            )
            db.add(detail)
            db.flush()
            line_outs.append(_line_out_from_request(detail))

            # Side-effect: bump units_on_order for each line
            product = db.get(Product, line.product_id)
            if product is not None:
                product.units_on_order = (product.units_on_order or 0) + int(line.quantity)

        db.flush()
        return _order_request_to_out(header, line_outs)

    else:  # PURCHASE
        header = OrderReception(
            provider_id=data.partner_id,
            status="RECEIVED",
            order_date=today,
            required_by_date=data.required_by_date,
            promised_by_date=data.promised_by_date,
            freight_charge=data.freight_charge,
            sales_tax_rate=data.sales_tax_rate,
            notes=data.notes,
            purchase_order_number=data.purchase_order_number,
            received_by=created_by,
        )
        db.add(header)
        db.flush()

        line_outs = []
        for line in data.lines:
            line_total = round(line.quantity * line.sale_price, 2)
            detail = OrderReceptionDetail(
                order_id=header.order_id,
                product_id=line.product_id,
                quantity=line.quantity,
                unit_price=line.unit_price,
                sale_price=line.sale_price,
                discount=line.discount,
                sales_tax=line.sales_tax,
                line_total=line_total,
                date_sold=today,
            )
            db.add(detail)
            db.flush()
            line_outs.append(_line_out_from_reception(detail))
            # Purchase: units_on_order NOT updated (intentional — VB6 had this commented out)

        db.flush()
        return _order_reception_to_out(header, line_outs)


def get_order(db: Session, order_id: int, direction: str) -> Optional[OrderOut]:
    if direction == "SALE":
        o = db.get(OrderRequest, order_id)
        if o is None:
            return None
        lines = [_line_out_from_request(d) for d in
                 db.query(OrderRequestDetail).filter_by(order_id=order_id).all()]
        return _order_request_to_out(o, lines)
    else:
        o = db.get(OrderReception, order_id)
        if o is None:
            return None
        lines = [_line_out_from_reception(d) for d in
                 db.query(OrderReceptionDetail).filter_by(order_id=order_id).all()]
        return _order_reception_to_out(o, lines)


def list_orders(
    db: Session,
    direction: Literal["SALE", "PURCHASE"] = "SALE",
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> list[OrderOut]:
    if direction == "SALE":
        q = db.query(OrderRequest)
        if status:
            q = q.filter(OrderRequest.status == status.upper())
        if date_from:
            q = q.filter(OrderRequest.order_date >= date_from)
        if date_to:
            q = q.filter(OrderRequest.order_date <= date_to)
        return [_order_request_to_out(o, []) for o in q.order_by(OrderRequest.order_id).all()]
    else:
        q = db.query(OrderReception)
        if status:
            q = q.filter(OrderReception.status == status.upper())
        if date_from:
            q = q.filter(OrderReception.order_date >= date_from)
        if date_to:
            q = q.filter(OrderReception.order_date <= date_to)
        return [_order_reception_to_out(o, []) for o in q.order_by(OrderReception.order_id).all()]


def _check_transition(status: Optional[str], target: str) -> None:
    s = (status or "").upper()
    if s == "APPROVED":
        raise OrderAlreadyApproved(f"Order is already APPROVED")
    if s == "CANCELLED":
        raise OrderAlreadyCancelled(f"Order is already CANCELLED")


def approve_order(db: Session, order_id: int, direction: str, changed_by: str) -> OrderOut:
    if direction == "SALE":
        o = db.get(OrderRequest, order_id)
        _check_transition(o.status, "APPROVED")
        o.status = "APPROVED"
        o.changed_by = changed_by
        o.changed_date = _TODAY()
        db.flush()
        lines = [_line_out_from_request(d) for d in
                 db.query(OrderRequestDetail).filter_by(order_id=order_id).all()]
        return _order_request_to_out(o, lines)
    else:
        o = db.get(OrderReception, order_id)
        _check_transition(o.status, "APPROVED")
        o.status = "APPROVED"
        o.changed_by = changed_by
        o.changed_date = _TODAY()
        db.flush()
        lines = [_line_out_from_reception(d) for d in
                 db.query(OrderReceptionDetail).filter_by(order_id=order_id).all()]
        return _order_reception_to_out(o, lines)


def cancel_order(db: Session, order_id: int, direction: str, changed_by: str) -> OrderOut:
    if direction == "SALE":
        o = db.get(OrderRequest, order_id)
        _check_transition(o.status, "CANCELLED")
        o.status = "CANCELLED"
        o.changed_by = changed_by
        o.changed_date = _TODAY()
        db.flush()
        lines = [_line_out_from_request(d) for d in
                 db.query(OrderRequestDetail).filter_by(order_id=order_id).all()]
        return _order_request_to_out(o, lines)
    else:
        o = db.get(OrderReception, order_id)
        _check_transition(o.status, "CANCELLED")
        o.status = "CANCELLED"
        o.changed_by = changed_by
        o.changed_date = _TODAY()
        db.flush()
        lines = [_line_out_from_reception(d) for d in
                 db.query(OrderReceptionDetail).filter_by(order_id=order_id).all()]
        return _order_reception_to_out(o, lines)
