"""Phase 2 — Feature 1: Auth service tests."""
import pytest
from app.services.auth import authenticate_user, get_user
from app.schemas.auth import LoginInput, UserOut


# ── authenticate_user ────────────────────────────────────────────────────────

def test_authenticate_valid_admin(auth_session):
    result = authenticate_user(auth_session, "testadmin", "adminpass")
    assert result is not None
    assert result.username == "testadmin"
    assert result.fullname == "Test Admin"
    assert result.level == "Administrator"
    assert result.is_admin is True


def test_authenticate_valid_seller(auth_session):
    result = authenticate_user(auth_session, "testseller", "sellerpass")
    assert result is not None
    assert result.is_admin is False
    assert result.level == "Seller"


def test_authenticate_wrong_password(auth_session):
    result = authenticate_user(auth_session, "testadmin", "wrongpassword")
    assert result is None


def test_authenticate_unknown_user(auth_session):
    result = authenticate_user(auth_session, "nobody", "whatever")
    assert result is None


def test_authenticate_empty_username(auth_session):
    assert authenticate_user(auth_session, "", "adminpass") is None


def test_authenticate_empty_password(auth_session):
    assert authenticate_user(auth_session, "testadmin", "") is None


def test_authenticate_whitespace_username(auth_session):
    assert authenticate_user(auth_session, "   ", "adminpass") is None


# ── UserOut never exposes password ────────────────────────────────────────────

def test_user_out_has_no_password_field(auth_session):
    result = authenticate_user(auth_session, "testadmin", "adminpass")
    assert result is not None
    assert isinstance(result, UserOut)
    assert not hasattr(result, "password")


# ── get_user ─────────────────────────────────────────────────────────────────

def test_get_user_known(auth_session):
    result = get_user(auth_session, "testadmin")
    assert result is not None
    assert result.username == "testadmin"


def test_get_user_unknown(auth_session):
    assert get_user(auth_session, "ghost") is None


def test_get_user_empty(auth_session):
    assert get_user(auth_session, "") is None


# ── Against real Orders.db seed data ─────────────────────────────────────────

def test_get_user_seeded_admin(seeded_session):
    """acantillo is a real Administrator in Orders.db seed data."""
    result = get_user(seeded_session, "acantillo")
    assert result is not None
    assert result.username == "acantillo"
    assert result.fullname == "Allan Cantillo"
    assert result.level == "Administrator"
    assert result.is_admin is True


def test_get_user_seeded_seller(seeded_session):
    result = get_user(seeded_session, "cbastos")
    assert result is not None
    assert result.is_admin is False
    assert result.level == "Seller"


def test_get_user_seeded_all_five(seeded_session):
    expected = {"acantillo", "mrojas", "cbastos", "jwelsh", "jbrown"}
    for username in expected:
        assert get_user(seeded_session, username) is not None


# ── LoginInput schema validation ─────────────────────────────────────────────

def test_login_input_rejects_empty_username():
    with pytest.raises(Exception):
        LoginInput(username="", password="secret")


def test_login_input_rejects_empty_password():
    with pytest.raises(Exception):
        LoginInput(username="user", password="")


def test_login_input_rejects_whitespace_username():
    with pytest.raises(Exception):
        LoginInput(username="   ", password="secret")
