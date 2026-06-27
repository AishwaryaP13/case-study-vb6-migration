import streamlit as st
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.services.orders import create_order
from app.services.customers import list_customers
from app.services.providers import list_providers
from app.schemas.orders import OrderIn, OrderLineIn
from app.models.products import Product


def render(db: Session) -> None:
    st.header("Create Order")

    direction = st.radio("Order Type", ["SALE", "PURCHASE"], horizontal=True)

    # Partner picker
    if direction == "SALE":
        customers = list_customers(db)
        if not customers:
            st.warning("No customers found. Add a customer first.")
            return
        partner_label = "Customer"
        options = {f"{c.company_name} (#{c.customer_id})": c.customer_id for c in customers}
    else:
        providers = list_providers(db)
        if not providers:
            st.warning("No providers found.")
            return
        partner_label = "Provider"
        options = {f"{p.provider_name} (#{p.provider_id})": p.provider_id for p in providers}

    selected_partner = st.selectbox(partner_label, list(options.keys()))
    partner_id = options[selected_partner]

    # Load all products for the line items
    products = db.query(Product).filter(Product.discontinued == 0).order_by(Product.product_name).all()
    if not products:
        st.warning("No active products in the database.")
        return
    product_map = {f"{p.product_name} ({p.product_id})": p for p in products}
    product_labels = list(product_map.keys())

    st.subheader("Line Items")
    st.caption("Add product lines below. At least one line is required.")

    # Number of lines
    num_lines = st.number_input("Number of lines", min_value=1, max_value=20, value=1, step=1)

    lines_data = []
    totals = []
    for i in range(int(num_lines)):
        st.markdown(f"**Line {i + 1}**")
        col_prod, col_qty, col_unit, col_sale, col_disc = st.columns([3, 1, 1, 1, 1])

        prod_label = col_prod.selectbox("Product", product_labels, key=f"prod_{i}")
        qty = col_qty.number_input("Qty", min_value=0.01, value=1.0, step=1.0, key=f"qty_{i}")
        unit_price = col_unit.number_input("Unit $", min_value=0.0, value=0.0, step=0.01, key=f"unit_{i}",
                                           format="%.2f")
        sale_price = col_sale.number_input("Sale $", min_value=0.0, value=0.0, step=0.01, key=f"sale_{i}",
                                           format="%.2f")
        discount = col_disc.number_input("Disc $", min_value=0.0, value=0.0, step=0.01, key=f"disc_{i}",
                                         format="%.2f")

        line_total = round(qty * sale_price, 2)
        totals.append(line_total)
        lines_data.append({
            "product_id": product_map[prod_label].product_id,
            "quantity": qty,
            "unit_price": unit_price,
            "sale_price": sale_price,
            "discount": discount,
        })

    # Totals summary
    grand_total = sum(totals)
    st.markdown(f"**Order Total: ${grand_total:,.2f}**")

    # Optional fields
    with st.expander("Additional Details (optional)"):
        notes = st.text_area("Notes", key="order_notes")
        freight = st.number_input("Freight Charge", min_value=0.0, value=0.0, step=0.01,
                                  key="freight", format="%.2f")

    st.divider()
    if st.button("Submit Order", type="primary"):
        current_user = st.session_state.get("current_user")
        created_by = current_user.username if current_user else "unknown"

        try:
            order_lines = [OrderLineIn(**ld) for ld in lines_data]
            order_in = OrderIn(
                direction=direction,
                partner_id=partner_id,
                lines=order_lines,
                notes=notes or None,
                freight_charge=freight if freight > 0 else None,
            )
        except ValidationError as e:
            st.error(f"Validation error: {e}")
            return

        try:
            result = create_order(db, order_in, created_by)
            db.commit()
            st.success(
                f"Order #{result.order_id} created — Status: **{result.status}** "
                f"| {len(result.lines)} line(s) | Total: ${grand_total:,.2f}"
            )
            st.balloons()
        except Exception as e:
            db.rollback()
            st.error(f"Failed to create order: {e}")
