# Spec 04 — Products + Categories CRUD

**Source:** `frmProducts.frm`  
**Phase:** 2 — Backend service layer

---

## What the VB6 original did

Same ADODC pattern as Customers. `Save` calls `dcProducts.Recordset.Update` with **no explicit
required-field validation** — commented-out key handlers for numeric fields were never activated.

`CategoryID` is set via a dropdown (`cmbCategory`) populated by `LoadCombo "Categories"`.
`Discontinued` is a bound checkbox — stored as `0` / `1` integer, NOT NULL in the DB.
`ProductID` is a **user-entered TEXT primary key** (e.g. `"IK1"`, `"CRAB1"`) — not autoincrement.

---

## Service functions

### Categories (`app/services/products.py`)

| Function | Inputs | Returns |
|---|---|---|
| `list_categories(db)` | `Session` | `list[CategoryOut]` |

### Products (`app/services/products.py`)

| Function | Inputs | Returns |
|---|---|---|
| `list_products(db, search, category_id)` | `Session`, optional filters | `list[ProductOut]` |
| `get_product(db, product_id)` | `Session`, `str` | `ProductOut \| None` |
| `create_product(db, data)` | `Session`, `ProductIn` | `ProductOut` |
| `update_product(db, product_id, data)` | `Session`, `str`, `ProductIn` | `ProductOut \| None` |
| `delete_product(db, product_id)` | `Session`, `str` | `bool` |

## Pydantic schemas (`app/schemas/products.py`)

```
CategoryOut : category_id (int), category_name (str | None)

ProductIn   : product_id (str, required, non-empty, uppercased — VB6 key handler intent)
              product_name, product_description, serial_number,
              lead_time, unit  — Optional[str]
              unit_price, quantity_per_unit  — Optional[float]
              units_in_stock, units_on_order, reorder_level  — Optional[int]
              category_id  — Optional[int]
              discontinued (int, default=0) — 0=active, 1=discontinued (NOT NULL in DB)

ProductOut  : all ProductIn fields
```

---

## Validation rules

| Field | Rule | Source |
|---|---|---|
| `product_id` | Required, non-empty, stored uppercase | TEXT PK; VB6 commented key handler uppercased input |
| `discontinued` | Required, 0 or 1 | DB NOT NULL constraint |
| All other fields | Optional | No VB6 validation |

---

## Search behaviour

`list_products(db, search="foo")` → `WHERE ProductName LIKE '%foo%'` (case-insensitive).  
`list_products(db, category_id=3)` → `WHERE CategoryID = 3`.  
Both filters can be combined.

---

## Acceptance criteria checklist

- [ ] `create_product` rejects empty `product_id`
- [ ] `create_product` stores `product_id` uppercased
- [ ] `create_product` with the same `product_id` twice raises an integrity error
- [ ] `get_product` returns `None` for unknown id
- [ ] `update_product` cannot change `product_id` (PK is immutable)
- [ ] `update_product` returns `None` for unknown id
- [ ] `delete_product` returns `True` and removes the row
- [ ] `list_products()` returns all 4 seeded products
- [ ] `list_products(search="ikura")` finds `IK1` (case-insensitive)
- [ ] `list_products(category_id=2)` returns only products in that category
- [ ] `list_categories()` returns all 8 seeded categories

---

## Out of scope

- Streamlit page — Phase 3
- `UnitsInStock` / `UnitsOnOrder` updates — driven by the Orders service, not this CRUD
