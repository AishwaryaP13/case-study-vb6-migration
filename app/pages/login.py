import streamlit as st
from sqlalchemy.orm import Session
from app.services.auth import authenticate_user


def render(db: Session) -> None:
    st.title("SKS Order Management")
    st.subheader("Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        if not username or not password:
            st.error("Username and password are required.")
            return
        user = authenticate_user(db, username, password)
        if user is None:
            st.error("Invalid username or password.")
        else:
            st.session_state.current_user = user
            st.rerun()
