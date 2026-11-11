"""Login API:  /api/auth/..."""
from flask import Blueprint, request, session

from backend.services import auth_service
from backend.utils.responses import error, success

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.get("/accounts")
def accounts():
    return success(auth_service.list_accounts())


@bp.post("/login")
def login():
    body = request.get_json(silent=True) or {}
    ok, code, extra = auth_service.verify_pin(body.get("account_id"), body.get("pin"))
    if not ok:
        return error(code, 401 if code != "INVALID_INPUT" else 400, **extra)
    session.clear()
    session["account_id"] = body["account_id"]
    return success(auth_service.get_account_summary(body["account_id"]))


@bp.get("/me")
def me():
    account_id = session.get("account_id")
    if account_id is None:
        return error("NOT_LOGGED_IN", 401)
    return success(auth_service.get_account_summary(account_id))


@bp.post("/logout")
def logout():
    session.clear()
    return success()