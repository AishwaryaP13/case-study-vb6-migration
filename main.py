"""SKS Order Management — Streamlit entry point."""
import streamlit as st

from app.database import SessionLocal
from app.pages import login, customers, orders_create

st.set_page_config(page_title="SKS Order Management", layout="wide")


def get_db():
    if "db_session" not in st.session_state:
        st.session_state.db_session = SessionLocal()
    return st.session_state.db_session


db = get_db()

# Auth guard
if "current_user" not in st.session_state:
    login.render(db)
    st.stop()

# ── Authenticated shell ───────────────────────────────────────────────────────
user = st.session_state.current_user

with st.sidebar:
    st.title("SKS Seafood")
    st.caption(f"Logged in as **{user.username}**  ({user.level})")
    st.divider()
    page = st.radio(
        "Navigate",
        ["Customers", "Create Order"],
        label_visibility="collapsed",
    )
    st.divider()
    if st.button("Logout"):
        db.close()
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if page == "Customers":
    customers.render(db)
elif page == "Create Order":
    orders_create.render(db)
