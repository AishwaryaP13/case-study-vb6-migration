# Spec 01 — Auth (login / current user)

**Source:** `frmLogin.frm` (intent only — the form is dead code, never invoked in VB6)  
**Phase:** 2 — Backend service layer  

---

## What the VB6 original did

```vb
ExecuteSql "SELECT * FROM Users WHERE username = '" & txtUserName.Text & "' and password = '" & txtPassword.Text & "'"
If rs.EOF Then
    MsgBox "Invalid 'Username' or 'Password', please try again!"
    Exit Sub
End If
UserFullname  = rs.Fields!Fullname
UserLevel     = rs.Fields!Level
CurrentUserAdmin = (UserLevel = "Administrator")
```

On success, three module-level globals were set: `UserFullname`, `UserLevel`,
`CurrentUserAdmin`. These were then read by every other form.

---

## Target design

No HTTP server — Streamlit calls the service layer directly. "Session" is
`st.session_state`. There is no JWT in this demo.

### Service functions (`app/services/auth.py`)

| Function | Inputs | Returns | Notes |
|---|---|---|---|
| `authenticate_user(db, username, password)` | `Session`, `str`, `str` | `UserOut \| None` | Looks up user by username, verifies bcrypt hash. Returns `None` on any failure (unknown user, wrong password). Never reveals which check failed. |
| `get_user(db, username)` | `Session`, `str` | `UserOut \| None` | Read-only lookup — used by the Streamlit session guard to rehydrate the current user. |
| `require_login()` | — | `UserOut` | Reads `st.session_state.current_user`; calls `st.stop()` + redirects to login page if absent. |

### Pydantic schemas (`app/schemas/auth.py`)

```
LoginInput  : username (str, required), password (str, required)
UserOut     : username (str), fullname (str | None), level (str), is_admin (bool)
```

`is_admin` is derived: `level == "Administrator"`.  
`password` is **never** included in `UserOut`.

### Session state contract

| Key | Type | Set by | Read by |
|---|---|---|---|
| `st.session_state.current_user` | `UserOut \| None` | login page on success, logout on clear | `require_login()`, every protected page |

---

## Validation rules (from VB6 form)

| Rule | Source |
|---|---|
| `username` required, non-empty | `txtUserName` has no `DataField` — must be entered by user |
| `password` required, non-empty | `txtPassword` has `PasswordChar = "*"` — masked, required |
| Both fields checked together; failure message is generic ("Invalid username or password") | VB6 `MsgBox` on `rs.EOF` |

---

## Acceptance criteria checklist

- [ ] `authenticate_user` returns `None` for unknown username
- [ ] `authenticate_user` returns `None` for wrong password (correct username)
- [ ] `authenticate_user` returns `UserOut` for correct username + bcrypt-hashed password
- [ ] `UserOut.is_admin` is `True` when `level == "Administrator"`, `False` otherwise
- [ ] `UserOut` never exposes the `password` field
- [ ] `get_user` returns `None` for non-existent username
- [ ] `get_user` returns correct `UserOut` for a user in the seeded Orders.db data
- [ ] `authenticate_user` with empty username or empty password returns `None` (does not crash)

---

## Out of scope for this spec

- The actual Streamlit login page (`app/pages/login.py`) — that is Phase 3
- JWT or any token-based auth — session state is sufficient for the Streamlit demo
- Password reset or account creation via the auth flow — user management is Feature 10
- Migrating the plaintext passwords in `Orders.db` — that is a one-time ops task, not part of the service layer
- Replicating the VB6 `LogStatus` call on login — the status bar pattern is replaced by Streamlit's own feedback mechanisms
