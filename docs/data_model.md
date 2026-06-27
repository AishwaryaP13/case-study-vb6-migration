# SKS — Data Model and Relationships

Extracted from Phase 1. All FK constraints listed here are **enforced in `sks.db`**
(they did not exist in the original `Orders.db`). Dates are stored as `TEXT` (ISO 8601)
matching the VB6 original; no date-type migration was performed.

---

## Domain map

```
┌─────────────────────────────────────────────────────────────────────┐
│  AUTH          Levels ◄── Users                                     │
├─────────────────────────────────────────────────────────────────────┤
│  MASTER DATA   Categories ◄── Products ──► Providers                │
│                                  │                                  │
│                    ProductsByCustomer (M:N)  ProductsByProvider (M:N)│
│                         │                           │               │
│                      Customers               Providers              │
├─────────────────────────────────────────────────────────────────────┤
│  STOCK         Products ──► Stocks ──► ManualStocks                 │
│                Products ──► StockLog ◄── Stocks                     │
├─────────────────────────────────────────────────────────────────────┤
│  ORDERS        Customers ──► OrderRequests ──► OrderRequestDetails  │
│                                                       │             │
│                Providers ──► OrderReceptions ──► OrderReceptionDetails
│                                                       │             │
│                                              Products ┘             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tables

### Auth & access control

#### `Levels`
Lookup table for user roles. Only two values in seed data: `Administrator`, `Seller`.

| Column | Type | Constraints |
|---|---|---|
| `Level` | TEXT | **PK** (NOT NULL) |

#### `Users`
One row per system user. Passwords are stored as **bcrypt hashes** (the VB6 original
stored plaintext — this was fixed in Phase 1).

| Column | Type | Constraints |
|---|---|---|
| `Username` | TEXT | **PK** (NOT NULL) |
| `Password` | TEXT | bcrypt hash |
| `Fullname` | TEXT | |
| `Level` | TEXT | **FK → Levels.Level** |

---

### Master data

#### `Categories`
Simple product-category lookup. No hierarchy.

| Column | Type | Constraints |
|---|---|---|
| `CategoryID` | INTEGER | **PK** (autoincrement) |
| `CategoryName` | TEXT | |

#### `Providers`
Suppliers the business buys stock from. Seed data: 3 rows.

| Column | Type | Constraints |
|---|---|---|
| `ProviderID` | INTEGER | **PK** (autoincrement) |
| `ProviderName` | TEXT | |
| `ContactFirstName` / `ContactLastName` / `ContactTitle` | TEXT | |
| `Address`, `City`, `StateOrProvince`, `PostalCode` | TEXT | |
| `Country/Region` | TEXT | column name contains `/`; Python attr: `country_region` |
| `PhoneNumber`, `FaxNumber`, `Extension`, `EmailAddress` | TEXT | |
| `PaymentTerms` | TEXT | e.g. "Net 30" |
| `Notes` | TEXT | |

#### `Customers`
Buyers the business sells stock to. Seed data: 5 rows.

| Column | Type | Constraints |
|---|---|---|
| `CustomerID` | INTEGER | **PK** (autoincrement) |
| `CompanyName`, `CompanyOrDepartment` | TEXT | |
| `ContactFirstName` / `ContactLastName` / `ContactTitle` | TEXT | |
| `BillingAddress`, `City`, `StateOrProvince`, `PostalCode` | TEXT | |
| `Country/Region` | TEXT | same `/` naming quirk as Providers |
| `PhoneNumber`, `FaxNumber`, `Extension`, `EmailAddress` | TEXT | |
| `Notes` | TEXT | |

#### `Products`
The catalogue of items that can be bought or sold. Seed data: 4 rows.

| Column | Type | Constraints |
|---|---|---|
| `ProductID` | **TEXT** | **PK** (NOT NULL) — string PK, do not change |
| `ProductName`, `ProductDescription` | TEXT | |
| `SupplierID` | INTEGER | **FK → Providers.ProviderID** (nullable; all NULL in seed data) |
| `CategoryID` | INTEGER | **FK → Categories.CategoryID** |
| `UnitPrice` | FLOAT | catalogue price |
| `QuantityPerUnit` | FLOAT | |
| `Unit` | TEXT | e.g. "kg", "box" |
| `UnitsInStock` | INTEGER | denormalised — also tracked via `Stocks` |
| `UnitsOnOrder` | INTEGER | bumped when a sale order is created |
| `ReorderLevel` | INTEGER | |
| `Discontinued` | INTEGER | NOT NULL; 0 = active, 1 = discontinued |
| `LeadTime`, `SerialNumber` | TEXT | |

#### `ProductsByCustomer`
M:N junction — which products a customer is associated with.

| Column | Type | Constraints |
|---|---|---|
| `ID` | INTEGER | **PK** (autoincrement) |
| `CustomerID` | INTEGER | **FK → Customers.CustomerID** (NOT NULL) |
| `ProductID` | TEXT | **FK → Products.ProductID** (NOT NULL) |

#### `ProductsByProvider`
M:N junction — which products a provider supplies.

| Column | Type | Constraints |
|---|---|---|
| `ID` | INTEGER | **PK** (autoincrement) |
| `ProviderID` | INTEGER | **FK → Providers.ProviderID** (NOT NULL) |
| `ProductID` | TEXT | **FK → Products.ProductID** (NOT NULL) |

---

### Stock management

#### `Stocks`
Current on-hand stock position per product. One row per stock lot/entry; a product
can have multiple `Stocks` rows. Seed data: 50 rows.

| Column | Type | Constraints |
|---|---|---|
| `StockID` | INTEGER | **PK** (autoincrement) |
| `ProductID` | TEXT | **FK → Products.ProductID** |
| `Stock` | FLOAT | current quantity on hand |
| `InitialStock` | FLOAT | quantity when the lot was first entered |
| `UnitPrice` | FLOAT | selling price at time of entry |
| `StockPrice` | FLOAT | cost price at time of entry |
| `DateStarted`, `DateModified` | TEXT | ISO 8601 dates |
| `User` | TEXT | who created/last modified the row |

#### `ManualStocks`
Records each manual stock-in event (no purchase order involved). Every row
here also generates a `StockLog` entry. Seed data: 51 rows.

| Column | Type | Constraints |
|---|---|---|
| `ManualID` | INTEGER | **PK** (autoincrement) |
| `StockID` | INTEGER | **FK → Stocks.StockID** |
| `Action` | TEXT | e.g. `"IN"` |
| `Quantity`, `Price` | FLOAT | |
| `Date` | TEXT | |
| `User` | TEXT | |

#### `StockLog`
Audit trail of every stock movement regardless of source. Seed data: 52 rows.

| Column | Type | Constraints |
|---|---|---|
| `ID` | INTEGER | **PK** (autoincrement) |
| `StockID` | INTEGER | **FK → Stocks.StockID** |
| `ProductID` | TEXT | **FK → Products.ProductID** |
| `DocType` | TEXT | `"ManualStock"` or `"OrderReception"` — identifies the source document type |
| `DocID` | INTEGER | PK of the source document; **no FK** (polymorphic reference — two possible targets) |
| `Quantity`, `StockPrice` | FLOAT | |
| `Date`, `User` | TEXT | |

---

### Orders — Sales lifecycle

#### `OrderRequests`
Sales order header — one row per order to sell stock to a Customer.
Status values in seed data: `"Pending"`, `"Approved"`, `"Cancelled"`.
Seed data: 25 rows.

| Column | Type | Constraints |
|---|---|---|
| `OrderID` | INTEGER | **PK** (autoincrement) |
| `CustomerID` | INTEGER | **FK → Customers.CustomerID** |
| `Status` | TEXT | `Pending` / `Approved` / `Cancelled` |
| `OrderDate`, `RequiredByDate`, `PromisedByDate`, `ShipDate` | TEXT | |
| `ShipName`, `ShipAddress`, `ShipCity`, `ShipState` | TEXT | shipping destination fields |
| `ShipStateOrProvince`, `ShipPostalCode`, `ShipCountry`, `ShipPhoneNumber` | TEXT | |
| `ShippingMethodID` | INTEGER | no FK — lookup table not in scope |
| `FreightCharge`, `SalesTaxRate` | FLOAT | |
| `PurchaseOrderNumber`, `EmployeeID` | TEXT | |
| `Notes`, `ChangedBy`, `ChangedDate` | TEXT | |

#### `OrderRequestDetails`
Sales order line items — one row per product per order. Seed data: 25 rows.

| Column | Type | Constraints |
|---|---|---|
| `OrderDetailID` | INTEGER | **PK** (autoincrement) |
| `OrderID` | INTEGER | **FK → OrderRequests.OrderID** |
| `ProductID` | TEXT | **FK → Products.ProductID** |
| `Quantity` | FLOAT | |
| `UnitPrice` | FLOAT | price at time of order |
| `SalePrice` | FLOAT | negotiated sale price |
| `Discount` | FLOAT | fractional discount (e.g. 0.05 = 5%) |
| `SalesTax` | FLOAT | computed tax amount |
| `LineTotal` | FLOAT | computed: `(SalePrice * Quantity) - Discount + SalesTax` |
| `DateSold` | TEXT | |

---

### Orders — Purchase lifecycle

Structurally mirrors the sales lifecycle with `Providers` instead of `Customers`.

#### `OrderReceptions`
Purchase order header. Seed data: 19 rows.

| Column | Type | Constraints |
|---|---|---|
| `OrderID` | INTEGER | **PK** (autoincrement) |
| `ProviderID` | INTEGER | **FK → Providers.ProviderID** |
| `Status` | TEXT | `Pending` / `Approved` / `Cancelled` |
| `OrderDate`, `RequiredByDate`, `PromisedByDate` | TEXT | |
| `ReceivedBy` | TEXT | who accepted the delivery |
| `FreightCharge`, `SalesTaxRate` | FLOAT | |
| `PurchaseOrderNumber` | TEXT | |
| `Notes`, `ChangedBy`, `ChangedDate` | TEXT | |

#### `OrderReceptionDetails`
Purchase order line items. Seed data: 18 rows.

| Column | Type | Constraints |
|---|---|---|
| `OrderDetailID` | INTEGER | **PK** (autoincrement) |
| `OrderID` | INTEGER | **FK → OrderReceptions.OrderID** |
| `ProductID` | TEXT | **FK → Products.ProductID** |
| `Quantity`, `UnitPrice`, `SalePrice`, `Discount`, `SalesTax`, `LineTotal` | FLOAT | same shape as sales details |
| `DateSold` | TEXT | |

---

## FK graph (all enforced constraints)

```
Levels
  └─ Users.Level

Categories
  └─ Products.CategoryID

Providers
  ├─ Products.SupplierID
  ├─ OrderReceptions.ProviderID
  └─ ProductsByProvider.ProviderID

Customers
  ├─ OrderRequests.CustomerID
  └─ ProductsByCustomer.CustomerID

Products
  ├─ Stocks.ProductID
  ├─ StockLog.ProductID
  ├─ OrderRequestDetails.ProductID
  ├─ OrderReceptionDetails.ProductID
  ├─ ProductsByCustomer.ProductID
  └─ ProductsByProvider.ProductID

Stocks
  ├─ ManualStocks.StockID
  └─ StockLog.StockID

OrderRequests
  └─ OrderRequestDetails.OrderID

OrderReceptions
  └─ OrderReceptionDetails.OrderID
```

---

## What was dropped and why

| Table | Reason |
|---|---|
| `Invoices` | 0 rows; the VB6 menu item labelled "Create Invoice" actually opens the sales-order *approval* screen — it never writes to this table |
| `InvoiceDetails` | 0 rows; depends on `Invoices` which is out of scope |
| `Warehouses` | 0 rows; no VB6 form writes to it |

Add these back only if real invoicing or warehouse tracking is built as new functionality.

---

## Quirks to keep in mind when writing service code

1. **`Products.ProductID` is TEXT** — never cast it to int; downstream joins break.
2. **`Country/Region` column name** has a literal `/`. Python attribute is `country_region`; always use the ORM model, never raw SQL string with this column.
3. **`StockLog.DocID` has no FK** — it points at either `ManualStocks.ManualID` or `OrderReceptionDetails.OrderDetailID` depending on `DocType`. Resolve by checking `DocType` first.
4. **Dates are TEXT** — the VB6 app wrote them as locale-formatted strings. Seed data uses `M/D/YYYY` format. Parse with `datetime.strptime` before comparing; store as ISO 8601 going forward.
5. **`Products.UnitsOnOrder`** is bumped by the VB6 order-create form — it's a denormalised counter. The service layer must mirror this side-effect when creating `OrderRequestDetails`.
