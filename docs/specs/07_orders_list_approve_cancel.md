# Spec 07 — Orders: List / Filter / Approve / Cancel

**Source:** `frmRequestAproval.frm`, `frmActionOrderRequest.frm` (sales),
`frmOrderAproval.frm`, `frmActionOrderReception.frm` (purchase)

---

## What the VB6 original did

`frmRequestAproval` / `frmOrderAproval`: filtered list of orders by date range and status,
double-click opens the single-order action screen.

`frmActionOrderRequest` / `frmActionOrderReception` approve/cancel logic:

```vb
' Approve
If UCase(txtStatus) = "APPROVED" Then Exit Sub   ' already approved — no-op
If UCase(txtStatus) = "CANCELLED" Then Exit Sub  ' cancelled — block
UPDATE OrderRequests SET Status = 'APPROVED', ChangedBy = userId, ChangedDate = Date
    WHERE OrderId = orderId

' Cancel
If UCase(txtStatus) = "CANCELLED" Then Exit Sub  ' already cancelled — no-op
If UCase(txtStatus) = "APPROVED" Then Exit Sub   ' approved — block
UPDATE OrderRequests SET Status = 'CANCELLED', ChangedBy = userId, ChangedDate = Date
    WHERE OrderId = orderId
```

Same logic mirrored for `OrderReceptions`.

---

## Service functions (extend `app/services/orders.py`)

| Function | Inputs | Returns |
|---|---|---|
| `list_orders(db, direction, status, date_from, date_to)` | `Session`, filters | `list[OrderOut]` |
| `get_order(db, order_id, direction)` | `Session`, `int`, `str` | `OrderOut \| None` |
| `approve_order(db, order_id, direction, changed_by)` | `Session`, `int`, `str`, `str` | `OrderOut` |
| `cancel_order(db, order_id, direction, changed_by)` | `Session`, `int`, `str`, `str` | `OrderOut` |

## Result schema additions (`app/schemas/orders.py`)

```
OrderOut gains: changed_by (str | None), changed_date (str | None)
```

---

## Status transition rules

| Current status | approve() | cancel() |
|---|---|---|
| REQUESTED / RECEIVED | → APPROVED ✅ | → CANCELLED ✅ |
| APPROVED | raise `OrderAlreadyApproved` | raise `OrderAlreadyApproved` |
| CANCELLED | raise `OrderAlreadyCancelled` | raise `OrderAlreadyCancelled` |

Errors are domain exceptions (not HTTP codes — the Streamlit layer decides how to display them).

---

## List / filter behaviour

`list_orders(db, direction="SALE", status="REQUESTED", date_from="2023-01-01", date_to="2023-12-31")`
→ filters on `OrderDate` (ISO string comparison), direction routes to the right table.
All filters are optional — omitting all returns every order for that direction.

---

## Acceptance criteria checklist

- [ ] `list_orders(direction="SALE")` returns all 25 seeded sale orders
- [ ] `list_orders(direction="PURCHASE")` returns all 19 seeded purchase orders
- [ ] `list_orders(status="APPROVED")` filters correctly
- [ ] `get_order` returns order with its lines
- [ ] `approve_order` on REQUESTED → status becomes APPROVED, changed_by set
- [ ] `approve_order` on already APPROVED raises `OrderAlreadyApproved`
- [ ] `approve_order` on CANCELLED raises `OrderAlreadyCancelled`
- [ ] `cancel_order` on REQUESTED → status becomes CANCELLED
- [ ] `cancel_order` on APPROVED raises `OrderAlreadyApproved`
- [ ] `cancel_order` on CANCELLED raises `OrderAlreadyCancelled`
- [ ] Same rules apply symmetrically for direction=PURCHASE (RECEIVED as initial status)

---

## Out of scope

- Streamlit list/approve screens — Phase 3
- No stock movement on approval — confirmed by reading `frmActionOrderRequest`: it only updates `Status`, no `Stocks` writes
