"""Login logic: list accounts, check the PIN, lock after 3 wrong tries."""
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash

from backend.db import get_db
from backend.utils.money import paise_to_display

MAX_ATTEMPTS = 3
LOCK_SECONDS = 60
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def mask_number(account_number):
    return "XXXX XXXX " + account_number[-4:]


def list_accounts():
    rows = get_db().execute(
        "SELECT id, holder_name, account_type, account_number "
        "FROM accounts WHERE is_active = 1 ORDER BY id"
    ).fetchall()
    return [
        {
            "id": r["id"],
            "holder_name": r["holder_name"],
            "account_type": r["account_type"],
            "masked_number": mask_number(r["account_number"]),
        }
        for r in rows
    ]


def get_account_summary(account_id):
    row = get_db().execute(
        "SELECT id, holder_name, account_type, account_number, balance_paise "
        "FROM accounts WHERE id = ?",
        (account_id,),
    ).fetchone()
    if row is None:
        return None
    return {
        "id": row["id"],
        "holder_name": row["holder_name"],
        "account_type": row["account_type"],
        "masked_number": mask_number(row["account_number"]),
        "balance_paise": row["balance_paise"],
        "balance_display": paise_to_display(row["balance_paise"]),
    }


def verify_pin(account_id, pin):
    """Returns (ok, code, extra). 'code' is a message code for the frontend."""
    if not isinstance(account_id, int) or not isinstance(pin, str):
        return False, "INVALID_INPUT", {}
    if len(pin) != 4 or not pin.isdigit():
        return False, "INVALID_INPUT", {}

    db = get_db()
    row = db.execute(
        "SELECT id, pin_hash, failed_attempts, locked_until FROM accounts "
        "WHERE id = ? AND is_active = 1",
        (account_id,),
    ).fetchone()
    if row is None:
        return False, "ACCOUNT_NOT_FOUND", {}

    now = datetime.now()
    if row["locked_until"]:
        unlock_time = datetime.strptime(row["locked_until"], TIME_FORMAT)
        if unlock_time > now:
            seconds_left = int((unlock_time - now).total_seconds()) + 1
            return False, "ACCOUNT_LOCKED", {"seconds_left": seconds_left}

    if check_password_hash(row["pin_hash"], pin):
        db.execute(
            "UPDATE accounts SET failed_attempts = 0, locked_until = NULL WHERE id = ?",
            (account_id,),
        )
        db.commit()
        return True, "LOGIN_OK", {}

    failed = row["failed_attempts"] + 1
    if failed >= MAX_ATTEMPTS:
        lock_until = (now + timedelta(seconds=LOCK_SECONDS)).strftime(TIME_FORMAT)
        db.execute(
            "UPDATE accounts SET failed_attempts = 0, locked_until = ? WHERE id = ?",
            (lock_until, account_id),
        )
        db.commit()
        return False, "ACCOUNT_LOCKED", {"seconds_left": LOCK_SECONDS}

    db.execute("UPDATE accounts SET failed_attempts = ? WHERE id = ?", (failed, account_id))
    db.commit()
    return False, "PIN_INCORRECT", {"attempts_left": MAX_ATTEMPTS - failed}