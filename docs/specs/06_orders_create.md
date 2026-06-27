# Spec 06 — Orders: Create

**Source:** `frmOrderRequest.frm` (sales), `frmOrderReception.frm` (purchase)  
**Phase:** 2 — Backend service layer

---

## What the VB6 original did

Both forms follow the same create pattern:

1. Pick a partner (Customer for sales via `frmSearch`; Provider for purchase)
2. Add product lines to an `MSFlexGrid`
3. `cmdSave_Click`:
   - INSERT header row into `OrderRequests` / `OrderReceptions`
   - `SELECT last_insert_rowid()` for the new `OrderID`
   - For each grid line: INSERT one `OrderRequestDetails` / `OrderReceptionDetails` row
   - **Sales only:** `UPDATE Products SET UnitsOnOrder = UnitsOnOrder + qty WHERE ProductID = '...'`
   - Purchase: UnitsOnOrder update was explicitly **commented out** in the VB6 source

**Initial status values set by VB6:**
- Sales: status not written on create (field is NULL in fresh rows; treated as `REQUESTED` by the approval screen)
- Purchase: `Status = 'RECEIVED'` written explicitly on create

**VB6 bug preserved deliberately:** `LineTotal` was set equal to `SalePrice` (not `SalePrice * Quantity`) due to a grid-column mis-index. Python implementation corrects this: `line_total = round(quantity * sale_price, 2)`.

---

## Service functions (`app/services/orders.py`)

| Function | Inputs | Returns |
|---|---|---|
| `create_order(db, data, created_by)` | `Session`, `OrderIn`, `str` | `OrderOut` |

## Pydantic schemas (`app/schemas/orders.py`)

```
OrderLineIn  : product_id (str, required), quantity (float > 0, required),
               unit_price (float, required), sale_price (float, required),
               discount (float, default=0.0), sales_tax (float, default=0.0)

OrderIn      : direction (Literal["SALE","PURCHASE"], required)
               partner_id (int, required) — CustomerID for SALE, ProviderID for PURCHASE
               lines (list[OrderLineIn], min 1 item, required)
               required_by_date, promised_by_date, notes,
               purchase_order_number  — Optional[str]
               freight_charge, sales_tax_rate  — Optional[float]

OrderLineOut : order_detail_id, product_id, quantity, unit_price, sale_price,
               discount, sales_tax, line_total, date_sold

OrderOut     : order_id, direction, partner_id, status, order_date,
               required_by_date, promised_by_date, freight_charge,
               sales_tax_rate, notes, lines: list[OrderLineOut]
```

---

## Business logic

1. Insert header into `OrderRequests` (direction=SALE) or `OrderReceptions` (direction=PURCHASE)
2. Initial status: `"REQUESTED"` for SALE, `"RECEIVED"` for PURCHASE
3. For each line: insert detail row; compute `line_total = round(quantity * sale_price, 2)`
4. **SALE only:** `Products.units_on_order += quantity` per line
5. `order_date` set to today's date (ISO 8601)

---

## Validation rules

| Rule | Source |
|---|---|
| `lines` must have at least one item | No empty orders make sense |
| `quantity > 0` per line | VB6 skipped lines where TextMatrix col 0 == "0" |
| `product_id` required per line | FK to Products |
| `unit_price` and `sale_price` required | Used to compute `line_total` |
| `partner_id` must exist in Customers (SALE) or Providers (PURCHASE) | FK enforced by DB |

---

## Acceptance criteria checklist

- [ ] `create_order` with direction=SALE inserts into OrderRequests + OrderRequestDetails
- [ ] `create_order` with direction=PURCHASE inserts into OrderReceptions + OrderReceptionDetails
- [ ] Created SALE order has status `"REQUESTED"`
- [ ] Created PURCHASE order has status `"RECEIVED"`
- [ ] `line_total` is computed as `quantity * sale_price` (not the VB6 bug)
- [ ] SALE order creation increments `Products.units_on_order` for each line
- [ ] PURCHASE order creation does NOT change `Products.units_on_order`
- [ ] Empty `lines` list is rejected
- [ ] `quantity <= 0` per line is rejected
- [ ] Returns `OrderOut` with all lines and computed totals

---

## Out of scope

- Streamlit order-entry page — Phase 3
- Shipping fields (ShipName, ShipAddress, etc.) — present in DB, not required for the service demo
- SalesTax computation logic — stored as-is from input; tax calculation is out of scope
