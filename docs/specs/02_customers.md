# Spec 02 — Customers CRUD

**Source:** `frmCustomers.frm`  
**Phase:** 2 — Backend service layer

---

## What the VB6 original did

`frmCustomers` used an `Adodc` control (`dcCustomers`) with `RecordSource = "Select * from Customers;"`.
All 15 textboxes were bound via `DataField`/`DataSource` — no explicit save/validate code; the
control handled it. The toolbar buttons mapped to: `AddNew`, `Update`, `Delete`, `CancelUpdate`,
`Requery` on the recordset.

Search triggered `modFunctions.SearchShow "Customers", "CompanyName", "customer"`, which called
`SearchCriteriaProducts` (misnamed in this form):
```vb
ExecuteSql "Select * from Customers where CompanyName LIKE '" & value & "%'"
```

No required-field validation existed anywhere in the form — all fields were nullable in the original
schema.

---

## Service functions (`app/services/customers.py`)

| Function | Inputs | Returns |
|---|---|---|
| `list_customers(db, search)` | `Session`, `search: str \| None = None` | `list[CustomerOut]` |
| `get_customer(db, customer_id)` | `Session`, `int` | `CustomerOut \| None` |
| `create_customer(db, data)` | `Session`, `CustomerIn` | `CustomerOut` |
| `update_customer(db, customer_id, data)` | `Session`, `int`, `CustomerIn` | `CustomerOut \| None` |
| `delete_customer(db, customer_id)` | `Session`, `int` | `bool` (False if not found) |

## Pydantic schemas (`app/schemas/customers.py`)

```
CustomerIn  : company_name (str, required, non-empty)
              company_or_department, contact_first_name, contact_last_name,
              contact_title, billing_address, city, state_or_province,
              postal_code, country_region, phone_number, fax_number,
              extension, email_address, notes  — all Optional[str]

CustomerOut : customer_id (int) + all CustomerIn fields
```

---

## Validation rules

| Rule | Source |
|---|---|
| `company_name` required, non-empty | Only field used for search/display in VB6; no other field was required |
| All other fields optional | VB6 had no ValidateTextBox calls anywhere in frmCustomers |

---

## Search behaviour

`list_customers(db, search="foo")` applies `WHERE CompanyName LIKE '%foo%'` (case-insensitive).
No search term → returns all customers ordered by `CustomerID`.

---

## Acceptance criteria checklist

- [ ] `create_customer` rejects empty `company_name`
- [ ] `create_customer` returns `CustomerOut` with a generated `customer_id`
- [ ] `get_customer` returns `None` for unknown id
- [ ] `get_customer` returns correct data for a known id
- [ ] `update_customer` persists changes; returns updated `CustomerOut`
- [ ] `update_customer` returns `None` for unknown id
- [ ] `delete_customer` returns `True` and removes the row
- [ ] `delete_customer` returns `False` for unknown id
- [ ] `list_customers()` returns all 5 seeded customers
- [ ] `list_customers(search="Spec")` filters by company_name (case-insensitive)

---

## Out of scope for this spec

- The Streamlit page (`app/pages/customers.py`) — Phase 3
- The `frmSearch` generic search dialog shape — replaced by the `search` parameter on `list_customers`
- `CurrentCustomerID` (set on form unload to pass to order forms) — handled in the order-create spec
