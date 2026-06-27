# Spec 03 — Providers CRUD

**Source:** `frmProviders.frm`  
**Phase:** 2 — Backend service layer

---

## What the VB6 original did

Same ADODC data-binding pattern as `frmCustomers`, but with an explicit `Private Sub Save()`
that calls `TextBoxEmpty` on 11 fields before calling `dcProviders.Recordset.Update`. This is
the key difference from Customers — Providers has real required-field validation.

```vb
Private Sub Save()
    If TextBoxEmpty(txtField(0)) Then Exit Sub   ' ProviderName
    If TextBoxEmpty(txtField(1)) Then Exit Sub   ' PaymentTerms
    If TextBoxEmpty(txtField(2)) Then Exit Sub   ' EmailAddress
    If TextBoxEmpty(txtField(4)) Then Exit Sub   ' PostalCode
    If TextBoxEmpty(txtField(5)) Then Exit Sub   ' City
    If TextBoxEmpty(txtField(6)) Then Exit Sub   ' StateOrProvince
    If TextBoxEmpty(txtField(7)) Then Exit Sub   ' Country/Region  (checked twice — VB6 bug)
    If TextBoxEmpty(txtField(10)) Then Exit Sub  ' FaxNumber
    If TextBoxEmpty(txtField(11)) Then Exit Sub  ' ContactTitle
    If TextBoxEmpty(txtField(12)) Then Exit Sub  ' ContactFirstName
    If TextBoxEmpty(txtField(14)) Then Exit Sub  ' Notes
    dcProviders.Recordset.Update
End Sub
```

Note: `Address` is a column in the `Providers` table but is **not bound to any textbox**
in `frmProviders.frm` — the VB6 form never displayed or edited it.

---

## Service functions (`app/services/providers.py`)

| Function | Inputs | Returns |
|---|---|---|
| `list_providers(db, search)` | `Session`, `search: str \| None = None` | `list[ProviderOut]` |
| `get_provider(db, provider_id)` | `Session`, `int` | `ProviderOut \| None` |
| `create_provider(db, data)` | `Session`, `ProviderIn` | `ProviderOut` |
| `update_provider(db, provider_id, data)` | `Session`, `int`, `ProviderIn` | `ProviderOut \| None` |
| `delete_provider(db, provider_id)` | `Session`, `int` | `bool` |

## Pydantic schemas (`app/schemas/providers.py`)

```
ProviderIn  : provider_name, payment_terms, email_address, postal_code,
              city, state_or_province, country_region, fax_number,
              contact_title, contact_first_name, notes  — all str, required, non-empty

              phone_number, extension, contact_last_name  — Optional[str]
              address  — Optional[str]  (not on VB6 form but exists in DB)

ProviderOut : provider_id (int) + all ProviderIn fields
```

---

## Validation rules (from VB6 `frmProviders.Save()`)

| Field | Required | Source |
|---|---|---|
| `provider_name` | ✅ | txtField(0) |
| `payment_terms` | ✅ | txtField(1) |
| `email_address` | ✅ | txtField(2) |
| `postal_code` | ✅ | txtField(4) |
| `city` | ✅ | txtField(5) |
| `state_or_province` | ✅ | txtField(6) |
| `country_region` | ✅ | txtField(7) — checked twice in VB6 (bug), enforce once |
| `fax_number` | ✅ | txtField(10) |
| `contact_title` | ✅ | txtField(11) |
| `contact_first_name` | ✅ | txtField(12) |
| `notes` | ✅ | txtField(14) |
| `phone_number` | optional | txtField(8) — not checked |
| `extension` | optional | txtField(9) — not checked |
| `contact_last_name` | optional | txtField(13) — not checked |
| `address` | optional | not on form |

---

## Search behaviour

`list_providers(db, search="foo")` applies `WHERE ProviderName LIKE '%foo%'` (case-insensitive),
matching the `SearchCriteriaProviders` pattern in `modFunctions`.

---

## Acceptance criteria checklist

- [ ] `create_provider` rejects any of the 11 required fields being empty or missing
- [ ] `create_provider` accepts all optional fields as None
- [ ] `create_provider` returns `ProviderOut` with a generated `provider_id`
- [ ] `get_provider` returns `None` for unknown id
- [ ] `update_provider` persists all field changes
- [ ] `update_provider` returns `None` for unknown id
- [ ] `delete_provider` returns `True` and removes the row
- [ ] `delete_provider` returns `False` for unknown id
- [ ] `list_providers()` returns all 3 seeded providers
- [ ] `list_providers(search="...")` filters by provider_name (case-insensitive)

---

## Out of scope

- Streamlit page — Phase 3
- The `frmSearch` dialog shape — replaced by `search` parameter on `list_providers`
