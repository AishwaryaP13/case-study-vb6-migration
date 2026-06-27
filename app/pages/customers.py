import streamlit as st
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.services.customers import (
    list_customers, get_customer, create_customer, update_customer, delete_customer,
)
from app.schemas.customers import CustomerIn


def render(db: Session) -> None:
    st.header("Customers")

    mode = st.session_state.get("cust_mode", "list")

    if mode == "list":
        _render_list(db)
    elif mode == "add":
        _render_form(db, customer_id=None)
    elif mode == "edit":
        _render_form(db, customer_id=st.session_state.get("cust_edit_id"))


def _render_list(db: Session) -> None:
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("Search by company name", key="cust_search")
    with col2:
        st.write("")
        st.write("")
        if st.button("+ New Customer", type="primary"):
            st.session_state.cust_mode = "add"
            st.rerun()

    customers = list_customers(db, search=search or None)

    if not customers:
        st.info("No customers found.")
        return

    for c in customers:
        col_name, col_city, col_phone, col_edit, col_del = st.columns([3, 2, 2, 1, 1])
        col_name.write(f"**{c.company_name}**")
        col_city.write(c.city or "—")
        col_phone.write(c.phone_number or "—")
        if col_edit.button("Edit", key=f"edit_{c.customer_id}"):
            st.session_state.cust_mode = "edit"
            st.session_state.cust_edit_id = c.customer_id
            st.rerun()
        if col_del.button("Del", key=f"del_{c.customer_id}"):
            delete_customer(db, c.customer_id)
            db.commit()
            st.success(f"Deleted {c.company_name}")
            st.rerun()


def _render_form(db: Session, customer_id: int | None) -> None:
    is_edit = customer_id is not None
    st.subheader("Edit Customer" if is_edit else "New Customer")

    existing = get_customer(db, customer_id) if is_edit else None

    def val(field: str) -> str:
        return getattr(existing, field, None) or ""

    with st.form("customer_form"):
        company_name = st.text_input("Company Name *", value=val("company_name"))
        company_or_dept = st.text_input("Department", value=val("company_or_department"))

        c1, c2, c3 = st.columns(3)
        contact_first = c1.text_input("First Name", value=val("contact_first_name"))
        contact_last = c2.text_input("Last Name", value=val("contact_last_name"))
        contact_title = c3.text_input("Title", value=val("contact_title"))

        billing_address = st.text_input("Billing Address", value=val("billing_address"))

        c4, c5, c6 = st.columns(3)
        city = c4.text_input("City", value=val("city"))
        state = c5.text_input("State/Province", value=val("state_or_province"))
        postal = c6.text_input("Postal Code", value=val("postal_code"))

        c7, c8 = st.columns(2)
        country = c7.text_input("Country/Region", value=val("country_region"))
        email = c8.text_input("Email", value=val("email_address"))

        c9, c10, c11 = st.columns(3)
        phone = c9.text_input("Phone", value=val("phone_number"))
        fax = c10.text_input("Fax", value=val("fax_number"))
        ext = c11.text_input("Extension", value=val("extension"))

        notes = st.text_area("Notes", value=val("notes"))

        save, cancel = st.columns(2)
        submitted = save.form_submit_button("Save", type="primary")
        cancelled = cancel.form_submit_button("Cancel")

    if cancelled:
        st.session_state.cust_mode = "list"
        st.rerun()

    if submitted:
        try:
            data = CustomerIn(
                company_name=company_name,
                company_or_department=company_or_dept or None,
                contact_first_name=contact_first or None,
                contact_last_name=contact_last or None,
                contact_title=contact_title or None,
                billing_address=billing_address or None,
                city=city or None,
                state_or_province=state or None,
                postal_code=postal or None,
                country_region=country or None,
                email_address=email or None,
                phone_number=phone or None,
                fax_number=fax or None,
                extension=ext or None,
                notes=notes or None,
            )
        except ValidationError as e:
            st.error(str(e))
            return

        if is_edit:
            update_customer(db, customer_id, data)
            msg = f"Updated {company_name}"
        else:
            create_customer(db, data)
            msg = f"Created {company_name}"

        db.commit()
        st.success(msg)
        st.session_state.cust_mode = "list"
        st.rerun()
